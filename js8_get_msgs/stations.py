#!/usr/bin/env python3
# coding: utf-8

import time
import json
import argparse
from js8net import *

def main():
    """
    Main function to report monitored stations.
    """
    parser = argparse.ArgumentParser(description='Monitored Station Reporter.')
    parser.add_argument('--js8_host', default=False, help='IP/DNS of JS8Call server (default localhost)')
    parser.add_argument('--js8_port', default=False, help='TCP port of JS8Call server (default 2442)')
    parser.add_argument('--call_activity', default=False, help='Show only call activity', action='store_true')
    parser.add_argument('--band_activity', default=False, help='Show only band activity', action='store_true')
    parser.add_argument('--age', default=False, help='Sort list by age', action='store_true')
    parser.add_argument('--snr', default=False, help='Sort list by SNR', action='store_true')
    args = parser.parse_args()

    js8host = args.js8_host if args.js8_host else 'localhost'
    js8port = int(args.js8_port) if args.js8_port else 2442

    # Connect to JS8Call.
    start_net(js8host, js8port)

    # If Call Activity...
    if not args.call_activity:
        stuff = get_call_activity()
        if stuff:
            if args.age:
                for station in sorted(stuff, key=lambda n: n.age()):
                    print(station.string())
            elif args.snr:
                for station in sorted(stuff, key=lambda n: n.snr, reverse=True):
                    print(station.string())
            else:
                for station in stuff:
                    print(station.string())
        else:
            print('No active stations.')
        print()

    # If Band Activity...
    if not args.band_activity:
        stuff = get_band_activity()
        if stuff:
            if args.age:
                for station in sorted(stuff, key=lambda n: n.age()):
                    print(station.string())
            elif args.snr:
                for station in sorted(stuff, key=lambda n: n.snr, reverse=True):
                    print(station.string())
            else:
                for station in stuff:
                    print(station.string())
        else:
            print('No active stations.')

if __name__ == "__main__":
    main()
