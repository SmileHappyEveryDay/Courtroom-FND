import openai
import backoff
import time
import random
from openai.error import RateLimitError, APIError, ServiceUnavailableError, APIConnectionError
from .openai_utils import OutOfQuotaException, AccessTerminatedException
from .openai_utils import num_tokens_from_string, model2max_context

support_models = ['gpt-3.5-turbo', 'gpt-3.5-turbo-0301', 'gpt-4', 'gpt-4-0314']

class Agent:
    def __init__(self, model_name: str, name: str, temperature: float, sleep_time: float=0) -> None:
        self.model_name = model_name
        self.name = name
        self.temperature = temperature
        self.memory_lst = []
        self.sleep_time = sleep_time

    @backoff.on_exception(backoff.expo, (RateLimitError, APIError, ServiceUnavailableError, APIConnectionError), max_tries=20)
    def query_old(self, messages: "list[dict]", max_tokens: int, api_key: str, temperature: float) -> str:
        time.sleep(self.sleep_time)
        assert self.model_name in support_models, f"Not support {self.model_name}. Choices: {support_models}"
        try:
            if self.model_name in support_models:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                )
                gen = response['choices'][0]['message']['content']
            return gen

        except RateLimitError as e:
            if "You exceeded your current quota, please check your plan and billing details" in e.user_message:
                raise OutOfQuotaException(api_key)
            elif "Your access was terminated due to violation of our policies" in e.user_message:
                raise AccessTerminatedException(api_key)
            else:
                raise e
            
    # 原query方法存在异常处理，未处理 KeyError以及未处理所有可能的 OpenAI 错误类型，修改后的 query 方法如下
    @backoff.on_exception(backoff.expo, (RateLimitError, APIError, ServiceUnavailableError, APIConnectionError, InvalidRequestError), max_tries=20)
    def query(self, messages: "list[dict]", max_tokens: int, api_key: str, temperature: float) -> str:
        time.sleep(self.sleep_time)
        assert self.model_name in support_models, f"Not support {self.model_name}. Choices: {support_models}"
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
            )
            # 添加 KeyError 处理
            if not response.get("choices") or not response["choices"][0].get("message", {}).get("content"):
                raise ValueError("Invalid API response format")
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise APIError(f"Unexpected API response: {e}")
        except RateLimitError as e:
            # 原有处理逻辑
            if "You exceeded your current quota, please check your plan and billing details" in e.user_message:
                raise OutOfQuotaException(api_key)
            elif "Your access was terminated due to violation of our policies" in e.user_message:
                raise AccessTerminatedException(api_key)
            else:
                raise e

    def set_meta_prompt(self, meta_prompt: str):
        self.memory_lst.append({"role": "system", "content": f"{meta_prompt}"})

    def add_event(self, event: str):
        self.memory_lst.append({"role": "user", "content": f"{event}"})

    def add_memory(self, memory: str):
        self.memory_lst.append({"role": "assistant", "content": f"{memory}"})
        print(f"----- {self.name} -----\n{memory}\n")

    def ask(self, temperature: float=None):
        num_context_token = sum([num_tokens_from_string(m["content"], self.model_name) for m in self.memory_lst])
        max_token = model2max_context[self.model_name] - num_context_token
        return self.query(self.memory_lst, max_token, api_key=self.openai_api_key, temperature=temperature if temperature else self.temperature)