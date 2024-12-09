#!/usr/bin/env python3
# coding: utf-8

import os
import time
import argparse
from js8net import *

def main():
    """
    Main function to send SOTA spot via JS8Call.
    """
    parser = argparse.ArgumentParser(description="Send SOTA spot via JS8Call.")
    parser.add_argument("--js8_host", default=False, help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port", default=False, help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--summit", default=False, help="Summit designator")
    parser.add_argument("--mode", default=False, help="Operating mode (typically CW, USB, LSB, AM, FM, etc)")
    parser.add_argument("--spotfreq", default=False, help="Operating frequency in khz")
    parser.add_argument("--comment", default=False, help="Operating comment (optional)")
    parser.add_argument("--freq", default=False, help="Specify transmit freq (hz, ex: 7079000)")
    parser.add_argument("--freq_dial", default=False, help="Specify dial freq (hz, ex: 7078000)")
    parser.add_argument("--freq_audio", default=False, help="Specify transmit offset freq (hz, ex: 1000)")
    parser.add_argument("--speed", default=False, help="Specify transmit speed (slow==4, normal==0, fast==1, turbo==2)")
    parser.add_argument("--env", default=False, action="store_true", help="Use environment variables (cli options override)")
    parser.add_argument("--verbose", default=False, action="store_true", help="Lots of status messages")
    args = parser.parse_args()

    js8host = args.js8_host if args.js8_host else os.environ.get("JS8HOST") if args.env else "localhost"
    js8port = int(args.js8_port) if args.js8_port else int(os.environ.get("JS8PORT")) if args.env else 2442

    if not (args.summit and args.mode and args.spotfreq):
        print("--summit, --mode, and --spotfreq are mandatory")
        return

    if args.verbose:
        print("Connecting to JS8Call...")
    start_net(js8host, js8port)
    if args.verbose:
        print("Connected.")

    if args.freq or args.freq_dial or args.freq_audio:
        f = get_freq()
        if args.freq_dial and args.freq_audio:
            set_freq(args.freq_dial, args.freq_audio)
        elif args.freq and args.freq_audio:
            set_freq(args.freq_dial - args.freq_audio, args.freq_audio)
        elif args.freq:
            set_freq(args.freq_dial - 1000, 1000)
        elif args.freq_audio:
            set_freq(f['dial'], args.freq_audio)
    if args.verbose:
        print("Frequency set to ", get_freq())

    if args.speed:
        speed = int(args.speed)
        if 0 <= speed <= 4 and speed != 3:
            if args.verbose:
                print("Setting speed to ", str(speed))
            set_speed(speed)

    send_sota(args.summit, args.spotfreq, args.mode, args.comment)
    time.sleep(3)
    if args.verbose:
        print("Message sent.")

if __name__ == "__main__":
    main()
