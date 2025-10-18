# Base class for all agents
import os, datetime

from src.agent.model.model import Model, PredictConfig
from src.utils.utils import extract_json
from src.utils.logger_config import logger, log_model_conversation, COLOR_CODES, RESET

class Agent:
    def __init__(self, model: Model | None = None, log_dir: str | None = None):
        self.model = model
        self.chat_history = []
        self.log_dir = log_dir
        self.log_initiated = False

    def log_conversation(self, log_file="model.log", full: bool = False) -> None:
        """Log the conversation to a file."""
        if not self.log_dir or not self.model:
            return
        
        log_path = os.path.join(self.log_dir, log_file)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        model_name = self.model.name
        log_content = f"\n===== {timestamp} ({model_name}) =====\n"
        if full:
            for message in self.chat_history:
                role = message.get("role", "unknown")
                content = message.get("content", "")
                log_content += f"-----{role.upper()}:-----\n{content}\n\n"
        else:
            last_assistant_idx = -1
            for i in range(len(self.chat_history)-1, -1, -1):
                if self.chat_history[i].get("role") == "assistant":
                    last_assistant_idx = i
                    break
            for i in range(last_assistant_idx - 1, len(self.chat_history)):
                role = self.chat_history[i].get("role", "unknown")
                content = self.chat_history[i].get("content", "")
                log_content += f"-----{role.upper()}:-----\n{content}\n\n"
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_content)
        logger.info(f"Logged conversation to {log_path}")

    def chat(self, user_input: str, chat_history=None) -> str:
        if not self.model:
            raise ValueError("Model is not defined for this agent to chat.")
        if chat_history:
            self.chat_history = chat_history
        self.chat_history.append({"role": "user", "content": user_input})
        response = self.model.predict(PredictConfig(messages=self.chat_history, temperature=0, response_format={ "type": "json_object" }))
        self.chat_history.append({"role": "assistant", "content": response})

        self.log_conversation(full=not self.log_initiated)
        self.log_initiated = True
        return response

    def get_actions(self, prompt: str) -> dict:
        response = self.chat(prompt)
        log_model_conversation(f"{COLOR_CODES['YELLOW']}Model output: {response}{RESET}")
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