# Base class for all agents
from src.agent.model.model import Model, PredictConfig
from src.utils.utils import extract_json
from src.utils.logger_config import logger, COLOR_CODES, RESET

class Agent:
    def __init__(self, model: Model):
        self.model = model
        self.chat_history = []

    def chat(self, user_input: str, chat_history=None) -> str:
        if chat_history:
            self.chat_history = chat_history
        self.chat_history.append({"role": "user", "content": user_input})
        response = self.model.predict(PredictConfig(messages=self.chat_history, temperature=0, response_format={ "type": "json_object" }))
        self.chat_history.append({"role": "assistant", "content": response})
        return response

    def get_actions(self, prompt: str) -> dict:
        response = self.chat(prompt)
        logger.info(f"{COLOR_CODES['YELLOW']}Model output: {response}{RESET}")
        if not isinstance(response, str):
            raise ValueError("Model response is not a string.")
        try:
            actions = extract_json(response)
            if not isinstance(actions, dict):
                raise ValueError("Extracted actions is not a dictionary.")
            if "plan" in actions:
                actions = actions["plan"]
        except Exception as e:
            logger.error(f"{COLOR_CODES['RED']}Failed to parse model output as JSON: {e}{RESET}")
            logger.error(f"{COLOR_CODES['RED']}Original model output: {response}{RESET}")
            raise ValueError("Failed to parse model output as JSON.") from e
        return actions
    
    def create_result(self, simulator, retry_count: int, plan: dict|None = None, error_msg: str|None = None) -> dict:
        world = simulator.world
        return {
            "done": len(world.orders) == 0 if error_msg is None else False,
            "time": simulator.current_time,
            "finished_orders": world.finished_orders,
            "remaining_orders": world.orders,
            "agent_progress": {
                name: f"{len(agent.all_actions) - len(agent.action_queue)}/{len(agent.all_actions)}"
                for (name, agent) in simulator.world.agents.items()
            },
            "agent_all_execution_time": {
                name: agent.all_execution_time for (name, agent) in simulator.world.agents.items()
            },
            "agent_waiting_time": {
                name: agent.waiting_time for (name, agent) in simulator.world.agents.items()
            },
            "agent_moving_time": {
                name: agent.moving_time for (name, agent) in simulator.world.agents.items()
            },
            "agent_processing_time": {
                name: agent.processing_time for (name, agent) in simulator.world.agents.items()
            },
            "error": error_msg,
            "retry_count": retry_count,
            "plan": { name: agent.all_actions for (name, agent) in simulator.world.agents.items() } if plan is None else plan
        }