from src.agent.model.model import Model
from src.agent.method.agent import Agent
from src.agent.method.IO.instruction import INSTRUCTION, REFINE_INSTRUCTION
from src.game.const import *
from src.game.world_state import World
from src.game.simulator import Simulator
from src.utils.logger_config import logger, COLOR_CODES, RESET

import json
from copy import deepcopy

class IOAgent(Agent):
    def __init__(self, model: Model):
        super().__init__(model)
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
        for ex in examples:
            ex_mod = __import__(f"src.agent.method.IO.example.{ex}", fromlist=['input', 'output'])
            messages.append({"role": "user", "content": ex_mod.input})
            messages.append({"role": "assistant", "content": ex_mod.output})

        self.chat_history = messages.copy()

    def run_test(self, simulator: Simulator, recipes: list, examples: list = [], retries=3) -> dict:
        """Run test with the given world and simulator, using the provided examples for context."""
        self.initiate_chat(examples)
        world = simulator.world
        prompt = f"Map JSON:\n{json.dumps(world.map_data)}\n\nRecipes:\n{recipes}\n\nOrders:\n{str(world.orders)}"
        plan = self.get_actions(prompt)
        logger.info(f"{COLOR_CODES['BLUE']}final plan: {plan}{RESET}")

        count = 0
        simulator_copy = deepcopy(simulator)
        while count < retries:
            simulator = deepcopy(simulator_copy)
            world = simulator.world
            simulator.load_plan(plan)
            try:
                simulator.run_simulation()
                break
            except Exception as e:
                logger.error(f"{COLOR_CODES['RED']}Simulation error on attempt {count+1}: {e}{RESET}")
                count += 1
                if count == retries:
                    return self.create_result(simulator, count, plan, str(e))
                prompt = self.REFINE_INSTRUCTION.format(error=str(e), world_json=simulator.world.to_json())
                plan = self.get_actions(prompt)
                logger.info(f"{COLOR_CODES['BLUE']}plan after refinement: {plan}{RESET}")

        return self.create_result(simulator, count, plan)