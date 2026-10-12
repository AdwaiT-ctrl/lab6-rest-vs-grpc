#!/usr/bin/env python3
"""Run all eight benchmark cases from the client VM."""
import argparse
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('host', help='localhost or server internal IP')
parser.add_argument('scenario', choices=['local', 'same-zone', 'different-region'])
parser.add_argument('--reps', type=int)
parser.add_argument('--csv', type=Path)
args = parser.parse_args()
reps = args.reps if args.reps is not None else (100 if args.scenario == 'different-region' else 1000)
if reps <= 0:
    parser.error('reps must be positive')
root = Path(__file__).resolve().parent
output = (args.csv or root / 'measurements' / (args.scenario + '.csv')).resolve()
output.parent.mkdir(parents=True, exist_ok=True)
for protocol in ['rest', 'grpc']:
    for method in ['add', 'rawimage', 'dotproduct', 'jsonimage']:
        subprocess.run([sys.executable, str(root / (protocol + '-client.py')),
                        args.host, method, str(reps), '--scenario', args.scenario,
                        '--csv', str(output)], check=True)
print('Saved measurements to', output)
