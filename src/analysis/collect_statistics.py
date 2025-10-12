import json
import os

from src.analysis.compute_sequencial_time import compute_order_time_and_movements, get_dish_time_and_movements

def collect_statistics(model: str, method: str, orders_data: dict, dish_time_and_movements:dict, agent_nums: list|None=None, orders_nums: list|None=None, recipes: list|None=None) -> dict | None:
    max_retry_count = 0
    
    seeds = [42, 84, 126, 128, 256]
    # seeds = [42]
    if agent_nums is None:
        agent_nums = [1, 2, 3]
        # agent_nums = [2]
    if orders_nums is None:
        orders_nums = [1, 2, 3, 4]
        # orders_nums = [2]
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

                            orders = orders_data[f"{recipe}/seed_{seed}/orders_num_{orders_num}"]
                            sequencial_time, sequencial_movements = compute_order_time_and_movements(orders, dish_time_and_movements)

                            if data["done"]:
                                success_count += 1
                                max_retry_count = max(max_retry_count, data.get("retry_count", 0))
                                all_time.append(data["time"])
                                all_time_rate.append(data["time"] / sequencial_time if sequencial_time > 0 else 0)
                                for name, time in data["agent_waiting_time"].items():
                                    agent_waiting_times.append(time)
                                    agent_utilizations.append((data["agent_all_execution_time"][name] - time) / data["agent_all_execution_time"][name] if data["agent_all_execution_time"][name] > 0 else 0)
                                for name, time in data["agent_moving_time"].items():
                                    agent_movements.append(time)
                                
                            else:
                                all_time.append(sequencial_time)
                                # all_time_rate.append(1.0)
                                for name, time in data["agent_moving_time"].items():
                                    agent_movements.append(sequencial_movements / agent_num)
                    else:
                        pass
    # print("Max retry count:", max_retry_count)

    if all_count == 0:
        return None
    
    # assert success_count == len(all_time)
    assert len(agent_waiting_times) == len(agent_utilizations)
    return {
        "model": model,
        "method": method,
        "recipes": recipes,
        "success_count": success_count,
        "all_count": all_count,
        "success_rate": success_count / all_count,
        "all_time": sum(all_time),
        "all_avg_time": sum(all_time) / len(all_time) if len(all_time) > 0 else 0,
        "all_movements": sum(agent_movements),
        "all_waiting_time": sum(agent_waiting_times),
        "avg_time_rate": sum(all_time_rate) / len(all_time_rate) if len(all_time_rate) > 0 else 0,
        "agent_avg_movements": sum(agent_movements) / len(agent_movements) if len(agent_movements) > 0 else 0,
        "agent_avg_movements_rate": sum(agent_movements_rate) / len(agent_movements_rate) if len(agent_movements_rate) > 0 else 0,
        "agent_avg_waiting_time": sum(agent_waiting_times) / len(agent_waiting_times) if len(agent_waiting_times) > 0 else 0,
        "agent_avg_utilization": sum(agent_utilizations) / len(agent_utilizations) if len(agent_utilizations) > 0 else 0
    }
    

if __name__ == "__main__":
    # models = ["gpt-5", "gpt-5-2025-08-07", "gemini-2.5-pro", "claude-opus-4-1-20250805", "deepseek-reasoner", "qwen3-max-preview"]
    models = ["gpt-5", "gpt-5-2025-08-07", "gemini-2.5-pro", "deepseek-reasoner", "claude-opus-4-1-20250805", "qwen3-max-preview"]
    # models = ["pr", "gpt-5", "gemini-2.5-pro", "deepseek-reasoner"]
    methods = ["IO", "CoT", "MultiStepReAct"]
    # methods = ["IO", "CoT", "Human"]
    # recipes = [["sashimi", "salad"], ["sushi", "burger"], ["pasta", "burrito"]]
    recipes = [["sashimi", "salad"], ["pasta", "burrito"], ["sushi", "burger"]]
    # recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]

    orders_path = "data/cook/orders/all_orders.json"
    with open(orders_path, 'r') as f:
        orders_data = json.load(f)

    dish_time_and_movements = get_dish_time_and_movements()

    for model in models:
        for method in methods:
            all_count = 0
            success_count = 0

            output_line = ""
            for recipe in recipes:
                if not isinstance(recipe, list):
                    recipe = [recipe]
                result = collect_statistics(model, method, orders_data, dish_time_and_movements, recipes=recipe)
                if not result:
                    continue
                if result:
                    all_count += result["all_count"]
                    success_count += result["success_count"]
                avg_time = result["all_avg_time"]
                avg_time_rate = result["avg_time_rate"]
                avg_agent_utilization = result["agent_avg_utilization"]
                agent_avg_movements = result["agent_avg_movements"]

                output_line += f"{result.get('success_rate', 0):.4f} & {avg_time:.2f} & {avg_time_rate:.4f} & {agent_avg_movements:.2f} & {avg_agent_utilization:.4f} & "
                print(f"Model: {model}, Method: {method}, Recipe: {recipe}, Count: {result.get('all_count', 0)}, Success: {result.get('success_count', 0)}, Success Rate: {result.get('success_rate', 0):.4f}")
                print(f"Average Time: {avg_time:.2f}, Average Time Rate: {avg_time_rate:.4f}, Average Agent Utilization: {avg_agent_utilization:.4f}, Average Moving Time: {agent_avg_movements:.2f}")
            if len(output_line) > 0:
                # print(model, method, output_line)
                print(f"Model: {model}, Method: {method}, Total Count: {all_count}, Total Success: {success_count}, Overall Success Rate: {success_count / all_count if all_count > 0 else 0:.2f}\n")