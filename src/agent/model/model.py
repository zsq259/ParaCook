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