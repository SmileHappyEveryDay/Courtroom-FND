import tiktoken

# model2max_context = {
#     "gpt-4": 7900,
#     "gpt-4-0314": 7900,
#     "gpt-3.5-turbo-0301": 3900, 
#     "gpt-3.5-turbo": 3900,  gpt-3.5-turbo 的上下文长度已从 4096 升级到 16385，但代码中仍使用旧值
#     "text-davinci-003": 4096,
#     "text-davinci-002": 4096,
# }

model2max_context = {
    "gpt-4": 8192,
    "gpt-4-0314": 8192,
    "gpt-3.5-turbo-0301": 4096,
    "gpt-3.5-turbo": 16385,  # 更新为最新上下文长度
    "text-davinci-003": 4096,
    "text-davinci-002": 4096,
}

class OutOfQuotaException(Exception):
    def __init__(self, key, cause=None):
        super().__init__(f"No quota for key: {key}")
        self.key = key
        self.cause = cause

    def __str__(self):
        if self.cause:
            return f"{super().__str__()}. Caused by {self.cause}"
        else:
            return super().__str__()

class AccessTerminatedException(Exception):
    def __init__(self, key, cause=None):
        super().__init__(f"Access terminated key: {key}")
        self.key = key
        self.cause = cause

    def __str__(self):
        if self.cause:
            return f"{super().__str__()}. Caused by {self.cause}"
        else:
            return super().__str__()

def num_tokens_from_string(string: str, model_name: str) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens