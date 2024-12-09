#!/usr/bin/env python3
# coding: utf-8

import sys
import socket
import json
import time
import threading
import traceback
from threading import Thread
from queue import Queue

# Defaults within JS8Call.
eom = "♢"
error = "…"
timeout = 1.0

# These are our global objects (and locks for them).
tx_queue = Queue()
tx_lock = threading.Lock()
rx_queue = Queue()
rx_lock = threading.Lock()
spots_lock = threading.Lock()
unique = 0
unique_lock = threading.Lock()
s = False

# These globals represent the state of JS8Call.
spots = {}
dial = None
freq = None
offset = None
grid = None
info = None
call = None
speed = None
ptt = None
tx_text = None
rx_text = None
last_rx = None
mycall = None
messages = None
call_activity = None
band_activity = None

def calc_band(freq):
    """
    Calculate the band based on the frequency.

    Args:
        freq (int): Frequency in Hz.

    Returns:
        str: Band name.
    """
    if 1800000 <= freq <= 2000000:
        return "160m"
    elif 3500000 <= freq <= 4000000:
        return "80m"
    elif 5330000 <= 5410000:
        return "60m"
    elif 7000000 <= 7300000:
        return "40m"
    elif 10100000 <= 10150000:
        return "30m"
    elif 14000000 <= 14350000:
        return "20m"
    elif 17068000 <= 17168000:
        return "17m"
    elif 21000000 <= 21450000:
        return "15m"
    elif 24890000 <= 24990000:
        return "12m"
    elif 28000000 <= 29700000:
        return "10m"
    elif 50000000 <= 54000000:
        return "6m"
    elif 144000000 <= freq <= 148000000:
        return "2m"
    elif 219000000 <= freq <= 225000000:
        return "1.25m"
    elif 420000000 <= freq <= 450000000:
        return "70cm"
    else:
        return False

def process_message(msg):
    """
    Process an incoming message and record any useful stats about it.

    Args:
        msg (dict): Incoming message.
    """
    global spots, mycall, messages
    if 'MESSAGES' in msg['params']:
        messages = msg['params']['MESSAGES']
    if msg['type'] == "RX.SPOT":
        with spots_lock:
            band = calc_band(msg['params']['FREQ'])
            if mycall not in spots:
                spots[mycall] = {}
            if msg['params']['CALL'] not in spots[mycall]:
                spots[mycall][msg['params']['CALL']] = []
            grid = msg['params']['GRID'] if msg['params']['GRID'] != "" else False
            spots[mycall][msg['params']['CALL']].append({
                'time': msg['time'],
                'band': band,
                'grid': grid,
                'speed': False,
                'snr': msg['params']['SNR']
            })
    if msg['type'] == "RX.DIRECTED":
        with spots_lock:
            band = calc_band(msg['params']['FREQ'])
            if mycall not in spots:
                spots[mycall] = {}
            if msg['params']['FROM'] not in spots[mycall]:
                spots[mycall][msg['params']['FROM']] = []
            grid = msg['params']['GRID'] if msg['params']['GRID'] != "" else False
            spots[mycall][msg['params']['FROM']].append({
                'time': msg['time'],
                'band': band,
                'grid': grid,
                'speed': msg['params']['SPEED'],
                'snr': msg['params']['SNR']
            })
            if msg['params']['CMD'] in [" HEARTBEAT SNR", " SNR"]:
                grid = msg['params']['GRID'] if msg['params']['GRID'] != "" else False
                if msg['params']['FROM'] not in spots:
                    spots[msg['params']['FROM']] = {}
                if msg['params']['TO'] not in spots[msg['params']['FROM']]:
                    spots[msg['params']['FROM']][msg['params']['TO']] = []
                spots[msg['params']['FROM']][msg['params']['TO']].append({
                    'time': msg['time'],
                    'band': band,
                    'grid': grid,
                    'speed': msg['params']['SPEED'],
                    'snr': int(msg['params']['EXTRA'])
                })
            elif msg['params']['CMD'] == " GRID":
                grid = msg['params']['TEXT'].split()[3]
                if error not in grid:
                    if msg['params']['FROM'] not in spots:
                        spots[msg['params']['FROM']] = {}
                    if msg['params']['TO'] not in spots[msg['params']['FROM']]:
                        spots[msg['params']['FROM']][msg['params']['TO']] = []
                    spots[msg['params']['FROM']][msg['params']['TO']].append({
                        'time': msg['time'],
                        'band': band,
                        'grid': grid,
                        'speed': msg['params']['SPEED'],
                        'snr': False
                    })
            elif msg['params']['CMD'] == " HEARING":
                grid = msg['params']['GRID'] if msg['params']['GRID'] != "" else False
                if 'FROM' in msg['params']:
                    if msg['params']['FROM'] not in spots:
                        spots[msg['params']['FROM']] = {}
                if error not in msg['params']['TEXT']:
                    hearing = msg['params']['TEXT'].split()[3:-1]
                    for h in hearing:
                        if h not in msg['params']['FROM']:
                            spots[msg['params']['FROM']][h] = []
                        spots[msg['params']['FROM']][h].append({
                            'time': msg['time'],
                            'band': band,
                            'grid': False,
                            'speed': msg['params']['SPEED'],
                            'snr': False
                        })

def queue_message(message):
    """
    Add a message to the outgoing message queue.

    Args:
        message (dict): Message to be added to the queue.
    """
    with tx_lock:
        tx_queue.put(message)

def tx_thread(name):
    """
    Thread to watch the transmit queue and send data to JS8.

    Args:
        name (str): Name of the thread.
    """
    while True:
        thing = json.dumps(tx_queue.get())
        with tx_lock:
            s.sendall(bytes(thing + "\r\n", 'utf-8'))
        time.sleep(0.25)

class Callstation:
    """
    Station class for RX.CALL_ACTIVITY.
    """
    def __init__(self, call, stuff):
        self.call = call
        self.snr = stuff['SNR']
        self.utc = stuff['UTC'] / 1000
        self.grid = stuff['GRID'].strip() if stuff['GRID'] else False

    def age(self):
        """
        Calculate the age of the station.

        Returns:
            int: Age in seconds.
        """
        return round(time.time() - self.utc)

    def string(self):
        """
        Get the string representation of the station.

        Returns:
            str: String representation.
        """
        if self.grid:
            return f'Call: {self.call}\tSNR: {self.snr}\tAge: {self.age()}\tGrid: {self.grid}'
        else:
            return f'Call: {self.call}\tSNR: {self.snr}\tAge: {self.age()}'

class Bandstation:
    """
    Station class for RX.BAND_ACTIVITY.
    """
    def __init__(self, stuff):
        self.dial = stuff['DIAL']
        self.freq = stuff['FREQ']
        self.offset = stuff['OFFSET']
        self.snr = stuff['SNR']
        self.text = stuff['TEXT']
        self.utc = stuff['UTC'] / 1000

    def age(self):
        """
        Calculate the age of the station.

        Returns:
            int: Age in seconds.
        """
        return round(time.time() - self.utc)

    def string(self):
        """
        Get the string representation of the station.

        Returns:
            str: String representation.
        """
        return f'Freq: {self.freq / 1000} khz ({self.dial / 1000} khz + {self.offset} hz)\tSNR: {self.snr}\tAge: {self.age()}\tText: {self.text}'

def rx_thread(name):
    """
    Thread to receive messages from JS8Call.

    Args:
        name (str): Name of the thread.
    """
    global dial, freq, offset, grid, info, call, speed, ptt, tx_text, rx_text, call_activity, band_activity, last_rx
    n = 0
    left = False
    empty = True
    while True:
        try:
            string = ""
            stuff = s.recv(65535)
            if not empty:
                stuff = left + stuff
            if stuff[0:1] == b'{' and stuff[-2:-1] == b'}':
                string = stuff.decode("utf-8")
                empty = True
            else:
                if empty:
                    empty = False
                    left = stuff
            if string == "":
                message = {"type": "empty"}
            else:
                string = string.rstrip("\n")
                for m in string.split("\n"):
                    message = json.loads(m)
                    now = time.time()
                    message['time'] = now
                    last_rx = now
                    if 'params' in message.keys() and 'TEXT' in message['params'].keys():
                        message['rxerror'] = error in message['params']['TEXT']
                    try:
                        process_message(message)
                    except Exception:
                        print("Message: ", message)
                        traceback.print_exc()
                    if message['type'] == "RIG.FREQ":
                        dial = message['params']['DIAL']
                        freq = message['params']['FREQ']
                        offset = message['params']['OFFSET']
                    elif message['type'] == "STATION.CALLSIGN":
                        call = message['value']
                    elif message['type'] == "STATION.GRID":
                        grid = message['value']
                    elif message['type'] == "STATION.INFO":
                        info = message['value']
                    elif message['type'] == "MODE.SPEED":
                        speed = str(message['params']['SPEED'])
                    elif message['type'] == "RIG.PTT":
                        ptt = message['value'] == "on"
                    elif message['type'] == "RX.CALL_SELECTED":
                        pass
                    elif message['type'] == "TX.FRAME":
                        pass
                    elif message['type'] == "TX.TEXT":
                        tx_text = message['value']
                    elif message['type'] == "RX.TEXT":
                        rx_text = message['value']
                    elif message['type'] == "RX.CALL_ACTIVITY":
                        tmp = message['params']
                        if '_ID' in tmp:
                            del tmp['_ID']
                        stations = list(map(lambda c: Callstation(c, tmp[c]), list(tmp.keys())))
                        call_activity = stations
                    elif message['type'] == "RX.BAND_ACTIVITY":
                        tmp = message['params']
                        if '_ID' in tmp:
                            del tmp['_ID']
                        stations = list(map(lambda c: Bandstation(tmp[c]), list(tmp.keys())))
                        band_activity = stations
                    elif message['type'] == "RX.SPOT":
                        pass
                    if message['type'] not in ["RIG.FREQ", "STATION.CALLSIGN", "STATION.GRID", "STATION.INFO", "MODE.SPEED", "RIG.PTT", "RX.CALL_SELECTED", "TX.FRAME", "TX.TEXT", "RX.TEXT", "RX.CALL_ACTIVITY", "RX.BAND_ACTIVITY", "RX.SPOT"]:
                        with rx_lock:
                            rx_queue.put(message)
            time.sleep(0.1)
        except socket.timeout:
            n += 1
            time.sleep(0.1)

def hb_thread(name):
    """
    Thread to send a heartbeat request to JS8Call.

    Args:
        name (str): Name of the thread.
    """
    global mycall
    while True:
        mycall = get_callsign()
        time.sleep(300)

def start_net(host, port):
    """
    Start the network connection to JS8Call.

    Args:
        host (str): Hostname of the JS8Call server.
        port (int): Port of the JS8Call server.
    """
    global s
    s = socket.socket()
    s.connect((host, int(port)))
    s.settimeout(1)
    thread1 = Thread(target=rx_thread, args=("RX Thread",), daemon=True)
    thread1.start()
    thread2 = Thread(target=tx_thread, args=("TX Thread",), daemon=True)
    thread2.start()
    thread3 = Thread(target=hb_thread, args=("HB Thread",), daemon=True)
    thread3.start()
    time.sleep(1)

def get_freq():
    """
    Get the radio's frequency.

    Returns:
        dict: Dial frequency, offset, and actual frequency.
    """
    global dial, freq, offset, timeout
    dial = False
    freq = False
    offset = False
    queue_message({"params": {}, "type": "RIG.GET_FREQ", "value": ""})
    now = time.time()
    while not (dial and freq and offset):
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return {"dial": dial, "freq": freq, "offset": offset}

def set_freq(dial, offset):
    """
    Set the radio's frequency.

    Args:
        dial (int): Dial frequency in Hz.
        offset (int): Offset frequency in Hz.

    Returns:
        dict: Updated frequency information.
    """
    queue_message({"params": {"DIAL": dial, "OFFSET": offset}, "type": "RIG.SET_FREQ", "value": ""})
    time.sleep(0.1)
    return get_freq()

def get_messages():
    """
    Fetch all inbox messages.

    Returns:
        list: List of messages.
    """
    global messages, timeout
    messages = False
    queue_message({"params": {}, "type": "INBOX.GET_MESSAGES", "value": ""})
    now = time.time()
    while not messages:
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return messages

def store_message(callsign, text):
    """
    Store a message in the INBOX for later pickup by recipient.

    Args:
        callsign (str): Recipient callsign.
        text (str): Message text.

    Returns:
        list: Updated list of messages.
    """
    queue_message({"params": {"CALLSIGN": callsign, "TEXT": text}, "type": "INBOX.STORE_MESSAGE", "value": ""})
    time.sleep(0.1)
    return get_messages()

def get_callsign():
    """
    Get the configured callsign.

    Returns:
        str: Callsign.
    """
    global call, timeout
    call = False
    queue_message({"params": {}, "type": "STATION.GET_CALLSIGN", "value": ""})
    now = time.time()
    while not call:
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return call

def get_grid():
    """
    Get the configured grid square.

    Returns:
        str: Grid square.
    """
    global grid, timeout
    grid = False
    queue_message({'params': {}, 'type': 'STATION.GET_GRID', 'value': ''})
    now = time.time()
    while not grid:
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return grid

def set_grid(grid):
    """
    Set the grid square.

    Args:
        grid (str): Grid square.

    Returns:
        str: Updated grid square.
    """
    queue_message({"params": {}, "type": "STATION.SET_GRID", "value": grid})
    return get_grid()

def send_aprs_grid(grid):
    """
    Send the supplied grid info to APRS.

    Args:
        grid (str): Grid square.
    """
    send_message("@APRSIS GRID " + grid)

def send_heartbeat(grid=False):
    """
    Send a heartbeat message.

    Args:
        grid (str, optional): Grid square. Defaults to False.
    """
    if not grid:
        grid = get_grid()
    if len(grid) >= 4:
        grid = grid[0:4]
        send_message(get_callsign() + ": @HB HEARTBEAT " + grid)

def send_sms(phone, message):
    """
    Send an SMS message via JS8.

    Args:
        phone (str): Recipient phone number.
        message (str): Message text.
    """
    global unique
    with unique_lock:
        unique += 1
        if unique > 99:
            unique = 1
        send_message("@APRSIS CMD :SMSGTE   :@" + phone + " " + message + "{%02d}" % unique)

def send_email(address, message):
    """
    Send an email message via JS8.

    Args:
        address (str): Recipient email address.
        message (str): Message text.
    """
    global unique
    with unique_lock:
        unique += 1
        if unique > 99:
            unique = 1
        send_message("@APRSIS CMD :EMAIL-2  :" + address + " " + message + "{%02d}" % unique)

def send_aprs(dest, message):
    """
    Send an APRS message to the destination call.

    Args:
        dest (str): Destination callsign.
        message (str): Message text.
    """
    global unique
    dest = dest[0:9]
    while len(dest) < 9:
        dest += " "
    with unique_lock:
        unique += 1
        if unique > 99:
            unique = 1
        send_message("@APRSIS CMD :" + dest + ":" + message + "{%02d}" % unique)

def send_sota(summit, freq, mode, comment=False):
    """
    Send a SOTA spot.

    Args:
        summit (str): Summit designator.
        freq (int): Operating frequency in kHz.
        mode (str): Operating mode.
        comment (str, optional): Operating comment. Defaults to False.
    """
    global unique
    with unique_lock:
        unique += 1
        if unique > 99:
            unique = 1
        if comment:
            send_message("@APRSIS CMD :APRS2SOTA:" + get_callsign() + ";" + summit + ";" + str(int(freq)) + ";" + mode + ";" + comment + "{%02d}" % unique)
        else:
            send_message("@APRSIS CMD :APRS2SOTA:" + get_callsign() + ";" + summit + ";" + str(int(freq)) + ";" + mode + "{%02d}" % unique)

def send_pota(park, freq, mode, comment=False):
    """
    Send a POTA spot.

    Args:
        park (str): Park designator.
        freq (int): Operating frequency in kHz.
        mode (str): Operating mode.
        comment (str, optional): Operating comment. Defaults to False.
    """
    global unique
    with unique_lock:
        unique += 1
        if unique > 99:
            unique = 1
        if comment:
            send_message("@APRSIS CMD :POTAGW   :" + get_callsign() + " " + park + " " + str(int(freq)) + " " + mode + " " + comment + "{%02d}" % unique)
        else:
            send_message("@APRSIS CMD :POTAGW   :" + get_callsign() + " " + park + " " + str(int(freq)) + " " + mode + "{%02d}" % unique)

def get_info():
    """
    Get the configured info field.

    Returns:
        str: Info field.
    """
    global info, timeout
    info = False
    queue_message({"params": {}, "type": "STATION.GET_INFO", "value": ""})
    now = time.time()
    while not info:
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return info

def set_info(info):
    """
    Set the info field.

    Args:
        info (str): Info field.

    Returns:
        str: Updated info field.
    """
    queue_message({"params": {}, "type": "STATION.SET_INFO", "value": info})
    return get_info()

def get_call_activity():
    """
    Get the contents of the right white window.

    Returns:
        list: List of call activities.
    """
    global call_activity, timeout
    call_activity = False
    queue_message({"params": {}, "type": "RX.GET_CALL_ACTIVITY", "value": ""})
    now = time.time()
    while not call_activity:
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return call_activity

def get_call_selected():
    """
    Get the selected call.

    Returns:
        None
    """
    queue_message({"params": {}, "type": "RX.GET_CALL_SELECTED", "value": ""})

def get_band_activity():
    """
    Get the contents of the left white window.

    Returns:
        list: List of band activities.
    """
    global band_activity, timeout
    band_activity = False
    queue_message({"params": {}, "type": "RX.GET_BAND_ACTIVITY", "value": ""})
    now = time.time()
    while not band_activity:
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return band_activity

def get_rx_text():
    """
    Get the contents of the yellow window.

    Returns:
        str: Text in the yellow window.
    """
    global rx_text, timeout
    rx_text = '-=-=-=-shibboleeth-=-=-=-'
    queue_message({"params": {}, "type": "RX.GET_TEXT", "value": ""})
    now = time.time()
    while rx_text == '-=-=-=-shibboleeth-=-=-=-':
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return rx_text

def get_tx_text():
    """
    Get the contents of the window below the yellow window.

    Returns:
        str: Text in the window below the yellow window.
    """
    global tx_text, timeout
    tx_text = '-=-=-=-shibboleeth-=-=-=-'
    queue_message({"params": {}, "type": "TX.GET_TEXT", "value": ""})
    now = time.time()
    while tx_text == '-=-=-=-shibboleeth-=-=-=-':
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return tx_text

def set_tx_text(text):
    """
    Set the contents of the window below the yellow window.

    Args:
        text (str): Text to be set.

    Returns:
        str: Updated text in the window below the yellow window.
    """
    queue_message({"params": {}, "type": "TX.SET_TEXT", "value": text})
    return get_tx_text()

def get_speed():
    """
    Get the current transmission speed.

    Returns:
        str: Transmission speed.
    """
    global speed, timeout
    speed = False
    queue_message({"params": {}, "type": "MODE.GET_SPEED", "value": ""})
    now = time.time()
    while not speed:
        if time.time() > now + timeout:
            return False
        time.sleep(0.1)
    return speed

def speed_name(speed):
    """
    Get the name of the transmission speed.

    Args:
        speed (int): Transmission speed.

    Returns:
        str: Name of the transmission speed.
    """
    if 0 <= speed <= 4:
        return ['Normal', 'Fast', 'Turbo', 'Invalid', 'Slow'][speed]
    else:
        return 'Invalid'

def set_speed(speed):
    """
    Set the transmission speed.

    Args:
        speed (int): Transmission speed.

    Returns:
        str: Updated transmission speed.
    """
    queue_message({"params": {"SPEED": speed}, "type": "MODE.SET_SPEED", "value": ""})
    return get_speed()

def raise_window():
    """
    Raise the JS8Call window to the top.
    """
    queue_message({"params": {}, "type": "WINDOW.RAISE", "value": ""})

def send_message(message):
    """
    Send a message in the next transmit cycle.

    Args:
        message (str): Message to be sent.
    """
    queue_message({"params": {}, "type": "TX.SEND_MESSAGE", "value": message})

def send_directed_message(dest_call, message):
    """
    Send a directed message to a specific call sign.

    Args:
        dest_call (str): Destination callsign.
        message (str): Message to be sent.
    """
    queue_message({"params": {}, "type": "TX.SEND_MESSAGE", "value": dest_call + " " + message})

def send_inbox_message(dest_call, message):
    """
    Send a directed message to a specific call sign.

    Args:
        dest_call (str): Destination callsign.
        message (str): Message to be sent.
    """
    queue_message({"params": {}, "type": "TX.SEND_MESSAGE", "value": dest_call + " MSG " + message})

def alive():
    """
    Check if the TCP connection is still alive.

    Returns:
        bool: True if the connection is alive, False otherwise.
    """
    global last_rx
    return time.time() - last_rx <= 335

def query_snr(dest_call):
    """
    Query a station for your SNR report.

    Args:
        dest_call (str): Destination callsign.
    """
    queue_message({"params": {}, "type": "TX.SEND_MESSAGE", "value": dest_call + " SNR? "})

def query_grid(dest_call):
    """
    Query a station for their grid square.

    Args:
        dest_call (str): Destination callsign.
    """
    queue_message({"params": {}, "type": "TX.SEND_MESSAGE", "value": dest_call + " GRID? "})

def query_status(dest_call):
    """
    Query a station for their status.

    Args:
        dest_call (str): Destination callsign.
    """
    queue_message({"params": {}, "type": "TX.SEND_MESSAGE", "value": dest_call + " STATUS? "})

def query_info(dest_call):
    """
    Query a station for their info.

    Args:
        dest_call (str): Destination callsign.
    """
    queue_message({"params": {}, "type": "TX.SEND_MESSAGE", "value": dest_call + " INFO? "})

def query_hearing(dest_call):
    """
    Query a station for top stations heard.

    Args:
        dest_call (str): Destination callsign.
    """
    queue_message({"params": {}, "type": "TX.SEND_MESSAGE", "value": dest_call + " HEARING? "})

if __name__ == '__main__':
    print("This is a library and is not intended for stand-alone execution.")
