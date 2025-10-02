from src.agent.model.model import Model
from src.agent.method.agent import Agent
from src.game.const import *
from src.game.world_state import World
from src.game.simulator import Simulator
from src.utils.logger_config import logger, COLOR_CODES, RESET

import json
from copy import deepcopy
import subprocess
import sys
import os
import time

class HumanAgent(Agent):
    def __init__(self, model: Model):
        super().__init__(model)
       
    def run_test(self, simulator: Simulator, recipes: list, examples: list = [], retries=3) -> dict:
        """
        Start a GUI for human interaction to control agents in the simulator.
        """
        world = simulator.world
        actions_path = "tmp/actions.json"
        if os.path.exists(actions_path):
            os.remove(actions_path)
        if os.path.exists('tmp/world.json'):
            os.remove('tmp/world.json')

        gui_path = os.path.join(os.path.dirname(__file__), '../../../game/gui.py')
        gui_path = os.path.abspath(gui_path)
        recipes_str = "\n"
        for r in recipes:
            recipes_str += f"- {r}\n"

        cmd = [
            sys.executable, '-m', 'streamlit', 'run', gui_path,
            '--', '--recipes', recipes_str,
            '--orders', str(world.orders),
            "--map_data", json.dumps(world.map_data, ensure_ascii=False)
        ]
        print(f"Starting GUI: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd)

        last_actions = None

        simulator_copy = deepcopy(simulator)

        while proc.poll() is None:
            if os.path.exists(actions_path):
                try:
                    with open(actions_path, "r", encoding="utf-8") as f:
                        actions = f.read()
                    if actions and actions != last_actions:
                        last_actions = actions
                        # Clear log file
                        with open('tmp/log.txt', 'w', encoding='utf-8') as log_f:
                            log_f.write("")
                        # Reload simulator and run with new actions
                        simulator = deepcopy(simulator_copy)
                        world = simulator.world
                        simulator.load_plan(json.loads(actions))
                        simulator.run_simulation()
                        with open("tmp/world.json", "w", encoding="utf-8") as wf:
                            json.dump(simulator.world.to_json(), wf, ensure_ascii=False, indent=2)
                        
                        if len(world.orders) == 0:
                            return self.create_result(simulator, 0)


                except Exception as e:
                    print(f"Failed to read actions.json: {e}")
            time.sleep(1)
        return self.create_result(simulator, 0)
       