#!/usr/bin/env python3
"""Collect status samples for field acceptance; these are not exposure-to-screen timings."""
import argparse
import json
import os
from pathlib import Path
import time
import urllib.request

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--server',default='http://127.0.0.1:8080')
parser.add_argument('--seconds',type=int,default=120)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
if args.output.exists():parser.error('Refusing to overwrite existing metrics')
args.output.parent.mkdir(parents=True,exist_ok=True)
headers={'Authorization':'Bearer '+os.environ.get('TRACR_TOKEN','')}
with args.output.open('x') as out:
    for _ in range(args.seconds):
        try:
            request=urllib.request.Request(args.server.rstrip('/')+'/api/status',headers=headers)
            with urllib.request.urlopen(request,timeout=.8) as response:
                sample=json.load(response)
        except OSError as exc:
            sample={'server_time':time.time(),'error':type(exc).__name__}
        out.write(json.dumps(sample)+'\n');out.flush();time.sleep(1)
