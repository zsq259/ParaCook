import json
import random
import os
from src.utils.utils import print_map

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_stations_from_orders(orders, recipe_dir, num_chopping_board=1, num_each_cookware=1):
    # 统计订单所需食材和工序
    needed_ingredients = set()
    needed_workstations = set()
    needed_cookware = set()
    for order in orders:
        cate, name = order.split('/')
        recipe_path = os.path.join(recipe_dir, f"{cate}.json")
        recipes = load_json(recipe_path)
        recipe = next((r for r in recipes if r["name"] == name), None)
        if not recipe:
            raise ValueError(f"Recipe {name} not found in {recipe_path}")
        for ing in recipe["ingredients"]:
            needed_ingredients.add(ing["item"])
            # 根据食材状态推断需要的工作站
            if ing["state"] == "chopped":
                needed_workstations.add("chopping_board")
            elif ing["state"] == "cooked":
                needed_workstations.add("chopping_board")
                needed_workstations.add("stove")
                if "cookware" in ing:
                    needed_cookware.add(ing["cookware"])
            # 其他状态可扩展
    # 生成分配器
    stations = []
    dispenser_count = 1
    for ing in needed_ingredients:
        stations.append({"name": f"dispenser{dispenser_count}", "provides": ing})
        dispenser_count += 1
    # 生成工作站
    for ws in needed_workstations:
        if ws == "chopping_board":
            for i in range(num_chopping_board):
                stations.append({"name": f"chopping_board{i+1}"})
        elif ws == "stove":
            stove_count = 1
            for cw in needed_cookware:
                for i in range(num_each_cookware):
                    stations.append({"name": f"stove{stove_count}", "item": cw})
                    stove_count += 1
    # 固定添加窗口、洗碗池、盘子回收
    stations += [
        {"name": "serving_window"},
        {"name": "sink"},
        {"name": "plate_return"}
    ]
    return stations

def check_reachability(map_data):
    # 通过 bfs 检查所有 agent 是否可以到达所有工作站相邻四格中的至少一个
    from collections import deque
    width = map_data["width"]
    height = map_data["height"]
    grid = [[0]*width for _ in range(height)]
    for tile in map_data["tiles"]:
        x, y = tile["x"], tile["y"]
        # 工作站和障碍物都视为不可通行
        if tile["type"] == "obstacle" or tile["type"] == "station":
            grid[y][x] = 1
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    def bfs(start):
        visited = set()
        queue = deque([start])
        visited.add(start)
        while queue:
            x, y = queue.popleft()
            for dx, dy in directions:
                nx, ny = x+dx, y+dy
                if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return visited
    
    for agent in map_data["agents"]:
        start = (agent["x"], agent["y"])
        reachable = bfs(start)
        for tile in map_data["tiles"]:
            if tile["type"] == "station":
                pos = (tile["x"], tile["y"])
                # 检查工作站四个方向是否有可达位置
                can_reach = False
                for dx, dy in directions:
                    adj = (pos[0]+dx, pos[1]+dy)
                    if adj in reachable:
                        can_reach = True
                        break
                if not can_reach:
                    print(f"Agent at {start} cannot reach station {tile['name']} at {pos}")
                    return False
    
    return True

def generate_random_map(width=8, height=6, num_agents=2, orders=None, recipe_dir=None, num_tables=None, num_plates=None, num_walls=0, num_chopping_board=1, num_each_cookware=1, seed=None):
    if seed is not None:
        random.seed(seed)
    tiles = []
    # 边缘位置
    edge_positions = [(x, y) for x in range(width) for y in range(height)
                      if x == 0 or x == width-1 or y == 0 or y == height-1]
    # 中间位置
    center_positions = [(x, y) for x in range(1, width-1) for y in range(1, height-1)]

    random.shuffle(edge_positions)
    random.shuffle(center_positions)

    stations = get_stations_from_orders(orders, recipe_dir, num_chopping_board, num_each_cookware)
    pos_idx = 0
    # 工作站优先放边缘
    for station in stations:
        if pos_idx < len(edge_positions):
            pos = edge_positions[pos_idx]
        else:
            pos = center_positions[pos_idx - len(edge_positions)]
        pos_idx += 1
        tile = {"x": pos[0], "y": pos[1], "type": "station", **station}
        tiles.append(tile)

    # 桌子优先放中间
    if num_tables is None:
        num_tables = random.randint(2, 6)
    if num_plates is None:
        num_plates = random.randint(1, num_tables)
    for i in range(num_tables):
        if i < len(center_positions):
            pos = center_positions[i]
        else:
            pos = edge_positions[(pos_idx + i) % len(edge_positions)]
        table = {"x": pos[0], "y": pos[1], "type": "station", "name": f"table{i+1}"}
        if i < num_plates:
            table["item"] = "plate"
        tiles.append(table)

    # 随机放障碍物
    for i in range(num_walls):
        if pos_idx + i < len(center_positions):
            pos = center_positions[pos_idx + i]
        else:
            pos = edge_positions[(pos_idx + i) % len(edge_positions)]
        wall = {"x": pos[0], "y": pos[1], "type": "obstacle", "name": "wall"}
        tiles.append(wall)
    pos_idx += num_walls

    # agent 随机放在剩余空位
    used_positions = {(tile["x"], tile["y"]) for tile in tiles}
    available_positions = [p for p in center_positions + edge_positions if p not in used_positions]
    agent_positions = random.sample(available_positions, num_agents)
    agents = [{"name": f"agent{i+1}", "x": pos[0], "y": pos[1]} for i, pos in enumerate(agent_positions)]

    map_data = {
        "name": "kitchen",
        "width": width,
        "height": height,
        "agents": agents,
        "tiles": tiles
    }
    return map_data

if __name__ == "__main__":
    # 测试生成随机地图
    retry_count = 0
    map_data = None
    while retry_count < 5:
        map_data = generate_random_map(
            width=10,
            height=8,
            num_agents=2,
            orders=["burger/burger_full", "sushi/sushi_fish"],
            recipe_dir="config/recipe",
            num_tables=4,
            num_plates=2,
            num_walls=2,
            seed=42
        )
        print_map(map_data)
        if check_reachability(map_data):
            break
        map_data = None
        retry_count += 1
    if not map_data:
        print("Failed to generate a valid map after retries.")
    else:
        print(json.dumps(map_data, indent=4))   
