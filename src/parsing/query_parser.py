import json
import os

from abc import ABC, abstractmethod
from typing import Dict, List

class QueryParser(ABC):
    def load_names(self, dir: str) -> Dict:
        """
        Iterates through .json files to fetch all the card names.
        """
        names = {}
        for filename in os.listdir(dir):
            with open(f"{dir}/{filename}", "r") as f:
                card_info = json.load(f)
                names[card_info["name"]] = card_info["id"]
        print(f"Loaded {len(names)} names.")
        return names
    
    @abstractmethod
    def parse(self, query: str) -> List[str]:
        """
        Extract card names mentioned in a query.
        Potentially, this can also parse other game keywords in the future.
        """
        pass