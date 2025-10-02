import json
import os

def get_results(model: str, method: str, agent_nums: list|None=None, orders_nums: list|None=None, recipes: list|None=None):
    
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
    all_time = 0
    agent_movements = []
    agent_waiting_times = []
    
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
                            all_time += data["time"]
                            for name, time in data["agent_waiting_time"].items():
                                agent_waiting_times.append(time)
                            for name, time in data["agent_moving_time"].items():
                                agent_movements.append(time)
                    else:
                        # print(f"结果文件 {result_path} 不存在，跳过。")
                        pass
    print("Max retry count:", max_retry_count)

    if all_count == 0:
        return {}
    return {
        "model": model,
        "method": method,
        "recipes": recipes,
        "success_count": success_count,
        "all_count": all_count,
        "success_rate": success_count / all_count,
        "all_time": all_time,
        "all_movements": sum(agent_movements),
        "all_waiting_time": sum(agent_waiting_times),
        "agent_avg_movements": sum(agent_movements) / len(agent_movements),
        "agent_avg_waiting_time": sum(agent_waiting_times) / len(agent_waiting_times)
    }
    

if __name__ == "__main__":
    # result = get_results("gemini-2.5-pro", "CoT")
    # print(result)
    # print("success rate:", result["success_count"] / result["all_count"])
    # print("average time:", result["all_time"] / result["all_count"])
    # print("average movements:", result["agent_avg_movements"])
    # print("average waiting time:", result["agent_avg_waiting_time"])
    # print("total movements:", result["all_movements"])
    # print("total waiting time:", result["all_waiting_time"])
    results = []
    models = ["gpt-5", "gemini-2.5-pro"]
    # models = ["claude-opus-4-1-20250805"]
    # methods = ["IO", "CoT"]
    methods = ["IO", "CoT", "MultiStepReAct"]
    recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]
    for model in models:
        for method in methods:
            for recipe in recipes:
                result = get_results(model, method, recipes=[recipe])
                if result:
                    print(result)
                    results.append(result)
                    print("success rate:", result["success_count"] / result["all_count"])
                    print("average time:", result["all_time"] / result["all_count"])
                    print("average movements:", result["agent_avg_movements"])
                    print("average waiting time:", result["agent_avg_waiting_time"])
                    print("total movements:", result["all_movements"])
                    print("total waiting time:", result["all_waiting_time"])
                    print("====================================")
                else:
                    print(f"No results for model {model}, method {method}, recipe {recipe}")
    
    with open("results/summary.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)