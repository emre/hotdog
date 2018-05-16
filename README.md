#### hotdog

A custom json indexer for STEEM blockchain.

#### Introduction

STEEM supports custom_json operations which allows you to post any type of JSON data into the blockchain. 

For example, things like following, reblog, mute are implemented on CustomJSON level. 3rd party decentralized app can make use of it. [Here](https://steemit.com/steem/@emrebeyler/broadcasting-custom-operations-into-steem-blockchain) is an example of the script where you can push your custom JSON into the network.

I want to implement a *decentralized* [pastebin service](https://steemit.com/steem/@emrebeyler/designing-a-pastebin-service-on-the-top-of-steem-blockchain) with the STEEM blockchain just for the fun. Since pasted content on Pastebins are generally junk, embedding them into the posts or comments are useless. These type of content shouldn't be rewarded.

CustomJson operation can save the day for this kind of needs. However, I cannot run lookups on custom_json's. So, I have needed an indexer backend where I need to filter the relevant data into my own MongoDB. You can have a look at my [early and hacky design post](https://steemit.com/steem/@emrebeyler/designing-a-pastebin-service-on-the-top-of-steem-blockchain).

<img src="https://steemitimages.com/DQmVdLcqKEs6S9dKCWb3RovF1ZD47KMAirqNbYhRVJqd3Ej/Screen%20Shot%202018-05-16%20at%201.03.05%20PM.png">

hotdog is that backend indexer where you can insert the relevant CustomJSON operations into your MongoDB instance constantly. Then, you can use MongoDB to use the data, run complex queries and represent in a traditional web app.


#### Installation

```
$ (sudo) pip install steem_hotdog
```

#### Configuration

Hotdog works with JSON files to handle configuration. An example configuration file is located at the repository.

```
{
  "nodes": ["https://api.steemit.com"],
  "mongo_uri": "localhost",
  "mongo_db_name": "custom_json",
  "blacklisted_posting_auths": ["bad_user"],
  "custom_json_ids": ["dlink", "dnews"],
  "custom_json_id_collection_map": {
    "dlink": "dlink",
    "dnews": "dnews",
  }
}
```

| Option                          | Description                                  |
|---------------------------------|----------------------------------------------|
| nodes                           | A list of nodes to connect                   |
| mongo\_uri                      | MongoDB connection string                    |
| mongo\_db\_name                 | Database name for the MongoDB                |
| blacklisted\_posting\_auths     | A blacklist to skip posting auths            |
| custom\_json\_ids               | A list of CustomJson ids to fetch            |
| custom\_json\_id_collection_map | Map of custom\_json\_id and Mongo collections|

#### Running

```
$ hotdog /path/to/config.json
```

**Setting a specific starting point**

```
$ hotdog /path/to/config.json --start-at block_height
```

**Setting a specific stop point**

```
$ hotdog /path/to/config.json --stop-at block_height
```

Or you can use both:

```
$ hotdog /path/to/config.json --start-at start_block --stop-at stop_block
```

#### Technology Stack
The bot runs on Python 3.6+. It may run on previous versions of py3k, but didn't tried it myself.

#### Roadmap

Indexer runs fine at the moment. 

I have been thinking to add a REST API interface via flask to expose the data. However, the *dynamic* nature of custom jsons makes this task complicated for querying. 

#### How to Contribute
Contribution process is same as any other open-source project. You can check out open issues at Github and can start working. Just make sure, you will comment on the related issue before starting working on it.
