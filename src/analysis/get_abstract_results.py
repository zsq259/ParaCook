import os, json

def get_model_data(results_dir: str, model: str) -> dict:
    result_path = os.path.join(results_dir, f"{model}.json")
    if not os.path.exists(result_path):
        print(f"Result file {result_path} does not exist, skipping.")
        return {}
    with open(result_path, 'r') as f:
        results = json.load(f)
    return results

if __name__ == "__main__":
    results_dir = "results/abstract"
    cp_sat_data = get_model_data(results_dir, "cp_sat")
    models = ["cp_sat", "gpt-5", "gemini-2.5-pro", "deepseek-reasoner", "claude-opus-4-1-20250805", "qwen3-max-preview"]
    for model in models:
        model_data = get_model_data(results_dir, model)
        success_count = 0
        all_times = []
        time_rates = []
        for key, value in cp_sat_data.items():
            if not key in model_data:
                continue
            # if "agent_num_1" in key:
            #     continue
            # if "sashimi" in key or "salad" in key:
            #     continue
            cp_sat_result = value
            model_result = model_data[key]
            if model_result["done"]:
                success_count += 1
                all_times.append(model_result["time"])
                time_rates.append(model_result["time"] / cp_sat_result["time"])
            else:
                all_times.append(cp_sat_result["time"] * 1.2)
        total_count = len(model_data)
        success_rate = success_count / total_count if total_count > 0 else 0
        avg_time_rate = sum(time_rates) / len(time_rates) if len(time_rates) > 0 else 0
        avg_time = sum(all_times) / len(all_times) if len(all_times) > 0 else 0
        print(f"Model: {model}, Count: {total_count} Success Rate: {success_rate:.2f}, Average Time Rate: {avg_time_rate:.4f}, Average Time: {avg_time:.2f}")
        # print(f"Model: {model}, Success Rate: {success_rate:.2f}, Average Time Rate: {avg_time_rate:.4f}, Average Time: {avg_time:.2f}")
            