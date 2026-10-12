"""Common payload preparation, correctness checks, and measurement output."""
import argparse
import base64
import csv
import json
import math
from pathlib import Path
import random
from time import perf_counter
from operations import image_dimensions

IMAGE = Path(__file__).with_name('Flatirons_Winter_Sunrise_edit_2.jpg')


def arguments(protocol, default_port):
    parser = argparse.ArgumentParser(description=f'{protocol} RPC benchmark')
    parser.add_argument('host')
    parser.add_argument('cmd', type=str.lower, choices=['add', 'rawimage', 'dotproduct', 'jsonimage'])
    parser.add_argument('reps', type=int)
    parser.add_argument('-p', '--port', type=int, default=default_port)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--timeout', type=float, default=30)
    parser.add_argument('--warmup', type=int, default=5)
    parser.add_argument('--seed', type=int, default=6)
    parser.add_argument('--image', type=Path, default=IMAGE)
    parser.add_argument('--csv', type=Path, help='Append measurements to this CSV')
    parser.add_argument('--scenario', default='unspecified')
    args = parser.parse_args()
    if args.reps <= 0 or args.warmup < 0 or args.timeout <= 0:
        parser.error('reps and timeout must be positive; warmup must be nonnegative')
    return args


def payload(args):
    if args.cmd == 'add':
        return {'a': 5, 'b': 10}, {'sum': 15}
    if args.cmd == 'dotproduct':
        random.seed(args.seed)
        a = [random.random() for _ in range(100)]
        b = [random.random() for _ in range(100)]
        return {'a': a, 'b': b}, {'dotproduct': sum(x*y for x, y in zip(a, b))}
    data = args.image.read_bytes()
    expected = image_dimensions(data)
    return (data if args.cmd == 'rawimage' else
            {'image': base64.b64encode(data).decode('ascii')}), expected


def verify(actual, expected):
    if expected.keys() != actual.keys():
        raise RuntimeError(f'unexpected response: {actual}')
    for key, value in expected.items():
        if not math.isclose(actual[key], value, rel_tol=1e-9, abs_tol=1e-9):
            raise RuntimeError(f'incorrect response: {actual}; expected {expected}')


def measure(args, protocol, call, expected, request_bytes):
    for _ in range(args.warmup):
        verify(call(), expected)
    start = perf_counter()
    results = [call() for _ in range(args.reps)]
    elapsed = perf_counter() - start
    for result in results:
        verify(result, expected)
    if args.debug:
        print(json.dumps(results[-1]))
    row = dict(protocol=protocol, method=args.cmd, scenario=args.scenario,
               host=args.host, port=args.port, reps=args.reps, warmup=args.warmup,
               ms_per_operation=elapsed * 1000 / args.reps,
               request_payload_bytes=request_bytes)
    print(json.dumps(row))
    if args.csv:
        exists = args.csv.exists() and args.csv.stat().st_size > 0
        with args.csv.open('a', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=row.keys())
            if not exists:
                writer.writeheader()
            writer.writerow(row)
