#!/usr/bin/env python

""" Perf Stat Parser Script

Examples:
    $ python get_perf.py -t stat -i perf.stat.log
    $ python get_perf.py -t stat -i perf.mem.log
"""
import os
import sys
import re
import argparse
import pandas as pd
import json
from common.utils import *


def parse_args():
    parser = argparse.ArgumentParser('Perf Result Parser')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='perf stat output file')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='output file path with csv format')
    parser.add_argument('-t', '--type', type=str, default='stat',
                        help='perf log type')
    return parser.parse_args()


def parse_perf_stat(perf_file):
    event_code_map = json.load(open('event_code_map.json', 'r'))
    stat = dict()
    fd = open(perf_file)
    for line in fd.readlines():
        line = line.strip().replace(',', '')

        obj = re.search('^([\d.]+) seconds time elapsed', line)
        if obj:
            stat['elapsed_time'] = float(obj.group(1))
            continue

        obj = re.search('^(\d+)\s+(\w+)', line)
        if obj:
            cnt = int(obj.group(1))
            event = obj.group(2)
            event = event_code_map[event] or event
            stat[event] = cnt
            continue
    fd.close()
    if all(map(lambda x : x in stat.keys(), ['ins', 'load', 'br', 'store', 'fp'])):
        stat['int'] = stat['ins'] - stat['load'] - \
            stat['br'] - stat['store'] - stat['fp']
    if all(map(lambda x : x in stat.keys(), ['UNC_READ', 'UNC_WRITE', 'elapsed_time'])):
        stat['mem_band'] = (stat['UNC_READ'] + stat['UNC_WRITE']) * 64 / stat['elapsed_time']
    if all(map(lambda x : x in stat.keys(), ['cycles', 'ins'])):
        stat['ipc'] = stat['ins']/stat['cycles']
    stat_df = pd.DataFrame([stat])
    return stat_df


def parse_perf_mem(perf_file):
    """get memory entropy
    To get perf_file, you need to run:
            sudo perf mem -D -x , report > /path/to/perf_file
    """
    if not os.path.exists(perf_file):
        raise FileNotFound("%s" % perf_file)
    df = pd.read_csv(perf_file).rename(columns=lambda x: x.strip())
    mem_df = pd.DataFrame([{
        'mem_entropy': calc_entropy(df['ADDR'])
    }])
    return mem_df


def run():
    parser = parse_args()

    if parser.type == 'stat':
        df = parse_perf_stat(parser.input)
    elif parser.type == 'mem':
        df = parse_perf_mem(parser.input)
    else:
        raise TypeError("Invalid parser type=%s", parser.type)

    print(df)
    parser.output and df.to_csv(parser.output, index=False)


if __name__ == '__main__':
    run()
