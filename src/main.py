# main.py

import json
import sys
import os
import argparse
import datetime
from src.game.world_state import World
from src.game.simulator import Simulator
from src.utils.utils import get_model_wrapper
from src.agent.method.IO.IO import IOAgent
from src.agent.method.CoT.CoT import CoTAgent
from src.agent.method.PLaG.PLaG import PLaGAgent
from src.agent.method.ReAct.ReAct import ReActAgent
from src.agent.method.MultiStepReAct.MultiStepReAct import MultiStepReActAgent
from src.agent.method.Fixed.Fixed import FixedAgent
from src.agent.method.Human.Human import HumanAgent
from src.utils.logger_config import logger, set_log_dir, COLOR_CODES, RESET

name_to_agent = {
    "IO": IOAgent,
    "CoT": CoTAgent,
    "PLaG": PLaGAgent,
    "ReAct": ReActAgent,
    "MultiStepReAct": MultiStepReActAgent,
    "Fixed": FixedAgent,
    "Human": HumanAgent,
}

def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_test(args):
    log_dir = "logs"
    now = datetime.datetime.now()
    date_str = now.strftime("%y-%m-%d")
    run_time_str = now.strftime("%H-%M-%S")
    run_log_dir = os.path.join(log_dir, date_str, args.batch_log_id, run_time_str)
    set_log_dir(run_log_dir)

    run_args_path = os.path.join(run_log_dir, "run_args.json")
    os.makedirs(os.path.dirname(run_args_path), exist_ok=True)
    with open(run_args_path, 'w', encoding='utf-8') as f:
        json.dump(vars(args), f, indent=4)

    result_path = f"results/{args.agent}/{args.model}/{args.result_path}.json"
    if not args.result_path:
        result_path = None
    else:
        if os.path.exists(result_path) and args.result_path != "tmp":
            data = load_data(result_path)
            logger.info(data.get("time", 0))
            if data.get("time", 0) > 0:
                logger.info(f"{COLOR_CODES['GREEN']}result file {result_path} already exists, skipping execution.{RESET}")
                return
    # --- 1. Load configuration data ---
    map_data = load_data(f'{args.map}.json')
    ingredient_data = load_data(f'config/item/{args.ingredient}.json')
    object_data = load_data(f'config/item/{args.object}.json')
    orders = args.orders if args.orders else [] # Order list for testing (format: category/name)
    order_names = [order.split('/')[1] for order in orders] # List of order names
    recipe_data = [] # All recipe data recorded in world
    recipes = [] # Recipe data passed to agent
    
    unique_orders = list(set(orders))
    for order in unique_orders:
        order_cate, order_name = order.split('/')
        cate_recipe = load_data(f'config/recipe/{order_cate}.json')
        for recipe in cate_recipe:
            if recipe["name"] == order_name:
                recipe_data.append(recipe)
                recipes.append(recipe["name"] + ": " + recipe["recipe"])
                break

    # --- 2. Initialize world and simulator ---
    world = World(map_data, object_data, recipe_data, orders=order_names)
    simulator = Simulator(world)

    # --- 3. Initialize Agent and run test ---
    model_wrapper = get_model_wrapper(args.model)
    model = model_wrapper(args.model)
    agent = name_to_agent[args.agent](model, log_dir=run_log_dir)
    result = agent.run_test(simulator, recipes, args.examples if args.examples else [])
    
    logger.info(f"{COLOR_CODES['GREEN']}Results saved to: {result_path}{RESET}")
    if result_path:
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)




def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='OverCooked Agent Experiment Program')
    
    # Required parameters
    parser.add_argument('--model', '-m', required=True, 
                       help='Model to use (e.g., gpt-4o, gemini-2.5-pro)')
    parser.add_argument('--agent', '-a', required=True, 
                       help='Agent method to use')
    
    # Optional parameters with default values
    parser.add_argument('--ingredient', '-i', default='ingredient',
                       help='Ingredient configuration file name (default: ingredient)')
    parser.add_argument('--object', '-o', default='station',
                       help='Object configuration file name (default: station)')
    parser.add_argument('--map', default='config/map_examples/map1',
                       help='Map file path (default: config/map_examples/map1)')
    
    # List parameters
    parser.add_argument('--examples', nargs='*', default=["salad_advanced"],
                       help='Example list (e.g., --examples salad_advanced burger_basic)')
    parser.add_argument('--orders', nargs='*',
                       help='Order list (e.g., --orders salad/salad_advanced burger/burger_basic)')
    
    # Configuration file
    parser.add_argument('--config', '-c', type=str,
                       help='Configuration file path (if specified, will be merged with command line arguments)')
    
    # Result path
    parser.add_argument('--result-path', '-r', default='tmp',
                       help='Result file path must be specified')
    
    parser.add_argument('--batch-log-id', type=str, default='',
                       help='Batch log identifier for logging purposes')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    logger.info(f"Running test: model={args.model}, method={args.agent}, map={args.map}, orders={args.orders}, result_path={args.result_path}")

    run_test(args)