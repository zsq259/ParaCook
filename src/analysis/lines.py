import json
import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from src.analysis.compute_sequencial_time import compute_order_time_and_movements, get_dish_time_and_movements

def collect_data_by_group(
    models, methods, agent_nums, orders_nums, recipes, orders_data, dish_time_and_movements,
    group_by="agent_nums"
):
    """
    General data collection function, can be grouped by agent_nums or orders_nums.
    group_by: "agent_nums" or "orders_nums"
    """
    results = {}
    seeds = [42]
    if group_by == "agent_nums":
        outer_list = agent_nums
        inner_list = orders_nums
        outer_key = "agent_nums"
    elif group_by == "orders_nums":
        outer_list = orders_nums
        inner_list = agent_nums
        outer_key = "orders_nums"
    else:
        raise ValueError("group_by must be 'agent_nums' or 'orders_nums'")

    for model in models:
        for method in methods:
            key = f"{model}_{method}"
            results[key] = {
                outer_key: outer_list,
                'success_rates': [],
                'avg_times': [],
                'avg_time_rates': [],
                'avg_movements': [],
                'avg_utilizations': []
            }
            for outer in outer_list:
                all_count = 0
                success_count = 0
                all_time = []
                all_time_rate = []
                agent_movements = []
                agent_utilizations = []
                for inner in inner_list:
                    for recipe in recipes:
                        for seed in seeds:
                            if group_by == "agent_nums":
                                agent_num = outer
                                orders_num = inner
                            else:
                                agent_num = inner
                                orders_num = outer
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
                                        for name, time in data["agent_moving_time"].items():
                                            agent_movements.append(sequencial_movements / agent_num)

                success_rate = success_count / all_count if all_count > 0 else 0
                avg_time = sum(all_time) / len(all_time) if len(all_time) > 0 else 0
                avg_time_rate = sum(all_time_rate) / len(all_time_rate) if len(all_time_rate) > 0 else 0
                avg_utilization = sum(agent_utilizations) / len(agent_utilizations) if len(agent_utilizations) > 0 else 0
                avg_movement = sum(agent_movements) / len(agent_movements) if len(agent_movements) > 0 else 0
                assert len(all_time) > 0 and len(agent_movements) > 0
                if success_rate == 0:
                    results[key]['success_rates'].append(0)
                    results[key]['avg_times'].append(avg_time)
                    results[key]['avg_time_rates'].append(None)
                    results[key]['avg_movements'].append(avg_movement)
                    results[key]['avg_utilizations'].append(None)
                else:
                    results[key]['success_rates'].append(success_rate * 100)
                    results[key]['avg_times'].append(avg_time)
                    results[key]['avg_time_rates'].append(avg_time_rate)
                    results[key]['avg_movements'].append(avg_movement)
                    results[key]['avg_utilizations'].append(avg_utilization * 100)
    return results


def plot_performance_analysis(agent_data, orders_data, output_path='agent_order_num_lines.pdf'):
    """Plot performance analysis charts with 2 rows and 5 columns"""
    
    plt.rcParams['font.size'] = 26
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.linewidth'] = 1.2
    
    # Define models and methods
    models = ["gpt-5", "gemini-2.5-pro", "deepseek-reasoner", "claude-opus-4-1-20250805", "qwen3-max-preview"]
    methods = ["IO", "CoT"]
    
    # Define colors and line styles
    model_colors = {
        "gpt-5": "#10b981",          # Green
        "gemini-2.5-pro": "#3b82f6", # Blue
        "deepseek-reasoner": "#f59e0b", # Orange
        "claude-opus-4-1-20250805": "#ef4444", # Red
        "qwen3-max-preview": "#6b7280"  # Gray
    }
    
    method_linestyles = {
        "CoT": "-",   # Solid line
        "IO": "--"    # Dashed line
    }
    

    # Create figure: 2 rows, 5 columns
    fig, axes = plt.subplots(2, 5, figsize=(28, 11))
    fig.subplots_adjust(left=0.04, right=0.99, top=0.88, bottom=0.09, hspace=0.45, wspace=0.55)  # Increase spacing to prevent overlap
    
    # Metric titles
    metrics = [
        ('success_rates', 'Success Rate (%)'),
        ('avg_times', 'Avg Time (steps)'),
        ('avg_time_rates', 'Time Rate'),
        ('avg_movements', 'Avg Movements'),
        ('avg_utilizations', 'Utilization (%)')
    ]
    
    # First row: by number of agents
    for col, (metric_key, metric_title) in enumerate(metrics):
        ax = axes[0, col]
        for model in models:
            for method in methods:
                key = f"{model}_{method}"
                if key in agent_data:
                    x = agent_data[key]['agent_nums']
                    y = agent_data[key][metric_key]
                    ax.plot(x, y, 
                           color=model_colors[model], 
                           linestyle=method_linestyles[method],
                           linewidth=2,
                           marker='o',
                           markersize=8,
                           label=f"{model}_{method}")
        ax.set_xlabel('Number of Agents', fontsize=31)
        ax.set_ylabel(metric_title, fontsize=31)
        ax.set_xticks([1, 2, 3])
        ax.tick_params(axis='x', labelsize=26)
        ax.tick_params(axis='y', labelsize=26)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_title(f'(a{col+1})', fontsize=34, pad=19)
    
    # Second row: by number of orders
    for col, (metric_key, metric_title) in enumerate(metrics):
        ax = axes[1, col]
        for model in models:
            for method in methods:
                key = f"{model}_{method}"
                if key in orders_data:
                    x = orders_data[key]['orders_nums']
                    y = orders_data[key][metric_key]
                    ax.plot(x, y, 
                           color=model_colors[model], 
                           linestyle=method_linestyles[method],
                           linewidth=2,
                           marker='o',
                           markersize=8,
                           label=f"{model}_{method}")
        ax.set_xlabel('Number of Orders', fontsize=31)
        ax.set_ylabel(metric_title, fontsize=31)
        ax.set_xticks([1, 2, 3, 4])
        ax.tick_params(axis='x', labelsize=26)
        ax.tick_params(axis='y', labelsize=26)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_title(f'(b{col+1})', fontsize=34, pad=19)
    
    # Create unified legend (placed at the top)
    handles = []
    labels = []
    for model in models:
        for method in methods:
            line = Line2D([0], [0], 
                            color=model_colors[model], 
                            linestyle=method_linestyles[method],
                            linewidth=3,  # Increase line width
                            marker='',  # Remove marker, show only lines
                            markersize=0)
            # Simplify model names
            model_short = model.replace("claude-opus-4-1-20250805", "claude").replace("gemini-2.5-pro", "gemini").replace("deepseek-reasoner", "deepseek").replace("qwen3-max-preview", "qwen")
            handles.append(line)
            labels.append(f"{model_short} {method}")
    
    # Display legend in two rows
    fig.legend(handles, labels, 
              loc='upper center', 
              ncol=5,
              bbox_to_anchor=(0.5, 1.09),  # Legend closer to top
              frameon=True,
              fontsize=29,  # Larger font
              columnspacing=1.8,  # Increase column spacing
              handlelength=2.4,  # Increase legend line length
              handleheight=1)  # Increase legend line height
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")
    plt.close()


if __name__ == "__main__":
    models = ["gpt-5", "gemini-2.5-pro", "deepseek-reasoner", "claude-opus-4-1-20250805", "qwen3-max-preview"]
    methods = ["IO", "CoT"]
    agent_nums = [1, 2, 3]
    orders_nums = [1, 2, 3, 4]
    recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]
    
    # Read order data
    orders_path = "data/cook/orders/all_orders.json"
    with open(orders_path, 'r') as f:
        orders_data = json.load(f)
    
    dish_time_and_movements = get_dish_time_and_movements()
    
    print("Collecting data grouped by number of agents...")
    agent_data = collect_data_by_group(models, methods, agent_nums, orders_nums, recipes, orders_data, dish_time_and_movements, group_by="agent_nums")
    
    print("Collecting data grouped by number of orders...")
    orders_data_collected = collect_data_by_group(models, methods, agent_nums, orders_nums, recipes, orders_data, dish_time_and_movements, group_by="orders_nums")
    
    print("Starting plotting...")
    plot_performance_analysis(agent_data, orders_data_collected, output_path='agent_order_num_lines.pdf')
    print("Complete!")