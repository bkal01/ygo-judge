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
    
    def parse(self, query: str) -> List[str]:
        query_words = query.split()
        matched_names = []
        for i in range(len(query_words) - 1):
            for j in range(i+1, len(query_words)):
                substring = " ".join(query_words[i:j])
                if substring in self.names:
                    matched_names.append(substring)
        return matched_names
    
if __name__ == "__main__":
    load_dotenv()
    parser = NaiveQueryParser(
        card_name_dir=os.getenv("YUGIOH_CARD_HISTORY_PATH"),
    )
    matched_names = parser.parse(
        query="Tour Guide From the Underworld testing testing Raigeki testing testing Infinite Impermanence testing testing."
    )
    print(matched_names)