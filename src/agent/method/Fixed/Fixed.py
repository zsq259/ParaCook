# src/agent/method/Fixed/Fixed.py

from src.agent.model.model import Model
from src.agent.method.agent import Agent
from src.game.world_state import World
from src.game.simulator import Simulator
from src.utils.logger_config import logger, COLOR_CODES, RESET

class FixedAgent(Agent):
    def __init__(self, model: Model|None = None):
        pass

    def get_actions(self, orders, map_name):
        if orders == ["burger_basic"] and map_name == "kitchen_burger_8x6":
            return {
                    "agent1": [
                        # 任务：获取面包并组装汉堡
                        {"action": "MoveTo", "target": [1, 1]},         # 移动到面包分配器旁边，耗时3，当前时间3
                        {"action": "Interact", "target": "dispenser1"}, # 从分配器获取面包，耗时0，当前时间3
                        {"action": "MoveTo", "target": [3, 4]},         # 移动到有盘子的桌子旁，耗时4，当前时间7
                        {"action": "Interact", "target": "table1"},     # 将面包放入桌上的盘子，耗时0，当前时间7
                    ],
                    "agent2": [
                        # 任务：获取肉并煎熟
                        {"action": "MoveTo", "target": [2, 1]},         # 移动到肉分配器旁边，耗时7，当前时间7
                        {"action": "Interact", "target": "dispenser2"}, # 从分配器获取肉，耗时0，当前时间7
                        {"action": "MoveTo", "target": [5, 1]},         # 移动到切菜台旁边，耗时3，当前时间10
                        {"action": "Interact", "target": "chopping_board1"}, # 将肉放到切菜台上，耗时0，当前时间10
                        {"action": "Process", "target": "chopping_board1"},  # 切肉，耗时4，当前时间14
                        {"action": "Interact", "target": "chopping_board1"}, # 拿起切好的肉，耗时0，当前时间14
                        {"action": "MoveTo", "target": [5, 4]},         # 移动到炉灶旁边，耗时3，当前时间17
                        {"action": "Interact", "target": "stove"},      # 将肉放入锅中，耗时0，当前时间17，煎肉时间24，预计完成时间41
                        {"action": "MoveTo", "target": [3, 4]},         # 移动到有盘子的桌子旁，耗时2，当前时间19
                        {"action": "Interact", "target": "table1"},     # 拿起装有面包的盘子，耗时0，当前时间19
                        {"action": "MoveTo", "target": [5, 4]},         # 移动到炉灶旁边，耗时2，当前时间21，此时肉还在煎
                        {"action": "Wait", "duration": 20},             # 等待20时间单位，当前时间41
                        {"action": "Interact", "target": "stove"},      # 将煎好的肉放入盘子，耗时0，当前时间41
                        {"action": "MoveTo", "target": [4, 4]},         # 移动到上菜窗口旁，耗时1，当前时间42
                        {"action": "Interact", "target": "serving_window"}, # 上菜，耗时0，当前时间42
                    ]
                }
        elif orders == ["salad_advanced"] and map_name == "kitchen_salad_8x6":
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
            {"action": "Interact", "target": "table1"},
            {"action": "MoveTo", "target": [4, 1]},
            {"action": "Wait", "duration": 1},
            {"action": "Interact", "target": "chopping_board2"},
            {"action": "MoveTo", "target": [6, 1]},
            {"action": "Interact", "target": "serving_window"},
            {"action": "Finish"}
        ],
        "agent2": [
            {"action": "MoveTo", "target": [2, 1]},
            {"action": "Interact", "target": "dispenser2"},
            {"action": "MoveTo", "target": [4, 1]},
            {"action": "Interact", "target": "chopping_board2"},
            {"action": "Process", "target": "chopping_board2"},
        ]
    }
            return {
                    "agent1": [
                        # 任务：获取生菜并切碎
                        {"action": "MoveTo", "target": [1, 1]},        # 移动到生菜分配器旁边，耗时3，当前时间3
                        {"action": "Interact", "target": "dispenser1"},  # 从分配器获取生菜，耗时0，当前时间3
                        {"action": "MoveTo", "target": [3, 1]},        # 移动到切菜台1旁边，耗时2，当前时间5
                        {"action": "Interact", "target": "chopping_board1"},   # 将生菜放到切菜台1上，耗时0，当前时间5
                        {"action": "Process", "target": "chopping_board1"},    # 切生菜，耗时4，当前时间9
                        {"action": "Interact", "target": "chopping_board1"},   # 拿起切好的生菜，耗时0，当前时间9
                        
                        # 组装沙拉
                        {"action": "MoveTo", "target": [5, 1]},        # 移动到有盘子的桌子旁，耗时2，当前时间11
                        {"action": "Interact", "target": "table1"},       # 将手上的生菜放入桌上的盘子，耗时0，当前时间11
                        {"action": "Interact", "target": "table1"},      # 拿起盘子，耗时0，当前时间11
                        {"action": "MoveTo", "target": [4, 1]},        # 移动到切菜台2旁，耗时1，当前时间12
                        {"action": "Wait", "duration": 1},             # 等待1时间单位，等待agent2切好番茄，当前时间13
                        {"action": "Interact", "target": "chopping_board2"},   # 将切好的番茄放入盘子，耗时0，当前时间13

                        # 上菜
                        {"action": "MoveTo", "target": [6, 1]},        # 移动到上菜窗口旁，耗时2，当前时间15
                        {"action": "Interact", "target": "serving_window"},     # 上菜，耗时0，当前时间15
                    ],
                    "agent2": [
                        # 任务：获取番茄并切碎
                        {"action": "MoveTo", "target": [2, 1]},        # 移动到番茄分配器旁边，耗时7，当前时间7
                        {"action": "Interact", "target": "dispenser2"},   # 从分配器获取番茄，耗时0，当前时间7
                        {"action": "MoveTo", "target": [4, 1]},        # 移动到切菜台2旁边，耗时2，当前时间9
                        {"action": "Interact", "target": "chopping_board2"},   # 将番茄放到切菜台2上，耗时0，当前时间9
                        {"action": "Process", "target": "chopping_board2"},    # 切番茄，耗时4，当前时间13
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
                    # 任务：获取鱼并切碎
                    {"action": "MoveTo", "target": [1, 1]},         # 移动到鱼分配器旁边，耗时3，当前时间3
                    {"action": "Interact", "target": "dispenser1"}, # 从分配器获取鱼，耗时0，当前时间3
                    {"action": "MoveTo", "target": [5, 1]},         # 移动到切菜台旁边，耗时2，当前时间5
                    {"action": "Interact", "target": "chopping_board1"}, # 将鱼放到切菜台上，耗时0，当前时间5
                    {"action": "Process", "target": "chopping_board1"},  # 切鱼，耗时4，当前时间9
                    {"action": "Interact", "target": "chopping_board1"}, # 拿起切好的鱼，耗时0，当前时间9
                    {"action": "MoveTo", "target": [3, 4]},         # 移动到有盘子的桌子旁，耗时2，当前时间11
                    {"action": "Interact", "target": "table1"},     # 将切好的鱼放入盘子，耗时0，当前时间11
                ],
                "agent2": [
                    # 任务：煮米饭并准备紫菜
                    {"action": "MoveTo", "target": [3, 1]},         # 移动到米饭分配器旁边，耗时7，当前时间7
                    {"action": "Interact", "target": "dispenser3"}, # 从分配器获取米饭，耗时0，当前时间7
                    {"action": "MoveTo", "target": [5, 4]},         # 移动到锅旁边，耗时6，当前时间13
                    {"action": "Interact", "target": "stove"},      # 将米饭放入锅中，耗时0，当前时间13，煮饭时间16，预计完成时间29
                    {"action": "MoveTo", "target": [4, 1]},         # 移动到紫菜分配器旁边，耗时1，当前时间14
                    {"action": "Interact", "target": "dispenser4"}, # 获取紫菜，耗时0，当前时间14
                    {"action": "MoveTo", "target": [3, 4]},         # 移动到有盘子的桌子旁，耗时4，当前时间18
                    {"action": "Interact", "target": "table1"},     # 将紫菜放入盘子，耗时0，当前时间18
                    {"action": "Interact", "target": "table1"},     # 拿起装有紫菜和鱼的盘子，耗时0，当前时间18
                    {"action": "MoveTo", "target": [5, 4]},         # 移动到锅旁边，耗时3，当前时间21，此时米饭还未煮好
                    {"action": "Wait", "duration": 8},              # 等待8时间单位，当前时间29
                    {"action": "Interact", "target": "stove"},      # 将煮好的米饭放入盘子，耗时0，当前时间29
                    # 上菜
                    {"action": "MoveTo", "target": [4, 4]},         # 移动到上菜窗口旁，耗时1，当前时间30
                    {"action": "Interact", "target": "serving_window"}, # 上菜，耗时0，当前时间30
                ]
            }
        else:
            raise ValueError(f"未知订单: {orders}")
    
    def run_test(self, world: World, simulator: Simulator, recipes: list, examples: list = [], retries=3) -> dict:
        plan = self.get_actions(world.orders, world.map_data["name"])
        logger.info(f"{COLOR_CODES['YELLOW']}Fixed plan: {plan}{RESET}")
        simulator.load_plan(plan)
        simulator.run_simulation()
        return {}