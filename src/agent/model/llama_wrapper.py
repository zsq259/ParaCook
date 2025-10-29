from transformers import pipeline
from src.agent.model.model import Model, PredictConfig
from src.utils.logger_config import logger, COLOR_CODES, RESET

class LLaMaWrapper(Model):
    def __init__(self, name):
        super().__init__(name=name)
        self.pipe = pipeline("text-generation", model=name)

    def predict(self, config: PredictConfig) -> str:
        retries = config.retries
        attempt = 0
        response = ""

        while attempt < retries:
            try:
                prompt = config.prompt
                stop = config.stop
                system_prompt = config.system_prompt
                messages = config.messages
                temperature = config.temperature
                if temperature is None or temperature == 0:
                    temperature = 0.1  # LLaMa does not support temperature=0
                if messages is None:
                    if system_prompt:
                        messages = [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                    else:
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                kwargs = {
                    "text_inputs": messages,
                    "temperature": temperature,
                    "stop": stop
                }
                if config.top_p is not None:
                    kwargs["top_p"] = config.top_p,
                if config.max_tokens is not None:
                    kwargs["max_new_tokens"] = config.max_tokens,
                else:
                    kwargs["max_new_tokens"] = 12800  # default max tokens for LLaMa
                    
                response = self.pipe(**kwargs)
                return response[0]['generated_text'][-1]['content']
                
                # logger.info(f"{COLOR_CODES['PURPLE']}Usage: {response.usage}{RESET}")
            except Exception as e:
                logger.error(f"Error: {COLOR_CODES['RED']}{e}{RESET}")
                raise e
        return response
    
def main():
    
    model = LLaMaWrapper(name="Llama-3.1-8B-Instruct")
    prompt = "Please introduce gpt-5"
    config = PredictConfig(prompt=prompt, temperature=0.2)
    response = model.predict(config)
    print(response)

if __name__ == "__main__":
    main()