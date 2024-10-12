import os
import requests

from completion.completer import Completer

class BaseCompleter(Completer):
    def __init__(self, model: str, endpoint: str):
        self.model = model
        self.endpoint = endpoint

    def attach_context(self):
        return
    
    def complete(self, query: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
        }
        data = {
            "model": self.model,
            "prompt": query,
        }
        resp = requests.post(
            url=self.endpoint,
            headers=headers,
            json=data,
        )
        json_resp = resp.json()
        completion = json_resp["choices"][0]["text"]
        return completion