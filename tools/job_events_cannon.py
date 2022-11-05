#!/usr/bin/env python -u

"""
Usage:
    job_events_cannon [options]

Options:
    -h, --help                       Show this page
    -c=<count>, --count=<count>      Number of events to fire [default: 1000]
    --debug                          Show debug logging
    --verbose                        Show verbose logging
    --websocket-address=<address>    Address of the websocket server [default: ws://localhost:8080/api/ws2]
    --job-id=<id>                    Job ID to send events for
"""
from docopt import docopt
import asyncio
import logging
import sys
import websockets
import json
import uuid

logger = logging.getLogger("job_events_cannon")


async def fire(websocket_address, c, job_id):
    logger.info("Firing %s events at %s", c, websocket_address)
    event = json.dumps(
        {
            "type": "AnsibleEvent",
            "event": {"stdout": "test", "job_id": job_id, "counter": 1, "type": "x"},
        }
    )
    print("Event: %s", event)
    async for websocket in websockets.connect(websocket_address):
        for i in range(c):
            await websocket.send(event)


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
    asyncio.run(fire(websocket_address, int(parsed_args['--count']), job_id))
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
