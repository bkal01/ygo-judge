import os
import requests

from src.completion.completer import Completer

class BaseCompleter(Completer):
    def __init__(self, model: str, endpoint: str, prompt_prefix: str):
        self.method = "base"
        self.model = model
        self.endpoint = endpoint
        self.prompt_prefix = prompt_prefix

    def attach_context(self):
        return
    
    def complete(self, query: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
            "Accept": "text/event-stream",
        }
        messages = [
            {
                "role": "system",
                "content": self.prompt_prefix,
            },
            {
                "role": "user",
                "content": query,
            },
        ]
        data = {
            "model": self.model,
            "messages": messages,
        }
        resp = requests.post(
            url=self.endpoint,
            headers=headers,
            json=data,
        )
        json_resp = resp.json()
        print(json_resp)
        completion = json_resp["choices"][0]["message"]["content"]
        return completion