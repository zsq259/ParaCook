import json
import os
from turtle import update

from regex import F

max_time_dict = {}
min_time_dict = {}
# max_waiting_time_dict = {}
# min_waiting_time_dict = {}
max_moving_time_dict = {}
min_moving_time_dict = {}

def update_dict(d: dict, key, value, func):
    if key not in d:
        d[key] = value
    else:
        d[key] = func(d[key], value)

def collect_statistics(model: str, method: str, normalize: str|None, agent_nums: list|None=None, orders_nums: list|None=None, recipes: list|None=None) -> dict | None:
    max_retry_count = 0
    
    seeds = [42, 84, 126, 128, 256]
    if agent_nums is None:
        agent_nums = [1, 2, 3]
    if orders_nums is None:
        orders_nums = [1, 2, 3, 4]
    if recipes is None:
        recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]
    
    all_count = 0
    success_count = 0
    all_time = []
    all_time_rate = []
    agent_movements = []
    agent_movements_rate = []
    agent_waiting_times = []
    agent_utilizations = []
    
    for recipe in recipes:
        for seed in seeds:
            for agent_num in agent_nums:
                for orders_num in orders_nums:
                    result_path = f"results/{method}/{model}/{recipe}/seed_{seed}/agent_num_{agent_num}/orders_num_{orders_num}.json"
                    if os.path.exists(result_path):
                        with open(result_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            all_count += 1
                            if data["done"]:
                                success_count += 1
                                max_retry_count = max(max_retry_count, data.get("retry_count", 0))
                                key = (recipe, seed, agent_num, orders_num)
                                update_dict(max_time_dict, key, data["time"], max)
                                update_dict(min_time_dict, key, data["time"], min)
                                all_time.append(data["time"])

                                if normalize == "linear":
                                    max_time = max_time_dict[key]
                                    min_time = min_time_dict[key]
                                    all_time.append((data["time"] - min_time) / (max_time - min_time))
                                elif normalize == "ratio":
                                    min_time = min_time_dict[key]
                                    all_time_rate.append(data["time"] / min_time)

                                for name, time in data["agent_waiting_time"].items():
                                    # update_dict(max_waiting_time_dict, key, time, max)
                                    # update_dict(min_waiting_time_dict, key, time, min)
                                    agent_waiting_times.append(time)
                                    agent_utilizations.append((data["agent_all_execution_time"][name] - time) / data["agent_all_execution_time"][name] if data["agent_all_execution_time"][name] > 0 else 0)
                                for name, time in data["agent_moving_time"].items():
                                    if time != 0:
                                        update_dict(max_moving_time_dict, key, time, max)
                                        update_dict(min_moving_time_dict, key, time, min)
                                    agent_movements.append(time)
                                    if normalize == "linear":
                                        max_moving_time = max_moving_time_dict[key]
                                        min_moving_time = min_moving_time_dict[key]
                                        agent_movements.append((time - min_moving_time) / (max_moving_time - min_moving_time))
                                    elif normalize == "ratio":
                                        min_moving_time = min_moving_time_dict[key]
                                        agent_movements_rate.append(time / min_moving_time)
                    else:
                        # print(f"结果文件 {result_path} 不存在，跳过。")
                        pass
    # print("Max retry count:", max_retry_count)

    if all_count == 0:
        return None
    
    assert success_count == len(all_time)
    assert len(agent_movements) == len(agent_waiting_times) == len(agent_utilizations)
    return {
        "model": model,
        "method": method,
        "recipes": recipes,
        "success_count": success_count,
        "all_count": all_count,
        "success_rate": success_count / all_count,
        "all_time": sum(all_time),
        "all_movements": sum(agent_movements),
        "all_waiting_time": sum(agent_waiting_times),
        "avg_time_rate": sum(all_time_rate) / len(all_time_rate) if len(all_time_rate) > 0 else 0,
        "agent_avg_movements": sum(agent_movements) / len(agent_movements) if len(agent_movements) > 0 else 0,
        "agent_avg_movements_rate": sum(agent_movements_rate) / len(agent_movements_rate) if len(agent_movements_rate) > 0 else 0,
        "agent_avg_waiting_time": sum(agent_waiting_times) / len(agent_waiting_times) if len(agent_waiting_times) > 0 else 0,
        "agent_avg_utilization": sum(agent_utilizations) / len(agent_utilizations) if len(agent_utilizations) > 0 else 0
    }
    

if __name__ == "__main__":
    models = ["gpt-5", "gpt-5-2025-08-07", "gemini-2.5-pro", "claude-opus-4-1-20250805", "deepseek-reasoner", "qwen3-max-preview"]
    methods = ["IO", "CoT", "MultiStepReAct"]
    recipes = [["sashimi", "salad"], ["sushi", "burger"], ["pasta", "burrito"]]
    # recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]

    for model in models:
        for method in methods:
            for recipe in recipes:
                if not isinstance(recipe, list):
                    recipe = [recipe]
                collect_statistics(model, method, normalize=None, recipes=recipe)

    # print("Max time dict:")
    # for key, value in max_time_dict.items():
    #     print(f"{key}: {value}")
    # print("\nMin time dict:")
    # for key, value in min_time_dict.items():
    #     print(f"{key}: {value}")

    for model in models:
        for method in methods:
            all_count = 0
            success_count = 0
            for recipe in recipes:
                if not isinstance(recipe, list):
                    recipe = [recipe]
                result = collect_statistics(model, method, normalize="ratio", recipes=recipe)
                if not result:
                    continue
                if result:
                    all_count += result["all_count"]
                    success_count += result["success_count"]
                avg_time = result["all_time"] / result["success_count"] if result["success_count"] > 0 else 0
                avg_time_rate = result["avg_time_rate"]
                avg_agent_utilization = result["agent_avg_utilization"]
                avg_moving_time_rate = result["agent_avg_movements_rate"]
                print(f"Model: {model}, Method: {method}, Recipe: {recipe}, Count: {result.get('all_count', 0)}, Success: {result.get('success_count', 0)}, Success Rate: {result.get('success_rate', 0):.2f}")
                print(f"Average Time: {avg_time:.2f}, Average Time Rate: {avg_time_rate:.2f}, Average Agent Utilization: {avg_agent_utilization:.2f}, Average Moving Time: {avg_moving_time_rate:.2f}")
                
            print(f"Model: {model}, Method: {method}, Total Count: {all_count}, Total Success: {success_count}, Overall Success Rate: {success_count / all_count if all_count > 0 else 0:.2f}\n")