from src.utils.random_map import generate_random_map, print_map, load_json, check_reachability

import os
import random
import json

def generate_random_orders(recipe, num_orders, output_dir=None, seed=None) -> bool:
    recipe_dir = "config/recipe/" + recipe + ".json"
    all_recipes = load_json(recipe_dir)

    if seed is not None:
        random.seed(seed)
    
    selected_orders = random.choices(all_recipes, k=num_orders)
    order_names = [f"{recipe}/{r['name']}" for r in selected_orders]
    print("Selected Orders:", order_names)
    if output_dir is not None:
        for agent_num in range(1, 4):
            orders_path = output_dir + f"orders/agent_num_{agent_num}/orders_num_{num_orders}.yaml"
            os.makedirs(os.path.dirname(orders_path), exist_ok=True)
            with open(orders_path, 'w') as f:
                yaml_content = f"map: data/cook/{recipe}/seed_{seed}/maps/agent_num_{agent_num}\n"
                yaml_content += f"result_path: {recipe}/seed_{seed}/agent_num_{agent_num}/orders_num_{num_orders}\n"
                yaml_content += "orders:\n"
                for order in order_names:
                    yaml_content += f"  - {order}\n"
                f.write(yaml_content)
    return True


def generate_maps(recipe, num_agents, output_dir, seed=None) -> bool:
    recipe_dir = "config/recipe/" + recipe + ".json"
    all_recipes = load_json(recipe_dir)

    if seed is not None:
        random.seed(seed)
    
    order_names = [f"{recipe}/{r['name']}" for r in all_recipes]
    print("Selected Orders:", order_names)
    retry_count = 0
    map_data = None
    while retry_count < 5:
        map_data = generate_random_map(
            width=10,
            height=8,
            num_agents=num_agents,
            orders=order_names,
            recipe_dir="config/recipe",
            num_tables=4,
            num_plates=2,
            num_chopping_board=2,
            num_each_cookware=2,
            num_walls=2,
            seed=seed + retry_count if seed is not None else None
        )
        print_map(map_data)
        if check_reachability(map_data):
            break
        else:
            print("Map not fully reachable, regenerating...")
        map_data = None
        retry_count += 1
    if not map_data:
        print("Failed to generate a valid map after retries.")
        return False
    map_path = output_dir + f"maps/agent_num_{num_agents}.json"
    os.makedirs(os.path.dirname(map_path), exist_ok=True)
    with open(map_path, 'w') as f:
        json.dump(map_data, f, indent=4)
    return True


def main():
    # 示例调用
    # generate_test_cases(recipe="salad", num_agents=2, output_dir="data/cook", seed=41)
    seeds = [42, 84, 126, 128, 256]
    recipe_cates = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]
    # recipe_cates = ["burger"]
    for recipe in recipe_cates:
        for seed in seeds:
            for num_agents in range(1, 4):
                print(f"Generating map for {num_agents} agents with seed {seed}")
                done = generate_maps(recipe=recipe, num_agents=num_agents, output_dir=f"data/cook/{recipe}/seed_{seed}/", seed=seed)
                if not done:
                    raise ValueError("Failed to generate a valid map after retries.")
            for num_orders in range(1, 5):
                print(f"Generating orders for {num_orders} orders with seed {seed}")
                done = generate_random_orders(recipe=recipe, num_orders=num_orders, output_dir=f"data/cook/{recipe}/seed_{seed}/", seed=seed)
                if not done:
                    raise ValueError("Failed to generate orders.")

if __name__ == "__main__":
    main()