# src/agent/method/Fixed/Fixed.py

from src.agent.model.model import Model
from src.agent.method.agent import Agent
from src.game.simulator import Simulator
from src.utils.logger_config import logger, log_model_conversation, COLOR_CODES, RESET

class FixedAgent(Agent):
    def __init__(self, model: Model|None = None, log_dir: str|None = None):
        pass

    def get_actions(self, orders, map_name):
        if orders == ["burger_basic"] and map_name == "kitchen_burger_8x6":
            return {
                    "agent1": [
                        # Task: Get bread and assemble burger
                        {"action": "MoveTo", "target": [1, 1]},         # Move to bread dispenser, cost 3, current time 3
                        {"action": "Interact", "target": "dispenser1"}, # Get bread from dispenser, cost 0, current time 3
                        {"action": "MoveTo", "target": [3, 4]},         # Move to table with plate, cost 4, current time 7
                        {"action": "Interact", "target": "table1"},     # Put bread on plate on table, cost 0, current time 7
                    ],
                    "agent2": [
                        # Task: Get meat and cook it
                        {"action": "MoveTo", "target": [2, 1]},         # Move to meat dispenser, cost 7, current time 7
                        {"action": "Interact", "target": "dispenser2"}, # Get meat from dispenser, cost 0, current time 7
                        {"action": "MoveTo", "target": [5, 1]},         # Move to chopping board, cost 3, current time 10
                        {"action": "Interact", "target": "chopping_board1"}, # Put meat on chopping board, cost 0, current time 10
                        {"action": "Process", "target": "chopping_board1"},  # Chop meat, cost 4, current time 14
                        {"action": "Interact", "target": "chopping_board1"}, # Pick up chopped meat, cost 0, current time 14
                        {"action": "MoveTo", "target": [5, 4]},         # Move to stove, cost 3, current time 17
                        {"action": "Interact", "target": "stove"},      # Put meat in pan, cost 0, current time 17, frying time 24, expected finish time 41
                        {"action": "MoveTo", "target": [3, 4]},         # Move to table with plate, cost 2, current time 19
                        {"action": "Interact", "target": "table1"},     # Pick up plate with bread, cost 0, current time 19
                        {"action": "MoveTo", "target": [5, 4]},         # Move to stove, cost 2, current time 21, meat still frying
                        {"action": "Wait", "duration": 20},             # Wait 20 time units, current time 41
                        {"action": "Interact", "target": "stove"},      # Put cooked meat on plate, cost 0, current time 41
                        {"action": "MoveTo", "target": [4, 4]},         # Move to serving window, cost 1, current time 42
                        {"action": "Interact", "target": "serving_window"}, # Serve, cost 0, current time 42
                    ]
                }
        elif orders == ["salad_advanced"] and map_name == "kitchen_salad_8x6":
            return {
                    "agent1": [
                        # Task: Get lettuce and chop it
                        {"action": "MoveTo", "target": [1, 1]},        # Move to lettuce dispenser, cost 3, current time 3
                        {"action": "Interact", "target": "dispenser1"},  # Get lettuce from dispenser, cost 0, current time 3
                        {"action": "MoveTo", "target": [3, 1]},        # Move to chopping board 1, cost 2, current time 5
                        {"action": "Interact", "target": "chopping_board1"},   # Put lettuce on chopping board 1, cost 0, current time 5
                        {"action": "Process", "target": "chopping_board1"},    # Chop lettuce, cost 4, current time 9
                        {"action": "Interact", "target": "chopping_board1"},   # Pick up chopped lettuce, cost 0, current time 9
                        
                        # Assemble salad
                        {"action": "MoveTo", "target": [5, 1]},        # Move to table with plate, cost 2, current time 11
                        {"action": "Interact", "target": "table1"},       # Put lettuce in plate on table, cost 0, current time 11
                        {"action": "Interact", "target": "table1"},      # Pick up plate, cost 0, current time 11
                        {"action": "MoveTo", "target": [4, 1]},        # Move to chopping board 2, cost 1, current time 12
                        {"action": "Wait", "duration": 1},             # Wait 1 time unit for agent2 to chop tomato, current time 13
                        {"action": "Interact", "target": "chopping_board2"},   # Put chopped tomato in plate, cost 0, current time 13

                        # Serve
                        {"action": "MoveTo", "target": [6, 1]},        # Move to serving window, cost 2, current time 15
                        {"action": "Interact", "target": "serving_window"},     # Serve, cost 0, current time 15
                    ],
                    "agent2": [
                        # Task: Get tomato and chop it
                        {"action": "MoveTo", "target": [2, 1]},        # Move to tomato dispenser, cost 7, current time 7
                        {"action": "Interact", "target": "dispenser2"},   # Get tomato from dispenser, cost 0, current time 7
                        {"action": "MoveTo", "target": [4, 1]},        # Move to chopping board 2, cost 2, current time 9
                        {"action": "Interact", "target": "chopping_board2"},   # Put tomato on chopping board 2, cost 0, current time 9
                        {"action": "Process", "target": "chopping_board2"},    # Chop tomato, cost 4, current time 13
                    ]
                }
        elif orders == ["salad_advanced", "salad_advanced"] and map_name == "kitchen_salad_8x6":
            return {
                "agent1": [
                    {"action": "MoveTo", "target": [1, 1]},
                    {"action": "Interact", "target": "dispenser1"},
                    {"action": "MoveTo", "target": [3, 1]},
                    {"action": "Interact", "target": "chopping_board1"},
                    {"action": "Process", "target": "chopping_board1"},
                    {"action": "Interact", "target": "chopping_board1"},
                    {"action": "MoveTo", "target": [5, 1]},
                    {"action": "Interact", "target": "table1"},
                    {"action": "MoveTo", "target": [2, 1]},
                    {"action": "Interact", "target": "dispenser2"},
                    {"action": "MoveTo", "target": [4, 1]},
                    {"action": "Interact", "target": "chopping_board2"},
                    {"action": "Process", "target": "chopping_board2"},
                    {"action": "Interact", "target": "chopping_board2"},
                    {"action": "MoveTo", "target": [5, 1]},
                    {"action": "Interact", "target": "table1"},
                    {"action": "Interact", "target": "table1"},
                    {"action": "MoveTo", "target": [6, 1]},
                    {"action": "Interact", "target": "serving_window"}
                ],
                "agent2": [
                    {"action": "MoveTo", "target": [1, 1]},
                    {"action": "Interact", "target": "dispenser1"},
                    {"action": "MoveTo", "target": [3, 4]},
                    {"action": "Interact", "target": "table2"},
                    {"action": "MoveTo", "target": [2, 1]},
                    {"action": "Interact", "target": "dispenser2"},
                    {"action": "MoveTo", "target": [4, 4]},
                    {"action": "Interact", "target": "table3"},
                    {"action": "Wait", "duration": 10},
                    {"action": "MoveTo", "target": [2, 4]},
                    {"action": "Interact", "target": "plate_return"},
                    {"action": "MoveTo", "target": [1, 4]},
                    {"action": "Interact", "target": "sink"},
                    {"action": "Process", "target": "sink"},
                    {"action": "Interact", "target": "sink"},
                    {"action": "MoveTo", "target": [5, 4]},
                    {"action": "Interact", "target": "table4"},
                    {"action": "MoveTo", "target": [3, 4]},
                    {"action": "Interact", "target": "table2"},
                    {"action": "MoveTo", "target": [3, 1]},
                    {"action": "Interact", "target": "chopping_board1"},
                    {"action": "Process", "target": "chopping_board1"},
                    {"action": "Interact", "target": "chopping_board1"},
                    {"action": "MoveTo", "target": [5, 4]},
                    {"action": "Interact", "target": "table4"},
                    {"action": "MoveTo", "target": [4, 4]},
                    {"action": "Interact", "target": "table3"},
                    {"action": "MoveTo", "target": [4, 1]},
                    {"action": "Interact", "target": "chopping_board2"},
                    {"action": "Process", "target": "chopping_board2"},
                    {"action": "Interact", "target": "chopping_board2"},
                    {"action": "MoveTo", "target": [5, 4]},
                    {"action": "Interact", "target": "table4"},
                    {"action": "Interact", "target": "table4"},
                    {"action": "MoveTo", "target": [6, 1]},
                    {"action": "Interact", "target": "serving_window"}
                ]
            }
        elif orders == ["sushi_fish"] and map_name == "kitchen_sushi_8x6":
            return {
                "agent1": [
                    # Task: Get fish and chop it
                    {"action": "MoveTo", "target": [1, 1]},         # Move to fish dispenser, cost 3, current time 3
                    {"action": "Interact", "target": "dispenser1"}, # Get fish from dispenser, cost 0, current time 3
                    {"action": "MoveTo", "target": [5, 1]},         # Move to chopping board, cost 2, current time 5
                    {"action": "Interact", "target": "chopping_board1"}, # Put fish on chopping board, cost 0, current time 5
                    {"action": "Process", "target": "chopping_board1"},  # Chop fish, cost 4, current time 9
                    {"action": "Interact", "target": "chopping_board1"}, # Pick up chopped fish, cost 0, current time 9
                    {"action": "MoveTo", "target": [3, 4]},         # Move to table with plate, cost 2, current time 11
                    {"action": "Interact", "target": "table1"},     # Put chopped fish on plate, cost 0, current time 11
                ],
                "agent2": [
                    # Task: Cook rice and prepare seaweed
                    {"action": "MoveTo", "target": [3, 1]},         # Move to rice dispenser, cost 7, current time 7
                    {"action": "Interact", "target": "dispenser3"}, # Get rice from dispenser, cost 0, current time 7
                    {"action": "MoveTo", "target": [5, 4]},         # Move to pot, cost 6, current time 13
                    {"action": "Interact", "target": "stove"},      # Put rice in pot, cost 0, current time 13, cooking time 16, expected finish time 29
                    {"action": "MoveTo", "target": [4, 1]},         # Move to seaweed dispenser, cost 1, current time 14
                    {"action": "Interact", "target": "dispenser4"}, # Get seaweed, cost 0, current time 14
                    {"action": "MoveTo", "target": [3, 4]},         # Move to table with plate, cost 4, current time 18
                    {"action": "Interact", "target": "table1"},     # Put seaweed on plate, cost 0, current time 18
                    {"action": "Interact", "target": "table1"},     # Pick up plate with seaweed and fish, cost 0, current time 18
                    {"action": "MoveTo", "target": [5, 4]},         # Move to pot, cost 3, current time 21, rice not ready yet
                    {"action": "Wait", "duration": 6},              # Wait 6 time units, current time 27
                    {"action": "Interact", "target": "stove"},      # Put cooked rice on plate, cost 0, current time 27
                    # Serve
                    {"action": "MoveTo", "target": [4, 4]},         # Move to serving window, cost 1, current time 28
                    {"action": "Interact", "target": "serving_window"}, # Serve, cost 0, current time 28
                ]
            }
        elif orders == ["pasta_mushroom", "pasta_tomato"] and map_name == "kitchen":
            return {
                "agent1": [
                    {"action": "MoveTo", "target": [3, 6]},
                    {"action": "Interact", "target": "dispenser5"},
                    {"action": "MoveTo", "target": [4, 6]},
                    {"action": "Interact", "target": "chopping_board2"},
                    {"action": "Process", "target": "chopping_board2"},
                    {"action": "Interact", "target": "chopping_board2"},
                    {"action": "MoveTo", "target": [1, 6]},
                    {"action": "Interact", "target": "stove2"},
                    {"action": "MoveTo", "target": [8, 5]},
                    {"action": "Interact", "target": "dispenser6"},
                    {"action": "MoveTo", "target": [2, 1]},
                    {"action": "Interact", "target": "stove3"},
                    {"action": "MoveTo", "target": [7, 1]},
                    {"action": "Interact", "target": "dispenser2"},
                    {"action": "MoveTo", "target": [4, 6]},
                    {"action": "Interact", "target": "chopping_board2"},
                    {"action": "Process", "target": "chopping_board2"},
                    {"action": "Interact", "target": "chopping_board2"},
                    {"action": "MoveTo", "target": [1, 6]},
                    {"action": "Interact", "target": "stove2"}
                    ],
                "agent2": [
                    {"action": "MoveTo", "target": [8, 5]},
                    {"action": "Interact", "target": "dispenser6"},
                    {"action": "MoveTo", "target": [1, 4]},
                    {"action": "Interact", "target": "stove4"},
                    {"action": "MoveTo", "target": [4, 5]},
                    {"action": "Interact", "target": "table1"},
                    {"action": "MoveTo", "target": [1, 4]},
                    {"action": "Wait", "duration": 8},
                    {"action": "Interact", "target": "stove4"},
                    {"action": "MoveTo", "target": [1, 6]},
                    {"action": "Interact", "target": "stove2"},
                    {"action": "MoveTo", "target": [2, 6]},
                    {"action": "Interact", "target": "serving_window"},
                    {"action": "MoveTo", "target": [6, 3]},
                    {"action": "Interact", "target": "table2"},
                    {"action": "MoveTo", "target": [2, 1]},
                    {"action": "Interact", "target": "stove3"},
                    {"action": "MoveTo", "target": [1, 6]},
                    {"action": "Wait", "duration": 13},
                    {"action": "Interact", "target": "stove2"},
                    {"action": "MoveTo", "target": [2, 6]},
                    {"action": "Interact", "target": "serving_window"}
                ]
            }
        else:
            raise ValueError(f"Unknown orders: {orders}, map: {map_name}")
    
    def run_test(self, simulator: Simulator, recipes: list, examples: list = [], retries=3) -> dict:
        world = simulator.world
        plan = self.get_actions(world.orders, world.map_data["name"])
        log_model_conversation(f"{COLOR_CODES['YELLOW']}Fixed plan: {plan}{RESET}")
        simulator.load_plan(plan)
        simulator.run_simulation()
        return self.create_result(simulator, 0)