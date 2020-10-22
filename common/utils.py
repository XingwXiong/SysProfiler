import math
import logging
import subprocess
import numpy as np

logging_fmt = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
logging.basicConfig(format=logging_fmt, level=logging.INFO)
logger = logging.getLogger('SysProfiler')


def popen(cmd):
    # blocked execution
    logger.info("==> cmd running: %s <==" % cmd)
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    logger.info("cmd finished")
    return out + err


def launch_perf_stat_system_wide(interval=1):
    perf_cmd = 'sudo perf stat -a -e %s sleep %f' % (event_codes_str, interval)
    out = str(popen(perf_cmd))
    return out


def launch_perf_stat_command(cmd, repeat=1):
    perf_cmd = 'sudo perf stat -e %s -r %d %s' % (event_codes_str, repeat, cmd)
    out = str(popen(perf_cmd))
    return out


def calc_entropy(labels, base=None):
    """ Computes entropy of label distribution. """
    base = math.e if base is None else base
    n_labels = len(labels)
    if n_labels <= 1:
        return 0
    value, counts = np.unique(labels, return_counts=True)
    probs = counts / n_labels
    n_classes = np.count_nonzero(probs)
    if n_classes <= 1:
        return 0
    # Compute entropy
    ent = 0.
    for i in probs:
        ent -= i * math.log(i, base)
    # print(probs)
    return ent
