import argparse
from collections import Counter
import logging
from logging import handlers
import json
import math
import signal
import sys
import time

from ipmanager import IPManager
from requestmanager import RequestManager

arg_parser = argparse.ArgumentParser(description="Rate unlimiter")
arg_parser.add_argument("url")
arg_parser.add_argument("-t", "--threads", dest="threads", type=int, default=1)
arg_parser.add_argument("--timeout", dest="timeout", type=int, default=20)
arg_parser.add_argument("--method", dest="method", default="GET")
arg_parser.add_argument("--rotateip", dest="rotateip", action="store_true")
arg_parser.add_argument("--cooldown", dest="cooldown", type=int, default=10)
arg_parser.add_argument("--debug", dest="debug", action="store_true")

args = arg_parser.parse_args()


def init_logging(debug=False):
    logger = logging.getLogger("rateunlimiter")
    logger.setLevel(logging.DEBUG)
    logformat = "%(asctime)s.%(msecs)03d %(name)s (%(process)d) %(levelname)s:%(message)s"
    log_formatter = logging.Formatter(fmt=logformat, datefmt='%Y-%m-%d %H:%M:%S')
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(log_formatter)
    stderr_handler.setLevel(logging.INFO)
    logger.addHandler(stderr_handler)
    if debug:
        file_handler = handlers.RotatingFileHandler("debug.log", maxBytes=2*1024*1024, backupCount=1, encoding="utf-8")
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    return logger


def sig_handler(signum, frame):  # pylint: disable=unused-argument
    logger.info("Exiting...")
    if iprotation:
        iprotation.clear()
    sys.exit()


def process_decay(delay):
    new_delay = delay - math.sqrt(delay)
    if new_delay <= 0:
        return 0
    else:
        return new_delay


def perform_requests(delay=0):
    logger.info(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)
    while True:
        c["total"] += 1
        logger.debug(f"Performing request {c['total']}")
        req = manager.request("GET", args.url)
        request_times.append(time.monotonic())
        logger.info(f"Received HTTP {req.status} response from server")
        req_rate = len(request_times) / (request_times[-1] - request_times[0]) * 60
        logger.info(f"Current request rate: {req_rate:.2f} r/min")
        if req.status != 429:
            c["success"] += 1
            fail_count = 0
            delay = process_decay(delay)
        else:
            fail_count += 1
            delay += 2**fail_count
        logger.info(f"Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)


if __name__ == "__main__":
    logger = init_logging(args.debug)
    logger.info("Initializing...")
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    logger.debug("Initialising connection pool...")
    INITIAL_DELAY = 5
    c = Counter()
    fail_count = 0
    request_times = []
    cooldown_duration = list(range(args.cooldown, 1, -2))
    if args.rotateip:
        try:
            with open("config.json") as c:
                config = json.load(c)
            iprotation = IPManager(config['aws_access_key'], config['aws_secret_key'], config['aws_region'])
            logger.debug("Creating API gateway...")
            iprotation.create(args.url)
        except FileNotFoundError:
            logger.critical("Config file not found and IP rotation enabled, quitting!")
            sys.exit(-1)
    else:
        iprotation = None
    manager = RequestManager(rotateip=iprotation, num_pools=1, maxsize=args.threads)
    c["total"] += 1
    logger.debug(f"Performing request {c['total']}")
    req = manager.request("GET", args.url)
    request_times.append(time.monotonic())
    if req.status == 429:
        raise RuntimeError("Already rate-limited")
    if req.status == 405:
        raise RuntimeError("Invalid method: Server returned HTTP 405")
    c["success"] += 1
    logger.info(f"Received HTTP {req.status} response from server")
    perform_requests(INITIAL_DELAY)
