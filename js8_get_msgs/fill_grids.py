#!/usr/bin/env python3
# coding: utf-8

import time
import argparse
from js8net import *

def main():
    """
    Main function to fill in missing grids.
    """
    parser = argparse.ArgumentParser(description='Test Script')
    parser.add_argument('--js8_host', default=False, help='IP/DNS of JS8Call server (default localhost)')
    parser.add_argument('--js8_port', default=False, help='TCP port of JS8Call server (default 2442)')
    parser.add_argument("--fill_time", default=False, help="How far back to fill in (default 600 seconds)")
    parser.add_argument("--sleep_time", default=False, help="How long to sleep between requests (default 120 seconds)")
    parser.add_argument("--freq_audio", default=False, help="Specify transmit offset freq (hz, ex: 1000)")
    args = parser.parse_args()

    js8host = args.js8_host if args.js8_host else 'localhost'
    js8port = int(args.js8_port) if args.js8_port else 2442
    filltime = int(args.fill_time) if args.fill_time else 600
    sleeptime = int(args.sleep_time) if args.sleep_time else 120

    start_net(js8host, js8port)
    print("Connected.")

    if args.freq_audio:
        f = get_freq()
        print(f)
        set_freq(f['dial'], int(args.freq_audio))

    stuff = get_call_activity()

    print("Missing grids:")
    for s in stuff:
        if not s.grid and s.age() <= filltime:
            print(s.call)
    print("")

    for s in stuff:
        if not s.grid and s.age() <= filltime:
            print("Requesting grid from " + s.call)
            query_grid(s.call)
            time.sleep(sleeptime)

    time.sleep(3)

if __name__ == "__main__":
    main()
