# main.py

import json
import yaml
import sys
import os
import argparse
from src.game.world_state import World
from src.game.simulator import Simulator
from src.utils.utils import get_model
from src.agent.method.IO.IO import IOAgent
from src.agent.method.CoT.CoT import CoTAgent
from src.agent.method.ReAct.ReAct import ReActAgent
from src.agent.method.Fixed.Fixed import FixedAgent
from src.utils.logger_config import logger, COLOR_CODES, RESET

name_to_agent = {
    "IO": IOAgent,
    "CoT": CoTAgent,
    "ReAct": ReActAgent,
    "Fixed": FixedAgent
}

def load_yaml_config(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_test(args):
    result_path = f"results/{args.agent}/{args.model}/{args.result_path}.json"
    if not args.result_path:
        result_path = None
    else:
        if os.path.exists(result_path):
            data = load_data(result_path)
            logger.info(data.get("time", 0))
            if data.get("time", 0) > 0:
                logger.info(f"{COLOR_CODES['GREEN']}result file {result_path} already exists, skipping execution.{RESET}")
                return
    # --- 1. 加载配置数据 ---
    map_data = load_data(f'{args.map}.json')
    ingredient_data = load_data(f'config/item/{args.ingredient}.json')
    object_data = load_data(f'config/item/{args.object}.json')
    orders = args.orders if args.orders else [] # 测试时的订单列表（格式为 分类/名称）
    order_names = [order.split('/')[1] for order in orders] # 订单名称列表
    recipe_data = [] # world 中记录的所有菜谱数据
    recipes = [] # 传给 agent 的菜谱数据
    
    unique_orders = list(set(orders))
    for order in unique_orders:
        order_cate, order_name = order.split('/')
        cate_recipe = load_data(f'config/recipe/{order_cate}.json')
        for recipe in cate_recipe:
            if recipe["name"] == order_name:
                recipe_data.append(recipe)
                recipes.append(recipe["name"] + ": " + recipe["recipe"])
                break

    # --- 2. 初始化世界和模拟器 ---
    world = World(map_data, object_data, recipe_data, orders=order_names)
    simulator = Simulator(world)

    # --- 3. 初始化Agent并运行测试 ---
    model = get_model(args.model)
    agent = name_to_agent[args.agent](model)
    result = agent.run_test(world, simulator, recipes, args.examples if args.examples else [])
    
    logger.info(f"{COLOR_CODES['GREEN']}Results saved to: {result_path}{RESET}")
    if result_path:
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)




def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='OverCooked 智能体实验程序')
    
    # 必需参数
    parser.add_argument('--model', '-m', required=True, 
                       help='使用的模型 (例如: gpt-4o, gemini-2.5-pro)')
    parser.add_argument('--agent', '-a', required=True, 
                       choices=['IO', 'CoT', 'ReAct', 'Fixed'],
                       help='使用的智能体方法')
    
    # 可选参数，设置默认值
    parser.add_argument('--ingredient', '-i', default='ingredient',
                       help='食材配置文件名 (默认: ingredient)')
    parser.add_argument('--object', '-o', default='station',
                       help='物品配置文件名 (默认: station)')
    parser.add_argument('--map', default='config/map/map1',
                       help='地图文件路径 (默认: config/map/map1)')
    
    # 列表参数
    parser.add_argument('--examples', nargs='*', default=["salad_advanced"],
                       help='示例列表 (例如: --examples salad_advanced burger_basic)')
    parser.add_argument('--orders', nargs='*',
                       help='订单列表 (例如: --orders salad/salad_advanced burger/burger_basic)')
    
    # 配置文件
    parser.add_argument('--config', '-c', type=str,
                       help='配置文件路径 (如果指定，会与命令行参数合并)')
    
    # 结果路径
    parser.add_argument('--result-path', '-r',
                       help='结果文件路径 必须指定')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    if args.config:
        if args.config.endwith(".yaml") or args.config.endwith(".yml"):
            config_data = load_yaml_config(args.config)
            for key, value in config_data.items():
                if hasattr(args, key) and value is not None:
                    setattr(args, key, value)

    run_test(args)