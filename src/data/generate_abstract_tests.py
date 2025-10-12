from calendar import c
import json
import random
import os
from typing import final

from matplotlib import category

from src.game.const import *


def generate_abstract_test(orders: dict, seed: int, recipe_dict: dict, output_dir: str):
    random.seed(seed)
    subtasks = []
    count = 1
    final_dishes = []
    category = ""
    for order in orders:
        cate, name = order.split('/')
        category = cate
        recipe_data = recipe_dict[name]
        final_ingredients = []
        for ingredient in recipe_data['ingredients']:
            if ingredient['state'] == 'raw':
                # pick up raw ingredient
                subtasks.append({
                    "name": f"subtask{count}",
                    "time": random.randint(1, 18),
                    "dependencies": {}
                })
                final_ingredients.append((count, 0))
                count += 1
            elif ingredient['state'] == 'chopped':
                # pick up raw ingredient
                subtasks.append({
                    "name": f"subtask{count}",
                    "time": random.randint(1, 18),
                    "dependencies": {}
                })
                raw_id = count
                count += 1
                # move to chopping board
                subtasks.append({
                    "name": f"subtask{count}",
                    "time": random.randint(1, 18),
                    "dependencies": {f"subtask{raw_id}": 0}
                })
                chop_id = count
                count += 1
                # chop
                subtasks.append({
                    "name": f"subtask{count}",
                    "time": PROCESS_CUT_TIME,
                    "dependencies": {f"subtask{chop_id}": 0}
                })
                final_ingredients.append((count, 0))
                count += 1
            elif ingredient['state'] == 'cooked':
                # pick up raw ingredient
                subtasks.append({
                    "name": f"subtask{count}",
                    "time": random.randint(1, 18),
                    "dependencies": {}
                })
                raw_id = count
                count += 1
                cook_time = 0
                if ingredient["item"] in ["meat", "chicken", "mushroom", "tomato", "fish", "prawn"]: # need chopping first
                    # move to chopping board
                    subtasks.append({
                        "name": f"subtask{count}",
                        "time": random.randint(1, 18),
                        "dependencies": {f"subtask{raw_id}": 0}
                    })
                    chop_id = count
                    count += 1
                    # chop
                    subtasks.append({
                        "name": f"subtask{count}",
                        "time": PROCESS_CUT_TIME,
                        "dependencies": {f"subtask{chop_id}": 0}
                    })
                    chopped_id = count
                    count += 1
                    cook_time = PROCESS_PAN_COOK_TIME
                elif ingredient["item"] in ["rice", "pasta"]: # no need chopping
                    chopped_id = raw_id
                    cook_time = PROCESS_POT_COOK_TIME
                else:
                    raise ValueError(f"Unknown ingredient item: {ingredient['item']}")
                # move to cooking station and put in pan/pot
                subtasks.append({
                    "name": f"subtask{count}",
                    "time": random.randint(1, 18),
                    "dependencies": {f"subtask{chopped_id}": 0}
                })
                cook_id = count
                final_ingredients.append((count, cook_time))
                count += 1
        # plate and serve
        subtasks.append({
            "name": f"subtask{count}",
            "time": random.randint(1, 18) * len(final_ingredients),
            "dependencies": {f"subtask{id[0]}": id[1] for id in final_ingredients}
        })
        final_dishes.append(count)
        count += 1
    clean_plates = []
    for i in range(0, len(orders) - 2):
        # pick dirty plate
        subtasks.append({
            "name": f"subtask{count}",
            "time": random.randint(1, 18),
            "dependencies": {f"subtask{final_dishes[i]}": RETURN_DIRTY_PLATE_TIME}
        })
        dirty_id = count
        count += 1
        # move to sink
        subtasks.append({
            "name": f"subtask{count}",
            "time": random.randint(1, 18),
            "dependencies": {f"subtask{dirty_id}": 0}
        })
        sink_id = count
        count += 1
        # wash
        subtasks.append({
            "name": f"subtask{count}",
            "time": PROCESS_WASH_PLATE_TIME,
            "dependencies": {f"subtask{sink_id}": 0}
        })
        clean_plates.append(count)
        count += 1
    
    for i in range(2, len(orders)):
        for subtask in subtasks:
            if subtask['name'] == f"subtask{final_dishes[i]}":
                subtask['dependencies'][f"subtask{clean_plates[i-2]}"] = 0
    
    output_path = os.path.join(output_dir, category, f"seed_{seed}", f"orders_num_{len(orders)}.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(subtasks, f, indent=4)

def main():
    

    # recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]
    recipe_dir = "config/recipe"
    recipe_dict = {}
    for recipe_file in os.listdir(recipe_dir):        
        if recipe_file.endswith(".json"):
            with open(os.path.join(recipe_dir, recipe_file), 'r') as f:
                recipe_data = json.load(f)
                for dish in recipe_data:
                    recipe_dict[dish['name']] = dish

    seeds = [42, 84, 126, 128, 256]

    orders_path = "data/cook/orders/all_orders.json"
    with open(orders_path, 'r') as f:
        orders_data = json.load(f)

    output_dir = "data/abstract"
    for name, orders in orders_data.items():
        for seed in seeds:
            generate_abstract_test(orders, seed, recipe_dict, output_dir)
        

if __name__ == "__main__":
    main()