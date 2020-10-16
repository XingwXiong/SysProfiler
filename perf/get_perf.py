#!/usr/bin/env python

""" Perf Script

Examples:
    system-wide:  $ python get_perf.py --output perf.csv
    command line: $ python get_perf.py --output perf.csv --cmd 'sleep 1'
"""
import os
import sys
import re
import subprocess
import argparse
import pandas as pd
import logging
import json

logging_fmt = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
logging.basicConfig(format=logging_fmt, level=logging.INFO)


def popen(cmd):
    # blocked execution
    logging.info("==> cmd running: %s <==" % cmd)
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    logging.info("cmd finished")
    return out + err


def parse_args():
    parser = argparse.ArgumentParser('Perf Analysis Script')
    parser.add_argument('-o', '--output', type=str,
                        required=True, help='output file path')
    parser.add_argument('-c', '--cmd', type=str, default=None,
                        help='cmd, if this variable is not set, the entire system will be monitored')
    return parser.parse_args()


event_codes = ['r3c', 'rc0', 'rc4', 'r10b', 'r20b', 'r110']
event_descs = ['cycles', 'ins', 'br', 'load', 'store', 'fp']
event_codes_str = ','.join(event_codes)


def launch_perf_stat_system_wide(interval=1):
    perf_cmd = 'sudo perf stat -a -e %s sleep %f' % (event_codes_str, interval)
    out = str(popen(perf_cmd))
    return out


def launch_perf_stat_command(cmd, repeat=1):
    perf_cmd = 'sudo perf stat -e %s -r %d %s' % (event_codes_str, repeat, cmd)
    out = str(popen(perf_cmd))
    return out


def parse_perf_stat(cmd_out):
    cmd_out = cmd_out.replace(',', '')
    counters = map(int, re.findall('\s+(\d+)\s+', cmd_out, re.M))
    elapsed_time = float(re.findall(
        '\s+(\d+\.*\d+) seconds time elapsed', cmd_out, re.M)[0])

    stat = dict(zip(event_descs, counters))
    logging.debug("stat dict: %s" % json.dumps(stat, indent=2))
    stat['elapsed_time'] = elapsed_time
    stat['int'] = stat['ins'] - stat['load'] - \
        stat['br'] - stat['store'] - stat['fp']
    # stat['mem_band'] = (stat['UNC_READ'] + stat['UNC_WRITE']) * 64 / stat['elapsed_time']
    return stat


def perf_system_analysis(output, interval=1, epoch_num=10):
    if os.path.exists(output):
        os.remove(output)
    for epoch in range(epoch_num):
        out = launch_perf_stat_system_wide(interval=1)
        stat = parse_perf_stat(out)
        df = pd.DataFrame([stat])
        if not os.path.exists(output):
            df.to_csv(output, mode='w', header=True, index=False)
        else:
            df.to_csv(output, mode='a', header=False, index=False)
    stats_df = pd.read_csv(output)
    logging.info("system-wide stat:\n%s" % str(stats_df))


def perf_cmd_analysis(output, run_cmd):
    if os.path.exists(output):
        os.remove(output)
    out = launch_perf_stat_command(run_cmd)
    stat = parse_perf_stat(out)
    df = pd.DataFrame([stat])
    df.to_csv(output, mode='w', header=True, index=False)
    logging.info("cmd stat:\n%s" % str(df))


def run():
    parser = parse_args()
    if parser.cmd:
        perf_cmd_analysis(parser.output, parser.cmd)
    else:
        perf_system_analysis(parser.output)


if __name__ == '__main__':
    run()
