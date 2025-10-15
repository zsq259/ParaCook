# object.py

from ast import In
from typing import List, Dict, Optional, Tuple
from src.utils.logger_config import logger, COLOR_CODES, RESET
from src.game.const import *

class GameObject:
    def __init__(self, name: str, obj_type: str, x: int, y: int):
        self.name = name  # directly use the name as unique id
        self.type = obj_type
        self.x = x
        self.y = y

    def get_pos(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def to_json(self):
        return {
            "name": self.name,
            "type": self.type
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', pos=({self.x},{self.y}))"

class Item(GameObject):
    """the base class for items that can be picked up and put down"""
    def __init__(self, name: str, obj_type: str, x: int, y: int):
        super().__init__(name, obj_type, x, y)

class Ingredient(Item):
    """Ingredient with states"""
    def __init__(self, name: str, x: int, y: int, state: str = "raw"):
        super().__init__(name, "ingredient", x, y)
        self.state = state
    
    def to_json(self):
        return {
            "name": self.name,
            # "type": self.type,
            "state": self.state
        }

    def __repr__(self):
        return f"Ingredient(name='{self.name}', state='{self.state}')"

class Container(Item):
    """Container that can hold ingredients"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, "container", x, y)
        self.contents: List[Ingredient] = []

    def add_item(self, item: Ingredient, current_time = None):
        self.contents.append(item)

    def to_json(self):
        return {
            "name": self.name,
            "type": self.type,
            "contents": [item.to_json() for item in self.contents]
        }

    def __repr__(self):
        content_names = [c.name for c in self.contents]
        return f"Container(name='{self.name}', contents={content_names})"

class Plate(Container):
    """Plate, used for serving, has recipe checking logic"""
    def __init__(self, x: int, y: int):
        super().__init__("plate", x, y)

    def check_recipe(self, recipe: Dict) -> bool:
        recipe_ingredients = recipe.get("ingredients", [])
        if len(self.contents) != len(recipe_ingredients):
            raise ValueError(f"Container contents count does not match recipe requirements. Contents: {self.contents}")

        def get_signature(item: Ingredient):
            return f"{item.name}:{item.state}"

        contents_signatures = sorted([get_signature(ing) for ing in self.contents])
        recipe_signatures = sorted([f"{req['item']}:{req['state']}" for req in recipe_ingredients])

        logger.info(f"Checking recipe {recipe['name']}: contents {contents_signatures} vs recipe {recipe_signatures}")
        return contents_signatures == recipe_signatures
    
class DirtyPlate(Item):
    """Dirty plate, needs to be washed before reuse"""
    def __init__(self, x: int, y: int):
        super().__init__("dirty_plate", "dirty_plate", x, y)

class Pan(Container):
    """Pan, used for frying"""
    def __init__(self, x: int, y: int):
        super().__init__("pan", x, y)
        self.finished: bool = False  # Is cooking finished
        self.current_time: int = 0  # Current cooking time
        self.processed_cook_time : int = 0  # Already cooked time
        self.required_cook_time : int = 0  # Required cooking time
        self.is_cooking: bool = False  # Is currently cooking
    
    def add_item(self, item: Ingredient, current_time: int) -> bool:
        if item.name in ["meat", "chicken", "mushroom", "tomato", "fish", "prawn"]:
            if item.state == "chopped":
                super().add_item(item)
                self.is_cooking = True
                if self.current_time == 0:
                    self.current_time = current_time
                self.required_cook_time += PROCESS_PAN_COOK_TIME
                return True
        raise ValueError("Can only put chopped ingredients (meat, chicken, mushroom, tomato, fish, prawn) into the pan for cooking")
    
    def update_cooking(self, current_time: int):
        if not self.is_cooking:
            return
        duration = current_time - self.current_time
        self.current_time = current_time
        if self.processed_cook_time + duration >= self.required_cook_time:
            self.processed_cook_time = self.required_cook_time
            self.is_cooking = False
            for ing in self.contents:
                ing.state = "cooked"
            logger.info(f"Pan {self.name} food is cooked")
        else:
            self.processed_cook_time += duration
            logger.info(f"Pan {self.name} food cooked {self.processed_cook_time}/{self.required_cook_time}")

    def to_json(self):
        data = super().to_json()
        data.update({
            "finished": self.finished,
            "processed_cook_time": self.processed_cook_time,
            "required_cook_time": self.required_cook_time,
            "is_cooking": self.is_cooking
        })
        return data

class Pot(Container):
    """Pot, used for boiling"""
    def __init__(self, x: int, y: int):
        super().__init__("pot", x, y)
        self.finished: bool = False  # Is cooking finished
        self.current_time: int = 0  # Current cooking time
        self.processed_cook_time : int = 0  # Already cooked time
        self.required_cook_time : int = 0  # Required cooking time
        self.is_cooking: bool = False  # Is currently cooking
    
    def add_item(self, item: Ingredient, current_time: int) -> bool:
        if item.name in ["rice", "pasta"]:
            if item.state == "raw":
                super().add_item(item)
                self.is_cooking = True
                if self.current_time == 0:
                    self.current_time = current_time
                self.required_cook_time += PROCESS_POT_COOK_TIME
                return True
        raise ValueError("Can only put raw rice or pasta for boiling")
    
    def update_cooking(self, current_time: int):
        if not self.is_cooking:
            return
        duration = current_time - self.current_time
        self.current_time = current_time
        if self.processed_cook_time + duration >= self.required_cook_time:
            self.processed_cook_time = self.required_cook_time
            self.is_cooking = False
            for ing in self.contents:
                ing.state = "cooked"
            logger.info(f"Pot {self.name} food is cooked")
        else:
            self.processed_cook_time += duration
            logger.info(f"Pot {self.name} food cooked {self.processed_cook_time}/{self.required_cook_time}")
        
    def to_json(self):
        data = super().to_json()
        data.update({
            "finished": self.finished,
            "processed_cook_time": self.processed_cook_time,
            "required_cook_time": self.required_cook_time,
            "is_cooking": self.is_cooking
        })
        return data

class Station(GameObject):
    """Base class for stations"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, "station", x, y)
        self.item: Optional[Item] = None
        self.in_use: bool = False
        self.current_user: Optional[str] = None
    
    def can_use(self, agent_name: str) -> bool:
        """Check if the station can be used (not in use or used by the same agent)"""
        return True
    
    def use(self, agent_name: str) -> bool:
        """Mark the station as in use by the agent"""
        if not self.can_use(agent_name):
            raise ValueError("Station is currently in use")
        self.in_use = True
        self.current_user = agent_name
        return True
    
    def release(self):
        """Release the station"""
        self.in_use = False
        self.current_user = None

    def basic_interact(self, agent, current_time = None) -> bool:
        """Basic interaction logic for placing or picking up items"""
        if agent.holding is None:
            # Empty hand: try to pick up from the station
            if self.item is not None:
                agent.holding = self.item
                self.item = None
                return True
            raise ValueError("The agent is empty-handed and there's nothing on the station to pick up")
        else:
            # Hold something: try to place it on the station
            if self.item is None:
                self.item = agent.holding
                agent.holding = None
                return True
            elif isinstance(agent.holding, Container) and isinstance(self.item, Ingredient):
                # If the hand is a container and the station has an ingredient, try to put the ingredient into the container
                agent.holding.add_item(self.item, current_time)
                self.item = None
                return True
            elif isinstance(agent.holding, Ingredient) and isinstance(self.item, Container):
                # If the hand is an ingredient and the station has a container, try to put the ingredient into the container
                self.item.add_item(agent.holding, current_time)
                agent.holding = None
                return True
            elif isinstance(agent.holding, Container) and isinstance(self.item, Container):
                # If both hand and station are containers, transfer contents to the plate
                if isinstance(agent.holding, Plate):
                    for ing in self.item.contents:
                        agent.holding.add_item(ing, current_time)
                    self.item.contents.clear()
                    return True
                if isinstance(self.item, Plate):
                    for ing in agent.holding.contents:
                        self.item.add_item(ing, current_time)
                    agent.holding.contents.clear()
                    return True
                
            raise ValueError("Cannot place the held item on the station")

    def interact(self, agent_name: str, world, current_time = None) -> bool:
        raise NotImplementedError("The subclass must implement the interact method")

    def process(self, agent_name: str) -> bool:
        raise NotImplementedError("The subclass must implement the process method")
    
    def to_json(self):
        data = {
            "name": self.name,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "item": None,
            "in_use": self.in_use,
            "current_user": self.current_user
        }
        if self.item is not None:
            data["item"] = self.item.to_json()
        return data
    
class Wall(Station):
    """Wall, obstacle"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, x, y)
        self.type = "obstacle"
    
    def interact(self, agent_name: str, world, current_time = None) -> bool:
        raise ValueError("Wall cannot be interacted with")
    
    def process(self, agent_name: str) -> bool:
        raise ValueError("Wall cannot be processed")

class Table(Station):
    """Table, can place and pick up items"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, x, y)
    
    def interact(self, agent_name: str, world, current_time = None) -> bool:
        """Place or pick up items"""
        agent = world.agents[agent_name]
        logger.info(f"Agent {agent_name} interact with Table: Surface={self.item}, Holding={agent.holding}")
        return self.basic_interact(agent, current_time)

class Dispenser(Station):
    """Ingredient Dispenser, can provide unlimited specific ingredients"""
    def __init__(self, name: str, x: int, y: int, provides: str):
        super().__init__(name, x, y)
        self.provides: str = provides
    
    def interact(self, agent_name: str, world, current_time = None) -> bool:
        """Get ingredient or place item on top"""
        agent = world.agents[agent_name]
        logger.info(f"Agent {agent_name} interact with Dispenser: Surface={self.item}, Holding={agent.holding}")
        if agent.holding is None and self.item is None:
            # Empty hand and no item on the station: generate a new raw ingredient
            new_ingredient = Ingredient(self.provides, agent.x, agent.y, "raw")
            agent.holding = new_ingredient
            logger.info(f"Agent {agent_name} got new ingredient {agent.holding} from Dispenser {self.name}")
            return True
        else:
            return self.basic_interact(agent, current_time)
        
    def to_json(self):
        data = super().to_json()
        data.update({
            "provides": self.provides
        })
        return data

class ChoppingBoard(Station):
    """Chopping Board, can perform chopping operations"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, x, y)
    
    def can_use(self, agent_name: str) -> bool:
        """Check if the chopping board can be used (not in use or used by the same agent)"""
        return not self.in_use or self.current_user == agent_name
    
    def interact(self, agent_name: str, world, current_time = None) -> bool:
        """Place or pick up items"""
        if not self.can_use(agent_name):
            raise ValueError("Chopping board is currently in use")

        agent = world.agents[agent_name]
        logger.info(f"Agent {agent_name} interact with ChoppingBoard: Surface={self.item}, Holding={agent.holding}")
        return self.basic_interact(agent, current_time)
    
    def process(self, agent_name: str) -> bool:
        if not self.can_use(agent_name):
            raise ValueError("Chopping board is currently in use")
        
        logger.info(f"Agent {agent_name} process ChoppingBoard: Surface={self.item}")
        
        if self.item is None or not isinstance(self.item, Ingredient):
            raise ValueError("No ingredient on the chopping board to cut")
        
        ingredient = self.item
        if ingredient.state == "raw":
            ingredient.state = "chopped"
            return True
        raise ValueError("Ingredient on chopping board is not in a state that can be cut")

class Stove(Station):
    """Stove, can only hold cookware (pots/pans)"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, x, y)
    
    def interact(self, agent_name: str, world, current_time) -> bool:
        """Place or pick up cookware (pots/pans)"""
        agent = world.agents[agent_name]
        logger.info(f"Agent {agent_name} interact with Stove: Surface={self.item}, Holding={agent.holding}")
        if agent.holding is None:
            # Empty hand: pick up cookware
            if self.item is not None:
                agent.holding = self.item
                self.item = None
                return True
            raise ValueError("The agent is empty-handed and there's nothing on the stove to pick up")
        else:
            # Hold something: can only place or pick up cookware
            if self.item is None:
                if isinstance(agent.holding, Container) and agent.holding.name in ["pot", "pan"]:
                    if self.item is None:
                        self.item = agent.holding
                        agent.holding = None
                        return True
            else:
                if isinstance(self.item, Container) and self.item.name in ["pot", "pan"] and isinstance(agent.holding, Ingredient):
                    # If the station has cookware and the hand has an ingredient, try to put the ingredient into the cookware
                    self.item.add_item(agent.holding, current_time)
                    agent.holding = None
                    return True
                elif isinstance(self.item, Container) and self.item.name in ["pot", "pan"] and isinstance(agent.holding, Container):
                    # If both hand and station are containers, transfer contents to the plate
                    if isinstance(agent.holding, Plate):
                        for ing in self.item.contents:
                            agent.holding.add_item(ing)
                        self.item.contents.clear()
                        return True
                    if isinstance(self.item, Plate):
                        for ing in agent.holding.contents:
                            self.item.add_item(ing)
                        agent.holding.contents.clear()
                        return True
            raise ValueError("Can only place or pick up cookware (pot/pan) on the stove")

class ServingWindow(Station):
    """Serving Window, check if the dish is completed"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, x, y)
    
    def interact(self, agent_name: str, world, current_time = None) -> bool:
        """Submit completed dish"""
        if not current_time:
            raise ValueError("Current time must be provided to handle serving")
        agent = world.agents[agent_name]
        logger.info(f"Agent {agent_name} serve: {agent.holding}")
        served_dish = agent.holding.to_json() if agent.holding else None

        if not isinstance(agent.holding, Plate):
            raise ValueError("Can only serve food on a plate")
        order = world.orders[0]
        for recipe in world.recipes:
            if recipe["name"] == order and agent.holding.check_recipe(recipe):
                logger.info(f"Agent {agent_name} successfully served: {recipe['name']}")
                agent.holding = None  # Clear the plate after serving
                for obj in world.objects.values():
                    if isinstance(obj, PlateReturn):
                        obj.return_time.append(current_time + RETURN_DIRTY_PLATE_TIME)
                        logger.info(f"Dirty plate will be generated at time {current_time + RETURN_DIRTY_PLATE_TIME}")
                        break
                world.finished_orders.append(order)
                world.orders.pop(0)
                if len(world.orders) == 0:
                    logger.info(f"{COLOR_CODES['GREEN']}All orders are completed!{RESET}")
                return True
        raise ValueError(f"The dish on the plate does not match the current order. Current dish: {served_dish}, Current order: {order}")

class Sink(Station):
    """Sink, wash dirty plates"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, x, y)
    
    def interact(self, agent_name: str, world, current_time = None) -> bool:
        """Can only place dirty plates or pick up washed plates"""
        agent = world.agents[agent_name]
        logger.info(f"Agent {agent_name} interact with Sink: Surface={self.item}, Holding={agent.holding}")
        if agent.holding is None:
            if self.item is not None and isinstance(self.item, Plate):
                agent.holding = self.item
                self.item = None
                return True
            raise ValueError("Agent is empty-handed and there's no washed plate on the sink to pick up")
        else:
            if self.item is None and isinstance(agent.holding, DirtyPlate):
                self.item = agent.holding
                agent.holding = None
                return True
            raise ValueError("Can only place dirty plates for washing, or pick up washed plates")
    
    def process(self, agent_name: str) -> bool:
        """ Wash dirty plate """
        if not self.can_use(agent_name):
            raise ValueError("Sink is currently in use")
        
        logger.info(f"Agent {agent_name} wash Sink: Surface={self.item}")
        
        if self.item is None or not isinstance(self.item, DirtyPlate):
            raise ValueError("No dirty plate on the sink to wash")
        
        # Wash the dirty plate and turn it into a clean plate
        self.item = Plate(self.x, self.y)
        return True

class PlateReturn(Station):
    """Dirty Plate Return, generates dirty plates over time"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, x, y)
        self.return_time = [] # Queue of times when dirty plates will be generated
        self.dirty_plates_sum = 0 # Current number of dirty plates available
    
    def interact(self, agent_name: str, world, current_time = None) -> bool:
        """Get a dirty plate if available, cannot place items here"""
        agent = world.agents[agent_name]
        if agent.holding is not None:
            raise ValueError("Cannot pick up dirty plate while holding something")
        if self.dirty_plates_sum == 0:
            raise ValueError("No dirty plates available to pick up")
        
        agent.holding = DirtyPlate(agent.x, agent.y)
        self.dirty_plates_sum -= 1
        return True
    
    def update(self, current_time: int):
        """Generate dirty plates based on the current time"""
        while self.return_time and self.return_time[0] <= current_time:
            self.return_time.pop(0)
            self.dirty_plates_sum += 1
            logger.info(f"PlateReturn {self.name} generated a dirty plate, total now {self.dirty_plates_sum}")

    def to_json(self):
        data = super().to_json()
        data.update({
            "dirty_plates_sum": self.dirty_plates_sum
        })
        return data

class Trash(Station):
    """Trash can, discard items in hand or in container"""
    def __init__(self, name: str, x: int, y: int):
        super().__init__(name, x, y)
    
    def interact(self, agent_name: str, world, current_time = None) -> bool:
        """Discard items in hand or in container"""
        agent = world.agents[agent_name]
        
        if agent.holding is not None:
            if isinstance(agent.holding, Container):
                agent.holding.contents.clear()
                return True
            else:
                agent.holding = None
                return True
        raise ValueError("No item in hand to discard")

class Agent(GameObject):
    def __init__(self, agent_name: str, x: int, y: int):
        super().__init__(agent_name, "agent", x, y)
        self.holding: Optional[Item] = None
        
        # Action queue and current action state
        self.all_action_list: List[List[Dict]] = []
        self.all_actions: List[Dict] = []

        self.action_queue: List[Dict] = []
        self.current_action: Optional[Dict] = None
        self.finish_time = 0
        self.is_idle = True
        self.all_finished = False

        self.all_execution_time = 0  # Total execution time for all actions
        self.waiting_time = 0  # Total waiting time when idle
        self.moving_time = 0  # Total time spent moving
        self.processing_time = 0  # Total time spent processing actions
    
    def reset_actions(self, actions: List[Dict]):
        self.all_actions.pop()
        self.all_action_list.append(actions)
        self.all_actions = [action for sublist in self.all_action_list for action in sublist]
        self.action_queue = actions.copy()

    def load_actions(self, actions: List[Dict]):
        self.all_action_list.append(actions)
        self.all_actions = [action for sublist in self.all_action_list for action in sublist]
        self.action_queue = actions.copy()
    
    def has_actions(self) -> bool:
        return len(self.action_queue) > 0 or not self.is_idle
    
    def start_next_action(self, current_time: int, duration: int):
        if self.action_queue:
            self.current_action = self.action_queue.pop(0)
            self.finish_time = current_time + duration
            self.is_idle = False
            if self.current_action["action"] == "MoveTo":
                self.moving_time += duration
            elif self.current_action["action"] in ["Process"]:
                self.processing_time += duration
            elif self.current_action["action"] == "Wait":
                self.waiting_time += duration
            self.all_execution_time += duration
        else:
            self.current_action = None
            self.is_idle = True

    def to_json(self):
        data = {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "current_action": self.current_action,
            "holding": None
        }
        if self.holding is not None:
            data["holding"] = self.holding.to_json()
        return data