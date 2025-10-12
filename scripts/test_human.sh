
#!/bin/bash
# Capture Ctrl+C and kill all child processes
trap "echo 'kill all child processes'; kill 0; exit" SIGINT

# Please enter the model name as your name
MODELS=("name")
MOTHODS=("Human")

RECIPES=("sashimi" "salad" "sushi" "burger" "pasta" "burrito")
AGENT_NUMS=(2)
ORDERS_NUMS=(2)
SEEDS=(42)

MAX_JOBS=1
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
                                           --result-path $result_path &
                        ((job_count++))
                        if [[ $job_count -ge $MAX_JOBS ]]; then
                            wait -n
                            ((job_count--))
                        fi
                    done
                done
            done
        done
    done
done
wait