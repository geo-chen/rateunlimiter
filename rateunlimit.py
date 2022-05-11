import argparse
from collections import Counter
from datetime import datetime, timedelta
import logging
from logging import handlers
import json
import math
import os.path
import signal
import sys
import time
import urllib3
import uuid
import enlighten
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from requestmanager import RequestManager
from database import Base, RequestLog

arg_parser = argparse.ArgumentParser(description="Rate unlimiter")
arg_parser.add_argument("url")
arg_parser.add_argument("-t", "--threads", dest="threads", type=int, default=1)
arg_parser.add_argument("--timeout", dest="timeout", type=int, default=20)
arg_parser.add_argument("--method", dest="method", default="GET")
arg_parser.add_argument("--cooldown", dest="cooldown", type=int, default=10)
arg_parser.add_argument("--max-interval", dest="max_interval", type=int, default=5)
arg_parser.add_argument("--goal", dest="goal", type=int, default=5)
arg_parser.add_argument("--proxy-host", dest="proxy_host", default=None)
arg_parser.add_argument("--proxy-port", dest="proxy_port", type=int, default=8080)
arg_parser.add_argument("--debug", dest="debug", action="store_true")

args = arg_parser.parse_args()


def init_logging(debug=False):
    logger = logging.getLogger("rateunlimiter")
    logger.setLevel(logging.DEBUG)
    logformat = "%(asctime)s %(name)s %(levelname)s:%(message)s"
    log_formatter = logging.Formatter(fmt=logformat, datefmt='%Y-%m-%d %H:%M:%S')
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(log_formatter)
    if debug:
        stderr_handler.setLevel(logging.DEBUG)
    else:
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
    if args.debug:
        debug_output = {}
        debug_output['request_times'] = request_times
        debug_output['fail_times'] = fail_times
        with open("debug_requests.json", "w") as f:
            json.dump(debug_output, f)
    console_manager.stop()
    sys.exit()


def process_decay(delay, min_delay=1):
    new_delay = 60/((60/delay)+1)
    if new_delay < min_delay:
        return min_delay
    else:
        return new_delay


def sleep_update(duration):
    while duration > 0:
        status_rate.update()
        if duration >= 1.00:
            time.sleep(1)
        else:
            time.sleep(duration)
        duration -= 1


def count_requests(list_times, min_time=0, max_time=float("inf")):
    counts = [x[0] for x in list_times if (min_time <= x[0] <= max_time)]
    return len(counts)


def perform_requests(delay=0):
    global request_times, success_times
    min_delay = 0.5
    success_rate = 0
    first_fail = 0
    fail_count = 0
    success_count = 1
    fail_times = []
    unblock_times = []
    rate_guesses = {}
    was_blocked = False
    logger.info(f"Sleeping for {delay:.2f} seconds...")
    sleep_update(delay)
    while True:
        blocked = False
        c["total"] += 1
        if args.proxy_host:
            req = manager.request("GET", "http://ipinfo.io/ip")
            logger.info(f"Source IP: {req.data}")
        logger.debug(f"Performing request {c['total']}")
        try:
            new_request = RequestLog(session_id=session_id,
                                     timestamp=datetime.now(),
                                     url=f"{args.url}",
                                     status=0,
                                     blocked=blocked)
            req = manager.request("GET", f"{args.url}")
            request_times.append([time.monotonic()])
            logger.info(f"Received HTTP {req.status} response from server")
            new_request.status = req.status
        except urllib3.exceptions.ProtocolError:
            blocked = True
            new_request.blocked = True
            new_request.status = 999  # Placeholder value for error
        if req.status == 429 or req.status == 403:
            blocked = True
            new_request.blocked = True
        session.add(new_request)
        session.commit()
        req_rate = len(request_times) / (request_times[-1][0] - request_times[0][0]) * 60
        status_rate.update(cur_rate=f"{req_rate:.2f}")
        logger.debug(f"Current request rate: {req_rate:.2f} req/min")
        if blocked:
            was_blocked = True
            success_count = 0
            if fail_count == 0:  # First fail, set new limits
                success_times = []
                first_fail = time.monotonic()
                for test_interval in range(1, args.max_interval+1):
                    lower_bound = datetime.now() - timedelta(minutes=test_interval)
                    if (first_fail - request_times[0][0]) < test_interval*60:
                        # Session has not been running long enough, skip remaining time intervals
                        break
                    prev_requests = (session.query(RequestLog).filter(
                                    (RequestLog.timestamp >= lower_bound) &
                                    (RequestLog.session_id == session_id))
                                    .count()) - 1  # Minus one to exclude the latest blocked request (since it tripped the limit)
                    min_delay = 60*test_interval/prev_requests
                    logger.debug(f"New guess (DB): {prev_requests} req/{test_interval} min")
                    if test_interval == 1:
                        continue
                    if prev_requests/test_interval == (rate_guesses.get(test_interval-1, 0)) / (test_interval-1):
                        # Frequency is the same as for the previous interval, assume no new policy for this new interval
                        logger.debug(f"Calculated rate is equal to previous time interval, skipping guess for {test_interval} min interval")
                        continue
                    rate_guesses[test_interval] = prev_requests
            fail_count += 1
            fail_times.append([time.monotonic(), fail_count, 1])
            if len(unblock_times) < 1:
                elapsed_time = (fail_times[-1][0] - request_times[0][0])
            else:
                elapsed_time = (fail_times[-2][0] - fail_times[-1][0])
            elapsed_min = math.floor(elapsed_time / 60)
            logger.debug(f"Blocked, elapsed time: {elapsed_time} sec ({elapsed_time / 60} min)")
            guess_str = ""
            guess_last = 0
            guess_rm = []

            # Additional filtering for guesses
            for guess_interval, guess_count in rate_guesses.items():
                if guess_interval == 1:
                    guess_last = guess_interval
                    continue
                if abs(round((guess_count/guess_interval)) - round((rate_guesses.get(guess_last, 0))/guess_interval)) == 1:
                    guess_rm.append(guess_last)
            for rm in guess_rm:
                rate_guesses.pop(rm)

            # Write to status bar
            for guess_interval, guess_count in rate_guesses.items():
                guess_str += f" {guess_count} r/{guess_interval} min"
            status_guess.update(guess=guess_str)
            delay = 120*((args.goal/10)**fail_count)
        else:
            if was_blocked:
                was_blocked = False
                unblock_times.append(time.monotonic())
            c["success"] += 1
            success_count += 1
            success_times.append([time.monotonic(), success_count, 1])
            if len(success_times) > 1:
                success_rate = len(success_times) / (success_times[-1][0] - success_times[0][0]) * 60
                # logger.info(f"Current success rate: {success_rate:.2f} r/min")
            if fail_count > 0:  # Block expired, calculate previous penalty
                penalty_guess = time.monotonic() - first_fail
                fail_count = 0
                fail_times = []
                delay = (cooldown_duration[::-1])[min(len(cooldown_duration)-1, fail_count)]
                # logger.info(f"Block expired, current penalty duration guess: {penalty_guess:.0f} seconds")
            delay = process_decay(delay, min_delay)
        logger.info(f"Sleeping for {delay:.2f} seconds...")
        sleep_update(delay)


if __name__ == "__main__":
    console_manager = enlighten.get_manager()
    status_rate = console_manager.status_bar(status_format="Rate Unlimiter{fill}Current rate: {cur_rate} req/min{fill}{elapsed}",
                                             color="bright_white_on_lightslategray",
                                             justify=enlighten.Justify.CENTER,
                                             cur_rate="-")
    status_guess = console_manager.status_bar(status_format="Current guess:{guess}{fill}URL: {url}",
                                              guess="",
                                              url="",
                                              justify=enlighten.Justify.CENTER)
    logger = init_logging(args.debug)
    logger.info("Initializing...")
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    logger.debug("Initializing database...")
    engine = create_engine(f"sqlite:///requests.db")
    if not os.path.exists("requests.db"):
        Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    logger.debug("Initializing connection pool...")
    session_id = str(uuid.uuid4())
    INITIAL_DELAY = 15
    c = Counter()
    request_times = []
    success_times = []
    cooldown_duration = list(range(args.cooldown, 1, -2))
    manager = RequestManager(proxy_host=args.proxy_host, proxy_port=args.proxy_port, num_pools=1, maxsize=args.threads)
    c["total"] += 1
    if args.proxy_host:
        req = manager.request("GET", "http://ipinfo.io/ip")
        logger.info(f"Source IP: {req.data.decode()}")
    logger.debug(f"Performing request {c['total']}")
    new_request = RequestLog(session_id=session_id,
                             timestamp=datetime.now(),
                             url=args.url,
                             status=0,
                             blocked=False) 
    req = manager.request("GET", args.url)
    request_times.append([time.monotonic()])
    if req.status == 429:
        raise RuntimeError("Already rate-limited")
    if req.status == 405:
        raise RuntimeError("Invalid method: Server returned HTTP 405")
    new_request.status = req.status
    session.add(new_request)
    session.commit()
    c["success"] += 1
    success_times.append([time.monotonic(), 1, 1])
    logger.info(f"Received HTTP {req.status} response from server")
    status_guess.update(url=args.url)
    perform_requests(INITIAL_DELAY)
