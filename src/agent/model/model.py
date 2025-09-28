from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import datetime
from typing import Any
from src.utils.logger_config import logger

@dataclass
class PredictConfig:
    prompt: str | None = None
    stop: Any = None
    max_tokens: int | None = None
    retries: int = 3
    delay: int = 2
    system_prompt: str | None = None
    messages: Any = None
    temperature: float = 0.2
    top_p: float | None = None
    response_format: dict | None = None

class Model(ABC):
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def predict(self, config: PredictConfig) -> str: ...
        
    def log_conversation(self, messages, response, log_file=None):
        if log_file is None:
            today = datetime.datetime.now().strftime("%Y%m%d")
            log_file = f"logs/conversations_{today}.txt"
        if not os.path.exists(log_file):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        model_name = self.name or "Unknown Model"
        log_content = f"\n--- {timestamp} ({model_name}) ---\n"
        # log_content += f"System Prompt:\n {system_prompt}\n"
        # log_content += f"User:\n {prompt}\n"
        for msg in messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            log_content += f"{role}:\n {content}\n"
        log_content += f"Model:\n {response}\n"
        log_content += "-" * 40 + "\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_content)
        
        logger.info(f"Logged conversation to {log_file}")
        
        return log_file