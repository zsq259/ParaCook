# Group statistics by agent_num and orders_num

import json
import os
from src.analysis.compute_sequencial_time import compute_order_time_and_movements, get_dish_time_and_movements


def analyze_by_agent_num(models, methods, agent_nums, orders_nums, recipes, orders_data, dish_time_and_movements):
    seeds = [42]
    for model in models:
        for method in methods:
            for agent_num in agent_nums:
                all_count = 0
                success_count = 0
                all_time = []
                all_time_rate = []
                agent_movements = []
                agent_utilizations = []
                for orders_num in orders_nums:
                    for recipe in recipes:
                        for seed in seeds:
                            result_path = f"results/{method}/{model}/{recipe}/seed_{seed}/agent_num_{agent_num}/orders_num_{orders_num}.json"
                            if os.path.exists(result_path):
                                with open(result_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    all_count += 1
                                    orders = orders_data[f"{recipe}/seed_{seed}/orders_num_{orders_num}"]
                                    sequencial_time, sequencial_movements = compute_order_time_and_movements(orders, dish_time_and_movements)
                                    if data["done"]:
                                        success_count += 1
                                        all_time.append(data["time"])
                                        all_time_rate.append(data["time"] / sequencial_time if sequencial_time > 0 else 0)
                                        for name, time in data["agent_waiting_time"].items():
                                            agent_utilizations.append((data["agent_all_execution_time"][name] - time) / data["agent_all_execution_time"][name] if data["agent_all_execution_time"][name] > 0 else 0)
                                        for name, time in data["agent_moving_time"].items():
                                            agent_movements.append(time)
                                    else:
                                        all_time.append(sequencial_time)
                                        # all_time_rate.append(1.0)
                                        for name, time in data["agent_moving_time"].items():
                                            agent_movements.append(sequencial_movements / agent_num)
                # Output statistics for each agent_num
                success_rate = success_count / all_count if all_count > 0 else 0
                avg_time = sum(all_time) / len(all_time) if len(all_time) > 0 else 0
                avg_time_rate = sum(all_time_rate) / len(all_time_rate) if len(all_time_rate) > 0 else 0
                avg_agent_utilization = sum(agent_utilizations) / len(agent_utilizations) if len(agent_utilizations) > 0 else 0
                avg_agent_movements = sum(agent_movements) / len(agent_movements) if len(agent_movements) > 0 else 0
                if all_count > 0:
                    print(f"{model} {method} Agent_num: {agent_num}, Success_rate: {success_rate:.4f}, Avg_pOCT: {avg_time:.2f}, Avg_nOCT: {avg_time_rate:.4f}, pMD: {avg_agent_movements:.2f}, AU: {avg_agent_utilization:.4f}")

# New: Group statistics by orders_num

def analyze_by_orders_num(models, methods, agent_nums, orders_nums, recipes, orders_data, dish_time_and_movements):
    seeds = [42]
    for model in models:
        for method in methods:
            for orders_num in orders_nums:
                all_count = 0
                success_count = 0
                all_time = []
                all_time_rate = []
                agent_movements = []
                agent_utilizations = []
                for agent_num in agent_nums:
                    for recipe in recipes:
                        for seed in seeds:
                            result_path = f"results/{method}/{model}/{recipe}/seed_{seed}/agent_num_{agent_num}/orders_num_{orders_num}.json"
                            if os.path.exists(result_path):
                                with open(result_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    all_count += 1
                                    orders = orders_data[f"{recipe}/seed_{seed}/orders_num_{orders_num}"]
                                    sequencial_time, sequencial_movements = compute_order_time_and_movements(orders, dish_time_and_movements)
                                    if data["done"]:
                                        success_count += 1
                                        all_time.append(data["time"])
                                        all_time_rate.append(data["time"] / sequencial_time if sequencial_time > 0 else 0)
                                        for name, time in data["agent_waiting_time"].items():
                                            agent_utilizations.append((data["agent_all_execution_time"][name] - time) / data["agent_all_execution_time"][name] if data["agent_all_execution_time"][name] > 0 else 0)
                                        for name, time in data["agent_moving_time"].items():
                                            agent_movements.append(time)
                                    else:
                                        all_time.append(sequencial_time)
                                        # all_time_rate.append(1.0)
                                        for name, time in data["agent_moving_time"].items():
                                            agent_movements.append(sequencial_movements / agent_num)
                # Output statistics for each orders_num
                success_rate = success_count / all_count if all_count > 0 else 0
                avg_time = sum(all_time) / len(all_time) if len(all_time) > 0 else 0
                avg_time_rate = sum(all_time_rate) / len(all_time_rate) if len(all_time_rate) > 0 else 0
                avg_agent_utilization = sum(agent_utilizations) / len(agent_utilizations) if len(agent_utilizations) > 0 else 0
                avg_agent_movements = sum(agent_movements) / len(agent_movements) if len(agent_movements) > 0 else 0
                if all_count > 0:
                    # print(f"{model} {method} Orders_num: {orders_num}, Success_rate: {success_rate:.4f}, Avg_time: {avg_time:.2f}, Avg_time_rate: {avg_time_rate:.4f}, Agent_avg_movements: {avg_agent_movements:.2f}, Agent_avg_utilization: {avg_agent_utilization:.4f}")
                    print(f"{model} {method} Orders_num: {orders_num}, Success_rate: {success_rate:.4f}, Avg_pOCT: {avg_time:.2f}, Avg_nOCT: {avg_time_rate:.4f}, pMD: {avg_agent_movements:.2f}, AU: {avg_agent_utilization:.4f}")



if __name__ == "__main__":
    models = ["gpt-5", "gemini-2.5-pro", "deepseek-reasoner", "claude-opus-4-1-20250805", "qwen3-max-preview"]
    methods = ["IO", "CoT"]
    agent_nums = [1, 2, 3]
    orders_nums = [1, 2, 3, 4]
    recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]
    orders_path = "data/cook/orders/all_orders.json"
    with open(orders_path, 'r') as f:
        orders_data = json.load(f)
    dish_time_and_movements = get_dish_time_and_movements()
    print("===== Group statistics by agent_num =====")
    analyze_by_agent_num(models, methods, agent_nums, orders_nums, recipes, orders_data, dish_time_and_movements)
    print("\n===== Group statistics by orders_num =====")
    analyze_by_orders_num(models, methods, agent_nums, orders_nums, recipes, orders_data, dish_time_and_movements)