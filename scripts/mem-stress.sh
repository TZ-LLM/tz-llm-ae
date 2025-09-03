setup=$1
stress=$2
cache=$3
len=$4
model=$5
n=$6

/data/local/tmp/rknpu/set-npu-irq.sh $setup

mount /dev/block/nvme0n1p1 /data/ssd/ && mkdir /dev/shm
sleep 5

set -e

model_path=""
bytes=""
if [ "$model" = "tinyllama" ]; then
    model_path="/data/ssd/tinyllama-1.1b-chat-v1.0.Q8_0.gguf"
    bytes="13312M"
elif [ "$model" = "gemma" ]; then
    model_path="/data/ssd/gemma-2-2b-it-Q8_0.gguf"
    bytes="12288M"
elif [ "$model" = "qwen" ]; then
    model_path="/data/ssd/qwen2.5-3b-instruct-q8_0.gguf"
    bytes="11264M"
elif [ "$model" = "phi" ]; then
    model_path="/data/ssd/Phi-3-mini-4k-instruct.Q8_0.gguf"
    bytes="10240M"
elif [ "$model" = "llama" ]; then
    model_path="/data/ssd/Meta-Llama-3-8B-Instruct.Q8_0.gguf"
    bytes="6144M"
else
    echo "invalid model $model"
    exit 1
fi

if [ "$stress" = "s" ]; then
    echo "Running stress-ng with $bytes..."
    mkdir -p /data/local/tmp/stress-ng
    LD_LIBRARY_PATH=/data/local/tmp/rknpu/ /data/local/tmp/rknpu/ld-linux-aarch64.so.1 /data/local/tmp/rknpu/stress-ng -m 1 --vm-keep --vm-bytes $bytes -t 800s --temp-path /data/local/tmp/stress-ng --taskset 3 &
    # n="1"
else
    echo "no stress-ng"
fi

sleep 15

if [ "$setup" = "base" ]; then
    echo "Running baseline..."
    echo "111: $model#$len"
    LD_LIBRARY_PATH=/data/local/tmp/rknpu/ /data/local/tmp/rknpu/ld-linux-aarch64.so.1 /data/local/tmp/rknpu/llama-cli --no-warmup -m $model_path -p "$model#$len" -n $n --cache $cache -s 1 -ngl 100 -t 4 --no-mmap -c 1124
elif [ "$setup" = "tz" ]; then
    echo "Running TZ-LLM..."
    LD_LIBRARY_PATH=/data/local/tmp/rknpu/ /data/local/tmp/rknpu/ld-linux-aarch64.so.1 /data/local/tmp/rknpu/fake -c $cache -l $len -m $model -n $n -s 0
elif [ "$setup" = "strawman" ]; then
    echo "Running Strawman..."
    LD_LIBRARY_PATH=/data/local/tmp/rknpu/ /data/local/tmp/rknpu/ld-linux-aarch64.so.1 /data/local/tmp/rknpu/fake -c $cache -l $len -m $model -n $n -s 1
else
    echo "invalid setup $setup"
    exit 1
fi

wait
