#!/usr/bin/env python3
# coding: utf-8

import dbm
import json
import argparse
import csv
from os.path import exists
from os.path import expanduser

def load_usa_data(usa, calldb):
    """
    Load USA callsign records into the database.

    Args:
        usa (str): Path to the USA data file.
        calldb (dbm): Database to store the callsign records.
    """
    if exists(usa):
        print('Loading USA callsign records...')
        with open(usa, 'r', encoding='utf8') as usa_file:
            usa_reader = csv.reader(usa_file, delimiter='|')
            for row in usa_reader:
                call = row[4]
                name = row[7]
                house = row[15]
                city = row[16]
                state = row[17]
                calldb[call] = json.dumps({'name': name,
                                           'info': ', '.join([name, city, state, 'US']),
                                           'address': ', '.join([house, city, state, 'USA'])})
    else:
        print('Unable to find USA data.')

def load_canada_data(canada, calldb):
    """
    Load Canadian callsign records into the database.

    Args:
        canada (str): Path to the Canadian data file.
        calldb (dbm): Database to store the callsign records.
    """
    if exists(canada):
        print('Loading Canadian callsign records...')
        with open(canada, 'r', encoding='utf8') as canada_file:
            canada_reader = csv.reader(canada_file, delimiter=';')
            for row in canada_reader:
                call = row[0]
                first_name = row[1]
                last_name = row[2]
                house = row[3]
                city = row[4]
                province = row[5]
                calldb[call] = json.dumps({'name': last_name,
                                           'info': ', '.join([last_name, first_name, city, province, 'CA']),
                                           'address': ', '.join([house, city, province, 'Canada'])})
    else:
        print('Unable to find Canada data.')

def load_australia_data(australia, calldb):
    """
    Load Australian callsign records into the database.

    Args:
        australia (str): Path to the Australian data directory.
        calldb (dbm): Database to store the callsign records.
    """
    print('Loading Australian callsign records...')

    print('Loading device details...')
    with open(australia + 'device_details.csv', 'r', encoding='utf8') as dd_file:
        # This maps the id with a '/' to a callsign.
        dd_reader = csv.reader(dd_file, delimiter=',')
        dd = {}
        for row in dd_reader:
            dd[row[1]] = row[33]

    print('Loading client info...')
    with open(australia + 'client.csv', 'r', encoding='utf8') as client_file:
        # This maps the id without a '/' to an address.
        client_reader = csv.reader(client_file, delimiter=',')
        client = {}
        for row in client_reader:
            client[row[0]] = row

    print('Loading license info...')
    with open(australia + 'licence.csv', 'r', encoding='utf8') as lic_file:
        lic_reader = csv.reader(lic_file, delimiter=',')
        # This gets us a list of Amateur license holder IDs. The first
        # value lets us find their call in device_details.csv and the
        # second lets us find their address in client.csv.
        for row in lic_reader:
            if row[4] == 'Amateur':
                if row[0] in dd and row[1] in client:
                    call = dd[row[0]]
                    c = client[row[1]]
                    name = c[1]
                    house = c[5]
                    city = c[6]
                    territory = c[7]
                    calldb[call] = json.dumps({'name': name,
                                               'info': ', '.join([name, city, territory, 'AU']),
                                               'address': ', '.join([house, city, territory, 'Australia'])})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aggregate collected JS8call data from collectors.')
    parser.add_argument('--usa', default=False, help='Path to EN.dat file (default is ./EN.dat)')
    parser.add_argument('--canada', default=False, help='Path to amateur_delim.txt file (default is ./amateur_delim.txt)')
    parser.add_argument('--australia', default=False, help='Path to extracted AUS directory (default is ./)')
    parser.add_argument('--basedir', default=False, help='Monitor program directory (default is ~/.js8net/)')
    args = parser.parse_args()

    usa = args.usa if args.usa else 'EN.dat'
    canada = args.canada if args.canada else 'amateur_delim.txt'
    australia = args.australia if args.australia else './'
    basedir = args.basedir if args.basedir else expanduser("~") + '/.js8net/'

    if basedir[-1] != '/':
        basedir += '/'

    if not exists(basedir):
        mkdir(basedir)

    calldb = dbm.open(basedir + 'calldb.dbm', 'c')

    load_usa_data(usa, calldb)
    load_canada_data(canada, calldb)
    load_australia_data(australia, calldb)

    print('Done.')
