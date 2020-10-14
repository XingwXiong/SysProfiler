#!/usr/bin/env python

""" Perf Script

Examples:
    python get_perf.py --output perf.csv --cmd_line 'ls -lrth'
"""
import os
import sys
import re
import subprocess
import argparse
import pandas as pd


def popen(cmd):
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out + err


def parse_args():
    parser = argparse.ArgumentParser('Perf Analysis Script')
    parser.add_argument('-o', '--output', type=str,
                        required=True, help='output file path')
    parser.add_argument('-c', '--cmd', type=str, default=None,
                        help='cmd, if this variable is not set, the entire system will be monitored')
    return parser.parse_args()


event_codes = ['r3c', 'rc0', 'rc4', 'r10b', 'r20b', 'r110',
               'uncore/event=0x2c,umask=0x07/', 'uncore/event=0x2f,umask=0x07/', 'r01c2']
event_descs = ['cycles', 'ins', 'br', 'load',
               'store', 'fp', 'UNC_READ', 'UNC_WRITE', 'UOPS']


def perf_system_analysis(output, interval=1, epoch_num=10):
    perf_cmd = 'sudo perf stat -a -e %s sleep %f' % (
        ','.join(event_codes), interval)
    if os.path.exists(output):
        os.remove(output)
    for epoch in range(epoch_num):
        out = str(popen(perf_cmd))
        out = out.replace(',', '')
        counters = re.findall('\s+(\d+)\s+', out, re.M)
        elapsed_time = float(re.findall('\s+(\d+\.*\d+) seconds time elapsed', out, re.M)[0])
        df = pd.DataFrame([dict(zip(event_descs, counters))]).astype(int)
        
        df['elapsed_time'] = elapsed_time
        df['int'] = df['ins'] - df['load'] - df['br'] - df['store'] - df['fp']
        df['mem_band'] = (df['UNC_READ'] + df['UNC_WRITE']) * 64 / df['elapsed_time']

        if not os.path.exists(output):
            df.to_csv(output, mode='w', header=True, index=False)
        else:
            df.to_csv(output, mode='a', header=False, index=False)
    stats_df = pd.read_csv(output)
    print(stats_df)


def perf_cmd_analysis(output, run_cmd):
    perf_cmd = 'perf stat -e %s "%s"' % (','.join(event_codes), run_cmd)
    print(perf_cmd)


def run():
    parser = parse_args()
    if parser.cmd:
        perf_cmd_analysis(parser.output, parser.cmd)
    else:
        perf_system_analysis(parser.output)


if __name__ == '__main__':
    run()
