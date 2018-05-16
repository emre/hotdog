from setuptools import setup

setup(
    name='steem_hotdog',
    version='0.0.1',
    packages=["hotdog",],
    url='http://github.com/emre/hotdog',
    license='MIT',
    author='emre yilmaz',
    author_email='mail@emreyilmaz.me',
    description='A mongodb indexer for custom_json operations',
    entry_points={
        'console_scripts': [
            'hotdog = hotdog.indexer:main',
        ],
    },
    install_requires=["pymongo", "steem"]
)