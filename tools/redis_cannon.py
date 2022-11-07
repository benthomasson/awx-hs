#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
    redis_cannon [options]

Options:
    -h, --help                          Show this page
    -c=<count>, --count=<count>         Number of events to fire [default: 1000]
    -w=<workers>, --workers=<workers>   Number of workers to use [default: 1]
    --debug                             Show debug logging
    --verbose                           Show verbose logging
    --redis-url=<REDIS_URL>             Redis URL [default: redis://localhost:6379/0]
    --stdout=<stdout>                   Stdout to send [default: world]
"""

import asyncio
import redis
import json
from docopt import docopt
import logging
import sys
import time
from multiprocessing import Pool

logger = logging.getLogger("redis_cannon")


def fire(redis_url, c, job_id, stdout, worker_id):

    logger.info("Worker %s Firing %s events at %s", worker_id, c, redis_url)
    connection = redis.Redis.from_url(redis_url)
    event = json.dumps({"type": "hello", "msg": stdout})
    print("Event: %s", event)
    for i in range(c):
        connection.rpush("queue", event)


def worker(*args):
    fire(*args[0])


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = docopt(__doc__, args)
    if parsed_args["--debug"]:
        logging.basicConfig(level=logging.DEBUG)
    elif parsed_args["--verbose"]:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    count = int(parsed_args["--count"])
    workers = int(parsed_args["--workers"])
    start = time.time()
    with Pool(workers) as p:
        list(
            p.map(
                worker,
                list(
                    [
                        (
                            parsed_args["--redis-url"],
                            count,
                            1,
                            parsed_args["--stdout"],
                            i,
                        )
                        for i in range(workers)
                    ]
                ),
            )
        )
    end = time.time()
    print("Time: ", (end - start))
    print("Events per second: ", (count * workers) / (end - start))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
