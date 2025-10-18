from src.agent.model.model import Model
from src.agent.method.agent import Agent
from src.agent.method.ReAct.instruction import INSTRUCTION, REFINE_INSTRUCTION
from src.game.const import *
from src.game.world_state import World
from src.game.simulator import Simulator
from src.utils.logger_config import logger, log_model_conversation, COLOR_CODES, RESET

import json
from copy import deepcopy

class ReActAgent(Agent):
    def __init__(self, model: Model, log_dir: str):
        super().__init__(model, log_dir)
        self.INSTRUCTION = INSTRUCTION
        self.REFINE_INSTRUCTION = REFINE_INSTRUCTION

    def initiate_chat(self, examples: list = []):
        messages = [
            {"role": "system", "content": self.INSTRUCTION.format(
                INTERACT_TIME=INTERACT_TIME,
                PROCESS_CUT_TIME=PROCESS_CUT_TIME,
                PROCESS_POT_COOK_TIME=PROCESS_POT_COOK_TIME,
                PROCESS_PAN_COOK_TIME=PROCESS_PAN_COOK_TIME,
                PROCESS_WASH_PLATE_TIME=PROCESS_WASH_PLATE_TIME,
                RETURN_DIRTY_PLATE_TIME=RETURN_DIRTY_PLATE_TIME,
            )},
        ]
        self.chat_history = messages.copy()

    def run_test(self, simulator: Simulator, recipes: list, examples: list = [], retries=3) -> dict:
        self.initiate_chat(examples)

        world = simulator.world
        prompt = None
        count_max = 0
        while len(simulator.get_finished_agents()) < len(simulator.world.agents) and not simulator.is_done():
            count = 0
            simulator_copy = deepcopy(simulator)
            while count < retries:
                try:
                    if not prompt:
                        prompt = f"Map JSON:\n{json.dumps(world.map_data)}\n\nRecipes:\n{recipes}\n\nOrders:\n{str(world.orders)}"
                    else:
                        prompt = f"Observation:\n{simulator.status()}\nCurrent World State:\n{simulator.world.to_json()}\n"
                    plan = self.get_actions(prompt)
                    log_model_conversation(f"{COLOR_CODES['BLUE']}next actions: {json.dumps(plan, indent=2)}{RESET}")
                    simulator.submit_plan(plan)
                    simulator.next_decision_step()
                    break
                except Exception as e:
                    logger.error(f"{COLOR_CODES['RED']}Simulation error on attempt {count+1}: {e}{RESET}")
                    count += 1
                    count_max = max(count_max, count)
                    if count == retries:
                        return self.create_result(simulator, count_max, error_msg=str(e))
                    prompt = self.REFINE_INSTRUCTION.format(error=str(e), world_json=simulator.world.to_json())
                    plan = self.get_actions(prompt)
                    log_model_conversation(f"{COLOR_CODES['BLUE']}plan after refinement: {json.dumps(plan, indent=2)}{RESET}")
                    simulator = deepcopy(simulator_copy)
                    world = simulator.world
                    simulator.rollback_plan()
                    simulator.submit_plan(plan)
                    simulator.next_decision_step()
            
            if len(world.orders) == 0:
                break

        return self.create_result(simulator, count_max)