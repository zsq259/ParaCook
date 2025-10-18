from calendar import c
import os
import sys
import time
import anthropic
from src.agent.model.model import Model, PredictConfig
from src.utils.logger_config import logger, COLOR_CODES, RESET

class ClaudeWrapper(Model):
    def __init__(self, name):
        super().__init__(name=name)
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.is_chat_model = True

    def predict(self, config: PredictConfig) -> str:
        prompt = config.prompt
        system_prompt = config.system_prompt
        messages = config.messages
        temperature = config.temperature
        max_tokens = config.max_tokens
        retries = config.retries or 3
        delay = config.delay or 1
        attempt = 0
        response = ""

        while attempt < retries:
            try:
                client = anthropic.Anthropic(api_key=self.api_key)
                cache_block_count = 0

                kwargs = {
                    "model": self.name,
                    "messages": messages
                }
                if system_prompt:
                    kwargs["system"] = [
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"}  # Use Prompt Caching
                        }
                    ]
                    cache_block_count += 1
                if temperature is not None:
                    kwargs["temperature"] = temperature
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                else:
                    kwargs["max_tokens"] = 21332 # default max tokens

                if messages is None:
                    messages = [
                        {
                            "role": "user", 
                            "content": [
                                {"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}}
                            ]
                        }
                    ]
                    cache_block_count += 1
                else:
                    if messages[0]["role"] == "system":
                        system_prompt = messages[0]["content"]
                        messages = messages[1:]
                    for msg in messages:
                        content = msg["content"]
                        if msg["role"] == "user" and isinstance(content, str):
                            if cache_block_count < 4:
                                msg["content"] = [{"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}]
                                cache_block_count += 1
                            else:
                                msg["content"] = [{"type": "text", "text": content}]
                        elif msg["role"] == "assistant" and isinstance(content, str):
                            msg["content"] = [{"type": "text", "text": content}]
                kwargs["messages"] = messages

                with client.messages.stream(**kwargs) as stream:
                    collected_text = ""
                    for text_chunk in stream.text_stream:
                        # print(text_chunk, end="", flush=True)
                        collected_text += text_chunk
                    final_message = stream.get_final_message()
                    if hasattr(final_message, 'usage'):
                        usage = final_message.usage
                        print(f"Usage: {usage}")

                response = collected_text

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
            raise ValueError("No response received from Claude API")
        return response

def main():
    model = ClaudeWrapper(name="claude-sonnet-4-20250514")
    prompt = "What is your name and version?"
    config = PredictConfig(prompt=prompt, temperature=0, max_tokens=1000)
    response = model.predict(config)
    print(response)

if __name__ == "__main__":
    main()