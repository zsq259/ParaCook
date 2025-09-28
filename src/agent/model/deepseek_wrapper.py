import os
import requests
from src.agent.model.model import Model, PredictConfig
from src.utils.logger_config import logger, COLOR_CODES, RESET

class DeepSeekWrapper(Model):
    def __init__(self, name="DeepSeek-V3", ip=None, port=None):
        super().__init__(name=name)
        self.ip = ip or os.environ.get("DEEPSEEK_IP", "28.12.131.215")
        self.port = port or int(os.environ.get("DEEPSEEK_PORT", 8081))
        self.is_chat_model = True

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
            "repetition_penalty": 1
        }
        if config.top_p is not None:
            kwargs["top_p"] = config.top_p,
        if config.max_tokens is not None:
            kwargs["max_completion_tokens"] = config.max_tokens,
        if config.response_format is not None:
            kwargs["response_format"] = config.response_format
        
        while attempt < retries:
            try:
                headers = {"Content-Type": "application/json"}
                url = f"http://{self.ip}:{self.port}/v1/chat/completions"
                resp = requests.post(url, headers=headers, json=kwargs)
                resp.raise_for_status()
                pred = resp.json()['choices'][0]['message']['content']
                self.log_conversation(messages, pred, log_file=f"logs/{self.name}_conversation.txt")
                response = pred
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