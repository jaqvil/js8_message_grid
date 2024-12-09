#!/usr/bin/env python3
# coding: utf-8

import os
import time
import json
import argparse
from os.path import exists
from js8net import *

def main():
    """
    Main function to demonstrate the usage of js8net.py.
    """
    parser = argparse.ArgumentParser(description="Example of using js8net.py")
    parser.add_argument("--js8_host", default=False, help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port", default=False, help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--clean", default=False, action="store_true", help="Start with clean spots (ie, don't load spots.json)")
    parser.add_argument("--env", default=False, action="store_true", help="Use environment variables (cli options override)")
    parser.add_argument("--listen", default=False, action="store_true", help="Listen only - do not write files")
    parser.add_argument("--verbose", default=False, action="store_true", help="Lots of status messages")
    args = parser.parse_args()

    # Load spots.json for some historical context, unless the file is
    # missing, or the user asks not to.
    if exists("spots.json") and not args.clean:
        with spots_lock:
            with open("spots.json") as f:
                spots = json.load(f)

    js8host = args.js8_host if args.js8_host else os.environ.get("JS8HOST") if args.env else "localhost"
    js8port = int(args.js8_port) if args.js8_port else int(os.environ.get("JS8PORT")) if args.env else 2442

    if args.verbose:
        print("Connecting to JS8Call...")
    start_net(js8host, js8port)
    if args.verbose:
        print("Connected.")
    print("Call: ", get_callsign())
    print("Grid: ", get_grid())
    print("Info: ", get_info())
    print("Freq: ", get_freq())
    print("Speed: ", get_speed())
    print("Freq: ", set_freq(7078000, 2000))
    get_band_activity()

    last = time.time()
    while True:
        time.sleep(0.1)
        if not rx_queue.empty():
            with rx_lock:
                rx = rx_queue.get()
                if not args.listen:
                    with open("rx.json", "a") as f:
                        f.write(json.dumps(rx))
                        f.write("\n")
                    if time.time() >= last + 300:
                        last = time.time()
                        with open("spots.json", "w") as f:
                            f.write(json.dumps(spots))
                            f.write("\n")
                if rx['type'] == "RX.DIRECTED":
                    print("FROM:   ", rx['params']['FROM'])
                    print("TO:     ", rx['params']['TO'])
                    if 'rxerror' in rx:
                        print("RX ERR: ", rx['rxerror'])
                    print("CMD:    ", rx['params']['CMD'])
                    print("GRID:   ", rx['params']['GRID'])
                    print("SPEED:  ", rx['params']['SPEED'])
                    print("SNR:    ", rx['params']['SNR'])
                    print("TDRIFT: ", str(int(rx['params']['TDRIFT'] * 1000)))
                    print("DIAL:   ", rx['params']['DIAL'])
                    print("OFFSET: ", rx['params']['OFFSET'])
                    print("EXTRA:  ", rx['params']['EXTRA'])
                    print("TEXT:   ", rx['params']['TEXT'])
                    print()

if __name__ == '__main__':
    main()
