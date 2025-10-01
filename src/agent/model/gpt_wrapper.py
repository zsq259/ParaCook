from itertools import tee
from pyexpat import model
import os, time
from openai import OpenAI, OpenAIError
from src.agent.model.model import Model, PredictConfig
from src.utils.logger_config import logger, COLOR_CODES, RESET

class GPTWrapper(Model):
    def __init__(self, name):
        super().__init__(name=name)
        if "deepseek" in name.lower():
            self.openai_api_key = os.environ.get("DEEPSEEK_API_KEY")
            self.openai_base_url = os.environ.get("DEEPSEEK_BASE_URL")
            self.is_chat_model = True
        elif "claude" in name.lower():
            self.openai_api_key = os.environ.get("CLAUDE_API_KEY")
            self.openai_base_url = os.environ.get("CLAUDE_BASE_URL")
            self.is_chat_model = True
        elif "gemini" in name.lower():
            self.openai_api_key = os.environ.get("GEMINI_API_KEY")
            self.openai_base_url = os.environ.get("GEMINI_BASE_URL")
            self.is_chat_model = True
        elif "qwen" in name.lower():
            self.openai_api_key = os.environ.get("DASHSCOPE_API_KEY")
            self.openai_base_url = os.environ.get("DASHSCOPE_BASE_URL")
            self.is_chat_model = True
        else:
            self.openai_api_key = os.environ.get("OPENAI_API_KEY")
            self.openai_base_url = os.environ.get("OPENAI_BASE_URL")
            self.is_chat_model = True
        
    def chat_create(self, client, config: PredictConfig) -> str:
        prompt = config.prompt
        stop = config.stop
        system_prompt = config.system_prompt
        messages = config.messages
        if messages is None:
            messages=[
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        kwargs = {
            "model": self.name,
            "messages": messages,
            "temperature": config.temperature,
            "stop": stop
        }
        if config.top_p is not None:
            kwargs["top_p"] = config.top_p,
        if config.max_tokens is not None:
            kwargs["max_completion_tokens"] = config.max_tokens,
        if config.response_format is not None:
            kwargs["response_format"] = config.response_format
        response = client.chat.completions.create(**kwargs)
        logger.info(f"{COLOR_CODES['PURPLE']}Usage: {response.usage}{RESET}")
        self.log_conversation(messages, response.choices[0].message.content)
        return response.choices[0].message.content
    
    def create(self, client, config: PredictConfig) -> str:
        raise NotImplementedError("Not implemented.")
    
    def predict(self, config: PredictConfig) -> str:
        prompt = config.prompt
        stop = config.stop
        retries = config.retries
        delay = config.delay
        messages = config.messages
        attempt = 0

        if self.name == "gpt-5":
            config.temperature = 1
        if "deepseek" in self.name.lower():
            config.max_tokens = 64000
        while attempt < retries:
            try:
                client = OpenAI(base_url=self.openai_base_url, api_key=self.openai_api_key)
                if self.is_chat_model:
                    response = self.chat_create(client, config)
                    break
                else :
                    response = self.create(client, config)
                    break
            except OpenAIError as e:
                logger.error(f"Error: {COLOR_CODES['RED']}{e}{RESET}")
                attempt += 1
                if attempt < retries:
                    logger.info(f"Retrying in {delay} seconds.")
                    time.sleep(delay)
                else:
                    logger.error(f"All {retries} attempts failed.")
                    raise e
            except Exception as e:
                logger.error(f"Unexpected error: {COLOR_CODES['RED']}{e}{RESET}")
                raise e
        if messages is None:
            messages=[
                {"role": "system", "content": config.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        self.log_conversation(messages, response, log_file=f"logs/{self.name}_conversation.txt")
        return response
    
def main():
    
    model = GPTWrapper(name="gpt-5")
    prompt = "Please introduce gpt-5"
    # response = model.predict(prompt)
    config = PredictConfig(prompt=prompt, temperature=1)
    response = model.predict(config)
    print(response)

if __name__ == "__main__":
    main()