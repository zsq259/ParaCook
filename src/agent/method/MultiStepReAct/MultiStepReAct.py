from src.agent.model.model import Model
from src.agent.method.ReAct.ReAct import ReActAgent
from src.agent.method.MultiStepReAct.instruction import INSTRUCTION, REFINE_INSTRUCTION
from src.game.const import *


class MultiStepReActAgent(ReActAgent):
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
        for ex in examples:
            ex_mod = __import__(f"src.agent.method.MultiStepReAct.example.{ex}", fromlist=['input', 'output'])
            messages.append({"role": "user", "content": ex_mod.input})
            messages.append({"role": "assistant", "content": ex_mod.output})

        self.chat_history = messages.copy()
