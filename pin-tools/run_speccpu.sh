#!/bin/bash
# use pin/mica to profile SPECCPU 2017

bench_name=523.xalancbmk_r
bench_type=mica

if [ -n "$1" ]; then
    bench_name=$1
fi

cur_dir=$(cd `dirname $0`; pwd)
log_dir=$cur_dir/results/$bench_name/$bench_type
pin_dir=$PIN_HOME/source/tools/MICA-BenchCPU
run_dir=$SPEC_HOME/benchspec/CPU/$bench_name/run/run_base_refrate_hw114-m64.0000

if [ ! -d $run_dir ]; then
    echo "ERROR: Directory $run_dir not exists"
    exit
fi

echo "INFO: bench_name=$bench_name"
echo "INFO: bench_type=$bench_type"

sleep 3
cd $run_dir

rm -f itypes_*.txt itypes_*.out mica.log
cp $pin_dir/itypes_default.spec $pin_dir/mica.conf .
rm -rf $log_dir
mkdir -p $log_dir

cmd_line=$(tail -n1 speccmds.cmd | grep "../run_base_refrate_hw114-m64.0000.*" -o | sed "s#> \(.*[(out)|(log)]\) 2>> \(.*err\)#> ${log_dir}/\1 2>> ${log_dir}/\2#")

set -x
eval "pin -injection child -t $pin_dir/mica.so -- ${cmd_line}"

mv itypes_*.txt itypes_*.out mica.log $log_dir
