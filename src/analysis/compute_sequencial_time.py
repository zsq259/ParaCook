from src.game.const import *
import json, os

def compute_dish_time_and_movements(dish: dict) -> tuple[int, int]:
    """
    Calculate the cooking time for a single dish.
    """
    total_time = 0
    total_movements = 0
    for ingredient in dish['ingredients']:
        if ingredient["state"] == "raw":
            total_time += 18 * 2 # move to dispenser, and plate
            total_movements += 18 * 2
        elif ingredient["state"] == "chopped":
            total_time += 18 * 3 # move to dispenser, chopping board, and plate
            total_time += PROCESS_CUT_TIME
            total_movements += 18 * 3
        elif ingredient["state"] == "cooked":
            total_time += 18 * 4 # move to dispenser, cooking station, and plate and cooking station
            if ingredient["item"] in ["rice", "pasta"]:
                total_time += PROCESS_POT_COOK_TIME
            else:
                total_time += PROCESS_PAN_COOK_TIME
            total_movements += 18 * 4
    total_time += 18 # move to serving station
    total_movements += 18
    return total_time, total_movements

def compute_order_time_and_movements(orders: list[str], dish_time_and_movements: dict) -> tuple[int, int]:
    """
    Calculate the total cooking time for a list of orders.
    """
    total_time = 0
    total_movements = 0
    for order in orders:
        if "/" in order:
            order = order.split('/')[1]
        total_time += dish_time_and_movements[order][0]
        total_movements += dish_time_and_movements[order][1]

    total_time += max(0, len(orders) - 2) * (18 * 2 + RETURN_DIRTY_PLATE_TIME + PROCESS_WASH_PLATE_TIME) # time for returning and washing plates if more than 2 dishes
    total_movements += max(0, len(orders) - 2) * (18 * 2) # movements for returning and washing plates if more than 2 dishes
    return total_time, total_movements

def get_dish_time_and_movements(recipe_dir: str="config/recipe") -> dict:
    dish_time_and_movements = {}
    for recipe_file in os.listdir(recipe_dir):        
        if recipe_file.endswith(".json"):
            with open(os.path.join(recipe_dir, recipe_file), 'r') as f:
                recipe_data = json.load(f)
                for dish in recipe_data:
                    time, movements = compute_dish_time_and_movements(dish)
                    dish_time_and_movements[dish['name']] = time, movements
    return dish_time_and_movements

def main():
    dish_time_and_movements = get_dish_time_and_movements()
    recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]

    orders_path = "data/cook/orders/all_orders.json"
    with open(orders_path, 'r') as f:
        orders_data = json.load(f)
    
    for recipe in recipes:
        times = []
        for name, orders in orders_data.items():
            if recipe in name:
                time = compute_order_time_and_movements(orders, dish_time_and_movements)
                times.append(time)
        print(times)
        # print(f"Orders: {recipe}, Avg Order Time: {sum(times)/len(times):.2f}, Max Order Time: {max(times)}, Min Order Time: {min(times)}")


if __name__ == "__main__":
    main()