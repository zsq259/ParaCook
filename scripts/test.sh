
#!/bin/bash
# 捕获 Ctrl+C，杀死所有子进程
trap "echo '终止所有子进程'; kill 0; exit" SIGINT

MODELS=(
    # "gpt-5"
    # "gpt-4.1"
    # "gemini-2.5-pro"
    # "claude-opus-4-1-20250805"
    "DeepSeek-V3.1"
)
MOTHODS=("IO" "CoT")

RECIPES=("sashimi" "salad" "sushi" "burger" "pasta" "burrito")
# RECIPES=("pasta" "burrito")
AGENT_NUMS=(1 2 3)
ORDERS_NUMS=(1 2 3 4)
SEEDS=(42 84 126 128 256)
# SEEDS=(42)

MAX_JOBS=8
job_count=0

for MODEL in "${MODELS[@]}"; do
    for METHOD in "${MOTHODS[@]}"; do
        for SEED in "${SEEDS[@]}"; do
            for RECIPE in "${RECIPES[@]}"; do
                for AGENT_NUM in "${AGENT_NUMS[@]}"; do
                    for ORDERS_NUM in "${ORDERS_NUMS[@]}"; do
                        # 从 data/cook/orders/all_orders.json 读取订单
                        order_name="${RECIPE}/seed_${SEED}/orders_num_${ORDERS_NUM}"
                        orders=$(jq -r --arg name "$order_name" '.[$name][]' data/cook/orders/all_orders.json)
                        orders=$(echo "$orders" | tr '\n' ' ')
                        # echo "订单列表: $orders"

                        map="data/cook/maps/${RECIPE}/seed_${SEED}/agent_num_${AGENT_NUM}"
                        result_path="${RECIPE}/seed_${SEED}/agent_num_${AGENT_NUM}/orders_num_${ORDERS_NUM}"

                        echo "运行测试: 模型=$MODEL, 方法=$METHOD, 地图=$map, 订单数=$ORDERS_NUM, 订单列表=[$orders], 结果路径=$result_path"

                        python -m src.main --model $MODEL \
                                           --agent $METHOD \
                                           --map $map \
                                           --orders $orders \
                                           --result-path $result_path &
                        ((job_count++))
                        if [[ $job_count -ge $MAX_JOBS ]]; then
                            wait -n  # 等待任意一个任务结束
                            ((job_count--))
                        fi
                    done
                done
            done
        done
    done
done
wait