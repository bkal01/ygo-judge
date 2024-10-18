import os

from dotenv import load_dotenv
from typing import List

from src.parsing.query_parser import QueryParser

class NaiveQueryParser(QueryParser):
    """
    Naively parses queries by checking for exact card name matches.
    """
    def __init__(self, card_name_dir: str) -> None:
        self.names = super().load_names(card_name_dir)
    
    def parse(self, query: str) -> List[int]:
        matched_ids = []
        for i in range(len(query)):
            for j in range(i + 1, len(query) + 1):
                substring = query[i:j]
                if substring in self.names:
                    matched_ids.append(self.names[substring])
        return matched_ids
    
if __name__ == "__main__":
    load_dotenv()
    parser = NaiveQueryParser(
        card_name_dir=os.getenv("YUGIOH_CARD_HISTORY_PATH"),
    )
    matched_ids = parser.parse(
        query="Tour Guide From the Underworld testing testing Raigeki testing testing Infinite Impermanence testing testing."
    )
    print(matched_ids)