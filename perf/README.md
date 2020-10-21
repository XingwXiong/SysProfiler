# Perf

## Perf Stat

```bash
# system-wide collection
sudo perf stat -a -e r3c,rc0,rc4,r10b,r20b,r110 -r 1 sleep 5
sudo perf stat -e r3c,rc0,rc4,r10b,r20b,r110 -r 1 sleep 5
```

## Perf Mem

```bash
sudo perf mem -t load record sleep 1
sudo perf mem -D report | more
```

## Perf Lock

```bash
sudo perf lock record sleep 1
sudo perf lock -D report >1.log 2>2.log
```
