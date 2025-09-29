from src.agent.model.model import Model
from src.agent.method.agent import Agent
from src.agent.method.ReAct.instruction import INSTRUCTION, REFINE_INSTRUCTION
from src.game.const import *
from src.game.world_state import World
from src.game.simulator import Simulator
from src.utils.logger_config import logger, COLOR_CODES, RESET

import json
from copy import deepcopy

class ReActAgent(Agent):
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
        self.chat_history = messages.copy()

    def run_test(self, simulator: Simulator, recipes: list, examples: list = [], retries=3) -> dict:
        self.initiate_chat(examples)

        world = simulator.world
        prompt = f"Map JSON:\n{json.dumps(world.map_data)}\n\nRecipes:\n{recipes}\n\nOrders:\n{str(world.orders)}"
        plan = self.get_actions(prompt)
        logger.info(f"{COLOR_CODES['BLUE']}initial plan: {json.dumps(plan, indent=2)}{RESET}")

        finished_agents = set()
        simulator.load_plan(plan)

        current_agent_plans = {name: [] for (name, agent) in simulator.world.agents.items()}
        for name, actions in plan.items():
            current_agent_plans[name].extend(actions)

        count_max = 0
        while len(finished_agents) < len(simulator.world.agents):
            count = 0
            simulator_copy = deepcopy(simulator)
            print("Fuck=================================================================")
            while count < retries:
                try:
                    have_agent_finished = False
                    while not have_agent_finished:
                        have_agent_finished = simulator.step()
                        if len(world.orders) == 0:
                            break
                    while have_agent_finished:
                        have_agent_finished = False
                        agent_state = simulator.status()
                        world_json = simulator.world.to_json()
                        obs = f"{agent_state}\nCurrent World State:\n{world_json}\n"
                        
                        plan = self.get_actions(f"Observation:\n{obs}\n")
                        logger.info(f"{COLOR_CODES['BLUE']}next actions: {plan}{RESET}")
                        for agent_name, next_action in plan.items():
                            if agent_name in finished_agents:
                                continue
                            for agent in simulator.world.agents.values():
                                if agent.name == agent_name:
                                    if next_action and len(next_action) > 0 and next_action[0].get("action") == "Finish":
                                        agent.all_finished = True
                                        finished_agents.add(agent_name)
                                    else:
                                        agent.load_actions(next_action)
                                        simulator.assign_next_action(agent_name)
                                        while agent.finish_time == simulator.current_time and not agent.is_idle:
                                            simulator.complete_current_action(agent_name)
                                            simulator.assign_next_action(agent_name)
                                        if not agent.all_finished and len(agent.action_queue) == 0 and agent.is_idle:
                                            have_agent_finished = True
                        simulator.update_event_queue()
                    break
                except Exception as e:
                    logger.error(f"{COLOR_CODES['RED']}Simulation error on attempt {count+1}: {e}{RESET}")
                    count += 1
                    count_max = max(count_max, count)
                    if count == retries:
                        return self.create_result(simulator, count_max, error_msg=str(e))
                    prompt = self.REFINE_INSTRUCTION.format(error=str(e), world_json=simulator.world.to_json())
                    plan = self.get_actions(prompt)
                    logger.info(f"{COLOR_CODES['BLUE']}plan after refinement: {json.dumps(plan, indent=2)}{RESET}")
                    simulator = deepcopy(simulator_copy)
                    world = simulator.world
                    simulator.reset_plan(plan)

            print("==================================== ", len(world.orders))
            
            if len(world.orders) == 0:
                break

        return self.create_result(simulator, count_max)