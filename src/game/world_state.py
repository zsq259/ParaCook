# world_state.py

from collections import deque
from typing import List, Dict, Optional, Tuple
from src.game.object import *

class World:
    """Manage all game objects and map state"""
    def __init__(self, map_data: Dict, objects_info: List[Dict], recipes: Optional[List] = [], orders: List[str] = []):
        self.width = map_data['width']
        self.height = map_data['height']
        
        self.objects_info = {o['name']: o for o in objects_info}
        self.objects_count = {o['name']: 0 for o in objects_info}
        self.recipes = recipes
        self.orders = orders
        self.finished_orders = []

        self.grid: Dict[Tuple[int, int], List[GameObject]] = {}
        self.objects: Dict[str, GameObject] = {}
        
        self.agents: Dict[str, Agent] = {}
        self.map_data = map_data
        self._load_map(map_data)

    def get_object_by_name(self, obj_name: str) -> Optional[GameObject]:
        """Return object with specified name"""
        return self.objects.get(obj_name)

    def get_objects_at(self, x: int, y: int) -> List[GameObject]:
        """Return all objects at specified position"""
        return self.grid.get((x, y), [])

    def get_station_at(self, x: int, y: int) -> Optional[Station]:
        """Return station at specified position (if any)"""
        for obj in self.get_objects_at(x, y):
            if isinstance(obj, Station):
                return obj
        return None
    
    def _is_walkable(self, x: int, y: int) -> bool:
        # Boundary check
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check all objects at this position
        objects_at_pos = self.get_objects_at(x, y)
        for obj in objects_at_pos:
            # If there's a wall or station, not walkable
            if obj.type in ["obstacle", "station"]:
                return False
            # Agents and items don't block movement
        
        return True
    
    def is_adjacent(self, pos1, pos2) -> bool:
        """Check if two positions are adjacent (four directions: up, down, left, right)"""
        return (abs(pos1[0] - pos2[0]) == 1 and pos1[1] == pos2[1]) or (abs(pos1[1] - pos2[1]) == 1 and pos1[0] == pos2[0])

    def find_path(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], adjacent_to_station: bool = False) -> Tuple[int, List[Tuple[int, int]]]:
        """
        Use BFS to find shortest path from start to end
        Args:
            start_pos: Start coordinates (x, y)
            end_pos: End coordinates (x, y)
            adjacent_to_station: If True and end_pos is a station, pathfind to nearest adjacent empty space
        Returns:
            tuple: (path length, list of path coordinates)
            - If unreachable, returns (-1, [])
            - Path includes start and end points
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
        
        return (-1, [])  # Cannot reach

    def _add_object(self, obj: GameObject):
        pos = obj.get_pos()
        self.grid.setdefault(pos, []).append(obj)
        if obj.name in self.objects_count:
            name = obj.name
            if obj.type == "obstacle" and self.objects_count.get(obj.name, 0) > 0:
                obj.name = f"{obj.name}_{self.objects_count[obj.name]}"
            self.objects_count[name] += 1
        self.objects[obj.name] = obj
        if isinstance(obj, Agent):
            self.agents[obj.name] = obj

    def _load_map(self, map_data: Dict):
        # Initialize empty spaces
        for y in range(self.height):
            for x in range(self.width):
                self.grid[(x,y)] = []
        
        # Load objects on the map
        for tile_data in map_data['tiles']:
            x, y = tile_data['x'], tile_data['y']
            name = tile_data.get('name')
            obj_type = tile_data.get('type')
            
            if obj_type == "obstacle":
                self._add_object(Wall(name, x, y))
            elif obj_type == "station":
                # Create corresponding derived class based on station name
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
                    raise ValueError(f"Unknown station type: {name}")
                
                self._add_object(station)
                
                # Load items initially on the station
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
                            raise ValueError(f"Unknown container type: {item_name}")
                        item = item(x, y)
                        station.item = item
                        self._add_object(item)

        # Load agents
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