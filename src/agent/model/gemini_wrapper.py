import os
import time
from google import genai
from google.genai import types
from src.agent.model.model import Model, PredictConfig
from src.utils.logger_config import logger, COLOR_CODES, RESET

class GeminiWrapper(Model):
    def __init__(self, name):
        super().__init__(name=name)
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.is_chat_model = True
        self.client = genai.Client(api_key=self.api_key)
        self.cache = None
    
    def init_cache(self, system_prompt: str):
        self.cache = self.client.caches.create(
            model=self.name,
            config=types.CreateCachedContentConfig(
                system_instruction=system_prompt,
            )
        )
        print(f'{self.cache=}')
    
    def predict(self, config: PredictConfig) -> str:

        prompt = config.prompt
        system_prompt = config.system_prompt
        messages = config.messages
        temperature = config.temperature
        top_p = config.top_p
        max_tokens = config.max_tokens
        retries = config.retries or 3
        delay = config.delay or 1
        attempt = 0
        response = ""
        
        if messages is None:
            if system_prompt:
                content = f"System: {system_prompt}\nUser: {prompt}"
            else:
                content = prompt
        else:
            content_parts = []
            if messages[0].get("role") == "system":
                system_prompt = messages[0].get("content")
                messages = messages[1:]
            for msg in messages:
                role = msg.get("role", "user")
                msg_content = msg.get("content", "")
                if role == "system":
                    content_parts.append(f"System: {msg_content}")
                elif role == "user":
                    content_parts.append(f"User: {msg_content}")
                elif role == "assistant":
                    content_parts.append(f"Assistant: {msg_content}")
            content = "\n".join(content_parts)

        config_kwargs = {}
        if temperature is not None:
            config_kwargs["temperature"] = temperature
        if top_p is not None:
            config_kwargs["top_p"] = top_p
        if max_tokens is not None:
            config_kwargs["max_output_tokens"] = max_tokens

        # if self.cache is None:
        #     if system_prompt is None:
        #         system_prompt = "You are a helpful assistant."
        #     self.init_cache(system_prompt)

        while attempt < retries:
            try:                
                
                response_obj = self.client.models.generate_content(
                    model=self.name,
                    contents=content,
                    # config=generation_config
                    config=types.GenerateContentConfig(
                        # cached_content=self.cache.name,
                        **config_kwargs
                    )
                )
                print(f'{response_obj.usage_metadata=}')
                logger.info(f"{COLOR_CODES['PURPLE']}Usage: {response_obj.usage_metadata}{RESET}")

                response = response_obj.text
                break
                
            except Exception as e:
                logger.error(f"Error: {COLOR_CODES['RED']}{e}{RESET}")
                attempt += 1
                if attempt < retries:
                    logger.info(f"Retrying in {delay} seconds.")
                    time.sleep(delay)
                else:
                    logger.error(f"All {retries} attempts failed.")
                    raise e
        if not response:
            raise ValueError("No response received from Gemini API")
        
        # 记录对话到文件
        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        
        self.log_conversation(messages, response, log_file=f"logs/{self.name}_conversation.txt")
        return response


def main():
    """测试代码"""
    model = GeminiWrapper(name="gemini-2.5-pro")
    prompt = "Please introduce Gemini AI"
    config = PredictConfig(prompt=prompt, temperature=0.7)
    response = model.predict(config)
    print(response)


if __name__ == "__main__":
    main()