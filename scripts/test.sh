
#!/bin/bash
# Capture Ctrl+C and kill all child processes
trap "echo 'kill all child processes'; kill 0; exit" SIGINT

BATCH_TIME=$(date +"%H-%M")

MODELS=(
    "gpt-5"
    "gemini-2.5-pro"
    "claude-opus-4-1-20250805"
    "DeepSeek-V3.1"
    "qwen3-max-preview"
)
MOTHODS=("IO" "CoT")

RECIPES=("sashimi" "salad" "sushi" "burger" "pasta" "burrito")
AGENT_NUMS=(1 2 3)
ORDERS_NUMS=(1 2 3 4)
SEEDS=(42 84 126 128 256)

MAX_JOBS=8
job_count=0

for MODEL in "${MODELS[@]}"; do
    for METHOD in "${MOTHODS[@]}"; do
        for SEED in "${SEEDS[@]}"; do
            for RECIPE in "${RECIPES[@]}"; do
                for AGENT_NUM in "${AGENT_NUMS[@]}"; do
                    for ORDERS_NUM in "${ORDERS_NUMS[@]}"; do
                        # Read orders from data/cook/orders/all_orders.json
                        order_name="${RECIPE}/seed_${SEED}/orders_num_${ORDERS_NUM}"
                        orders=$(jq -r --arg name "$order_name" '.[$name][]' data/cook/orders/all_orders.json)
                        orders=$(echo "$orders" | tr '\n' ' ')

                        map="data/cook/maps/${RECIPE}/seed_${SEED}/agent_num_${AGENT_NUM}"
                        result_path="${RECIPE}/seed_${SEED}/agent_num_${AGENT_NUM}/orders_num_${ORDERS_NUM}"

                        python -m src.main --model $MODEL \
                                           --agent $METHOD \
                                           --map $map \
                                           --orders $orders \
                                           --result-path $result_path \
                                           --batch-log-id $BATCH_TIME &
                        ((job_count++))
                        if [[ $job_count -ge $MAX_JOBS ]]; then
                            wait -n  # Wait for any job to finish
                            ((job_count--))
                        fi
                    done
                done
            done
        done
    done
done
wait