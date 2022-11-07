#!/usr/bin/env python -u

"""
Usage:
    job_events_cannon [options]

Options:
    -h, --help                        Show this page
    -c=<count>, --count=<count>       Number of events to fire [default: 1000]
    -w=<workers>, --workers=<workers> Number of workers to use [default: 1]
    --debug                           Show debug logging
    --verbose                         Show verbose logging
    --websocket-address=<address>     Address of the websocket server [default: ws://localhost:8080/api/ws2]
    --job-id=<id>                     Job ID to send events for
    --stdout=<stdout>                 Stdout to send [default: test]
"""
from docopt import docopt
import asyncio
import logging
import sys
import websockets
import json
import uuid
import time
from multiprocessing import Pool

logger = logging.getLogger("job_events_cannon")


async def fire(websocket_address, c, job_id, stdout, worker_id):
    logger.info("Worker %s Firing %s events at %s", worker_id, c, websocket_address)
    event = json.dumps(
        {
            "type": "AnsibleEvent",
            "event": {"stdout": stdout, "job_id": job_id, "counter": 1, "type": "x"},
        }
    )
    print("Event: %s", event)
    async with websockets.connect(websocket_address) as websocket:
        for i in range(c):
            await websocket.send(event)


def worker(*args):
    asyncio.run(fire(*args[0]))


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
    websocket_address = parsed_args["--websocket-address"]
    job_id = parsed_args["--job-id"]
    if not job_id:
        job_id = str(uuid.uuid4())
    count = int(parsed_args["--count"])
    workers = int(parsed_args["--workers"])
    start = time.time()
    # print([(websocket_address, count, job_id, parsed_args["--stdout"], i) for i in range(workers)])
    # with Pool(workers) as p:
    #    p.map(worker, [(websocket_address, count, job_id, parsed_args["--stdout"], i) for i in range(workers)])
    # asyncio.run(fire(websocket_address, count, job_id, parsed_args['--stdout'], 0))
    # worker(websocket_address, count, job_id, parsed_args['--stdout'], 0)
    print(
        [
            (websocket_address, count, job_id, parsed_args["--stdout"], i)
            for i in range(workers)
        ]
    )
    with Pool(workers) as p:
        list(
            p.map(
                worker,
                list(
                    [
                        (websocket_address, count, job_id, parsed_args["--stdout"], i)
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
    main(sys.argv[1:])
