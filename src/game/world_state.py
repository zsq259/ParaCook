# world_state.py

from collections import deque
from typing import List, Dict, Optional, Tuple
from src.game.object import *

class World:
    """管理所有游戏对象和地图状态"""
    def __init__(self, map_data: Dict, objects_info: List[Dict], recipes: Optional[List] = [], orders: List[str] = []):
        self.width = map_data['width']
        self.height = map_data['height']
        
        self.objects_info = {o['name']: o for o in objects_info}
        self.recipes = recipes
        self.orders = orders
        self.finished_orders = []

        self.grid: Dict[Tuple[int, int], List[GameObject]] = {}
        self.objects: Dict[str, GameObject] = {}
        
        self.agents: Dict[str, Agent] = {}
        self.map_data = map_data
        self._load_map(map_data)

    def get_object_by_name(self, obj_name: str) -> Optional[GameObject]:
        """返回指定名称的对象"""
        return self.objects.get(obj_name)

    def get_objects_at(self, x: int, y: int) -> List[GameObject]:
        """返回指定位置的所有对象"""
        return self.grid.get((x, y), [])

    def get_station_at(self, x: int, y: int) -> Optional[Station]:
        """返回指定位置的工作台（如果有的话）"""
        for obj in self.get_objects_at(x, y):
            if isinstance(obj, Station):
                return obj
        return None
    
    def _is_walkable(self, x: int, y: int) -> bool:
        # 边界检查
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # 检查该位置的所有对象
        objects_at_pos = self.get_objects_at(x, y)
        for obj in objects_at_pos:
            # 如果有墙壁或工作台，不可行走
            if obj.type in ["obstacle", "station"]:
                return False
            # Agent和物品不阻挡移动
        
        return True
    
    def is_adjacent(self, pos1, pos2) -> bool:
        """Check if two positions are adjacent (four directions: up, down, left, right)"""
        return (abs(pos1[0] - pos2[0]) == 1 and pos1[1] == pos2[1]) or (abs(pos1[1] - pos2[1]) == 1 and pos1[0] == pos2[0])

    def find_path(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], adjacent_to_station: bool = False) -> Tuple[int, List[Tuple[int, int]]]:
        """
        使用BFS找到从起点到终点的最短路径
        Args:
            start_pos: 起点坐标 (x, y)
            end_pos: 终点坐标 (x, y)
            adjacent_to_station: 若为True且end_pos为station，则寻路到最近的相邻空地
        Returns:
            tuple: (路径长度, 路径坐标列表)
            - 如果无法到达，返回 (-1, [])
            - 路径包括起点和终点
        """
        if start_pos == end_pos:
            return (0, [start_pos])
        
        if not self._is_walkable(*end_pos) and not adjacent_to_station:
            return (-1, [])
        
        queue = deque([(start_pos, 0, [start_pos])])  # (position, distance, path)
        visited = {start_pos}
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        # print(f"Finding path from {start_pos} to {end_pos}, adjacent_to_station={adjacent_to_station}")

        station = self.get_station_at(*end_pos)
        
        while queue:
            (x, y), dist, path = queue.popleft()
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited and self._is_walkable(nx, ny):
                    new_path = path + [(nx, ny)]
                    if (nx, ny) == end_pos:
                        return (dist + 1, new_path)
                    if adjacent_to_station and station and self.is_adjacent((nx, ny), end_pos):
                        return (dist + 1, new_path)
                    queue.append(((nx, ny), dist + 1, new_path))
                    visited.add((nx, ny))
        
        return (-1, [])  # 无法到达

    def _add_object(self, obj: GameObject):
        pos = obj.get_pos()
        self.grid.setdefault(pos, []).append(obj)
        if self.objects.get(obj.name):
            orig_obj = self.objects[obj.name]
            if isinstance(orig_obj, list):
                orig_obj.append(obj)
            else:
                self.objects[obj.name] = obj
        self.objects[obj.name] = obj
        if isinstance(obj, Agent):
            self.agents[obj.name] = obj

    def _load_map(self, map_data: Dict):
        # 初始化空地
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x,y)] = []
        
        # 加载地图上的对象
        for tile_data in map_data['tiles']:
            x, y = tile_data['x'], tile_data['y']
            name = tile_data.get('name')
            obj_type = tile_data.get('type')
            
            if obj_type == "obstacle":
                self._add_object(Wall(name, x, y))
            elif obj_type == "station":
                # 根据station名称创建对应的派生类
                station = None
                if "table" in name:
                    station = Table(name, x, y)
                elif "dispenser" in name:
                    provides = tile_data.get("provides")
                    station = Dispenser(name, x, y, provides)
                elif "chopping_board" in name:
                    station = ChoppingBoard(name, x, y)
                elif "stove" in name:
                    station = Stove(name, x, y)
                elif "serving_window" in name:
                    station = ServingWindow(name, x, y)
                elif "sink" in name:
                    station = Sink(name, x, y)
                elif "plate_return" in name:
                    station = PlateReturn(name, x, y)
                elif "trash" in name:
                    station = Trash(name, x, y)
                else:
                    raise ValueError(f"未知的工作台类型: {name}")
                
                self._add_object(station)
                
                # 加载初始时就在台上的物品
                name_to_item = {
                    "plate": Plate,
                    "pan": Pan,
                    "pot": Pot
                }
                if "item" in tile_data:
                    item_name = tile_data["item"]
                    if self.objects_info.get(item_name, {}).get("type") == "container":
                        item = name_to_item.get(item_name)
                        if not item:
                            raise ValueError(f"未知的容器类型: {item_name}")
                        item = item(x, y)
                        station.item = item
                        self._add_object(item)

        # 加载代理
        for agent_data in map_data['agents']:
            agent = Agent(agent_data['name'], agent_data['x'], agent_data['y'])
            self._add_object(agent)

    def to_json(self):
        data = {
            "width": self.width,
            "height": self.height,
            "agents": [agent.to_json() for agent in self.agents.values()],
            "tiles": []
        }
        for obj in self.objects.values():
            if obj.type == "obstacle" or obj.type == "station":
                data["tiles"].append(obj.to_json())
        return data