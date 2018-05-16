import json
import argparse
import logging
import time
import datetime

from pymongo.mongo_client import MongoClient
from steem import Steem
import steembase

logger = logging.getLogger('Hotdog')
logger.setLevel(logging.INFO)
logging.basicConfig()


class Hotdog:

    def __init__(self, config):
        self.config = config
        self.mongo_connection = MongoClient(config.get("mongo_uri"))
        self.mongo_database = self.mongo_connection[config.get(
            "mongo_db_name")]
        self.steem = Steem(nodes=config.get("nodes"))

        # set block_interval property at class initialization.
        # This is the expected sleep time if the indexer keeps
        # up with the blocks.
        self.block_interval = self.get_block_interval()

    def get_last_block_height(self):
        # Return the last irreversible block height. Being a "irreversible"
        # block means that the transactions get their *finality*.
        try:
            props = self.steem.get_dynamic_global_properties()
            return props['last_irreversible_block_num']
        except (TypeError, steembase.exceptions.RPCError):
            # sometimes nodes return null to that call. so it's better to r
            # recursively retry it. However, this might cause infinite retries.
            return self.get_last_block_height()

    def get_block_interval(self):
        block_interval = self.steem.get_config()["STEEM_BLOCK_INTERVAL"]
        logger.info("Set block_interval to %s seconds." % block_interval)

        return block_interval

    def parse_block(self, block_height):
        logger.info("Parsing block: %s." % block_height)

        # get all operations in the related block id
        try:
            operation_data = self.steem.get_ops_in_block(
                block_height, virtual_only=False)
        except steembase.exceptions.RPCError:
            return self.parse_block(block_height)

        for operation in operation_data:
            self.handle_operation(
                operation['op'][0],
                operation['op'][1],
                block_height)

    def handle_operation(self, op_type, op_value, block_height):

        if op_type != "custom_json":
            # we're only interested in votes, skip.
            return
        try:
            action, action_data = json.loads(op_value["json"])
        except ValueError:
            logger.error("Malformed json. %s. Skipped." % op_value["json"])
            return

        if op_value.get("id") not in self.config.get("custom_json_ids"):
            return

        collection = self.mongo_database[
            self.config.get("custom_json_id_collection_map").get(
                op_value.get("id"))]

        if set(self.config.get("blacklisted_posting_auths", [])).intersection(
                set(op_value.get("required_posting_auths"))):
            logger.info("Skipped post since the posting auth is blacklisted.")
            return

        # merge operation data and custom_json data in one dictionary
        data = {
            "required_auths": op_value.get("required_auths"),
            "required_posting_auths": op_value.get("required_posting_auths"),
            "id": op_value.get("id"),
            "action": action,
            "block_height": block_height,
            "created_at": datetime.datetime.utcnow(),
        }
        data.update(action_data)

        logger.info("Inserting %s" % data)
        collection.insert_one(data)

    def start(self, start_at=None, stop_at=None):
        logger.info("Starting Hotdog")
        if start_at and not isinstance(start_at, int):
            start_at = int(start_at) - 1
        if stop_at and not isinstance(stop_at, int):
            stop_at = int(stop_at)

        current_block = start_at or self.get_last_block_height()

        while True:
            while ((stop_at or self.get_last_block_height()) - current_block) > 0:
                current_block += 1
                self.parse_block(current_block)

            if stop_at == current_block:
                logger.info("Stopped. Reached to the end.")
                return

            time.sleep(self.block_interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Config file in JSON format")
    parser.add_argument(
        "--start-at", help="Start listening at a specific block")
    parser.add_argument("--stop-at", help="Stop listening at a specific block")

    args = parser.parse_args()
    config = json.loads(
        open(args.config).read(),
    )
    hotdog = Hotdog(config)
    hotdog.start(start_at=args.start_at, stop_at=args.stop_at)


if __name__ == '__main__':
    main()
