import os
import requests
from src.agent.model.model import Model, PredictConfig
from src.utils.logger_config import logger, COLOR_CODES, RESET
from openai import OpenAI
from transformers import AutoTokenizer


class DeepSeekWrapper(Model):
    def __init__(self, name="DeepSeek-V3.1", ip=None, port=None, tokenizer_model="deepseek-ai/DeepSeek-v3.1"):
        super().__init__(name=name)
        self.ip = ip or os.environ.get("DEEPSEEK_IP", "29.127.51.15")
        self.port = port or int(os.environ.get("DEEPSEEK_PORT", 8081))
        self.tokenizer_model = tokenizer_model
        self.is_chat_model = True

        self.client = OpenAI(base_url=f"http://{self.ip}:{self.port}/v1", api_key="local")
        if tokenizer_model is not None:
            self.client.tokenizer = AutoTokenizer.from_pretrained(tokenizer_model)
        else:
            self.client.tokenizer = AutoTokenizer.from_pretrained(self.name)

    def predict(self, config: PredictConfig) -> str:
        prompt = config.prompt
        retries = config.retries
        delay = config.delay
        messages = config.messages
        attempt = 0
        system_prompt = config.system_prompt
        if messages is None:
            messages=[
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        kwargs = {
            "model": self.name,
            "messages": messages,
            "temperature": config.temperature,
            "top_k": 1,
            "stream": False,
            "repetition_penalty": 1,
            "stream": True,
            "extra_body": {"chat_template_kwargs": {"thinking": True}}
        }
        if config.top_p is not None:
            kwargs["top_p"] = config.top_p,
        if config.max_tokens is not None:
            kwargs["max_completion_tokens"] = config.max_tokens,
        if config.response_format is not None:
            kwargs["response_format"] = config.response_format

        while attempt < retries:
            try:
                stream = self.client.chat.completions.create(**kwargs)
                response = ""
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        response += content
                break
            except Exception as e:
                logger.error(f"Error: {COLOR_CODES['RED']}{e}{RESET}")
                attempt += 1
                if attempt < retries:
                    logger.info(f"Retrying in {delay} seconds.")
                    import time
                    time.sleep(delay)
                else:
                    logger.error(f"All {retries} attempts failed.")
                    raise e
        self.log_conversation(messages, response, log_file=f"logs/{self.name}_conversation.txt")
        return response

def main():
    model = DeepSeekWrapper()
    prompt = "What's the answer to life the universe and everything"
    config = PredictConfig(prompt=prompt, temperature=1.0)
    response = model.predict(config)
    print(response)

if __name__ == "__main__":
    main()