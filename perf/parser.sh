#!/bin/bash
cur_dir=$(cd `dirname $0`; pwd)
bench_list=(505.mcf_r  507.cactuBSSN_r  523.xalancbmk_r  531.deepsjeng_r  544.nab_r  549.fotonik3d_r)
export PYTHONPATH=$cur_dir/../:$PYTHONPATH

# 生成解析的 csv 文件
for bench_name in ${bench_list[@]}
do
    log_dir=/usr/local/cpu2017/benchspec/CPU/scripts/results/$bench_name/perf
    ls $log_dir/*.err
    if [ $? -ne 0 ]; then
        continue
    fi
    echo "==> $bench_name perf stat<=="
    python3 $cur_dir/perf_parser.py -i $(ls $log_dir/*.err) -o $log_dir/perf.stat.csv

    echo "==> $bench_name perf mem<=="
    eval "echo xingw.xiong | sudo -S chmod 644 ${log_dir}/perf.data"
    cd $log_dir && eval "/usr/bin/perf mem -D -x , report > ${log_dir}/perf.mem.log" && cd -
    python3 $cur_dir/perf_parser.py -i ${log_dir}/perf.mem.log -o $log_dir/perf.mem.csv -t mem

done

# 汇总结果
echo "benchname",$(head -n 1 $log_dir/perf.stat.csv),$(head -n 1 $log_dir/perf.mem.csv)
for bench_name in ${bench_list[@]}
do
    log_dir=/usr/local/cpu2017/benchspec/CPU/scripts/results/$bench_name/perf
    echo $bench_name,$(tail -n 1 $log_dir/perf.stat.csv),$(tail -n 1 $log_dir/perf.mem.csv)
done
