#!/bin/bash
# use perf to profile SPECCPU 2017

bench_name=500.perlbench_r
bench_type=perf

if [ -n "$1" ]; then
    bench_name=$1
fi

cur_dir=$(cd `dirname $0`; pwd)
log_dir=$cur_dir/results/$bench_name/$bench_type
run_dir=$SPEC_HOME/benchspec/CPU/$bench_name/run/run_base_refrate_hw114-m64.0000

if [ ! -d $run_dir ]; then
    echo "ERROR: Directory $run_dir not exists"
    exit
fi

echo "INFO: bench_name=$bench_name"
echo "INFO: bench_type=$bench_type"

sleep 3
cd $run_dir

rm -rf $log_dir
mkdir -p $log_dir

cmd_line=$(tail -n1 speccmds.cmd | grep "../run_base_refrate_hw114-m64.0000.*" -o | sed "s#> \(.*[(out)|(log)]\) 2>> \(.*err\)##")
set -x

echo 'workspace: ', $run_dir
eval "echo xingw.xiong | sudo -S perf stat -e r3c,rc0,rc4,r10b,r20b,r110 -r 3 ${cmd_line}" > ${log_dir}/run.stat.log 2>> ${log_dir}/perf.stat.log
eval "echo xingw.xiong | sudo -S perf mem -t load record ${cmd_line}" > ${log_dir}/run.mem.log 2>> ${log_dir}/perf.mem.log
eval "echo xingw.xiong | sudo -S chmod 644 ${log_dir}/perf.data"

export PYTHONPATH=$cur_dir/../:$PYTHONPATH
python3 $cur_dir/perf_parser.py -i perf.stat.log -o $log_dir/perf.stat.csv

mv perf.data $log_dir

