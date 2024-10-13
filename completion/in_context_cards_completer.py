import json
import os
import requests

from typing import Dict, List

from completion.completer import Completer

class InContextCardsCompleter(Completer):
    def __init__(self, model: str, endpoint: str, prompt_prefix: str, context_source: str, name_to_id: Dict):
        self.method = "in_context_cards"
        self.model = model
        self.endpoint = endpoint
        self.prompt_prefix = prompt_prefix
        self.context_source = context_source
        self.name_to_id = name_to_id

    def attach_context(self, query: str) -> str:
        query_with_context = ""
        for card_name in self.name_to_id:
            if card_name in query:
                card_id = self.name_to_id[card_name]
                with open(f"{self.context_source}{card_id}.json", "r") as f:
                    card_info = json.load(f)
                    query_with_context += f"{card_info}\n"
        query_with_context += query
        return query_with_context
    
    def complete(self, query: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
            "Accept": "text/event-stream",
        }
        query_with_context = self.attach_context(query)
        messages = [
            {
                "role": "system",
                "content": self.prompt_prefix,
            },
            {
                "role": "user",
                "content": query_with_context,
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
        completion = json_resp["choices"][0]["message"]["content"]
        return completion