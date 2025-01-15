import json
import os

from argparse import ArgumentParser, Namespace
from dotenv import load_dotenv
from tqdm import tqdm

from src.completion.base_completer import BaseCompleter
from src.completion.in_context_cards_completer import InContextCardsCompleter
from src.completion.in_context_rules_and_cards_completer import InContextRulesAndCardsCompleter
from src.parsing.naive_query_parser import NaiveQueryParser
from src.store.store import load_documents, process_documents

def base(query: str) -> str:
    with open(os.getenv("BASE_MODEL_PROMPT_PATH"), "r") as f:
        prompt_prefix = str(f.read())
    completer = BaseCompleter(
        model=os.getenv("MODEL_NAME"),
        endpoint=os.getenv("CHAT_COMPLETIONS_ENDPOINT"),
        prompt_prefix=prompt_prefix,
    )
    completion = completer.complete(
        query=query
    )
    return completion

def in_context_cards(query: str) -> str:
    with open(os.getenv("IN_CONTEXT_CARDS_MODEL_PROMPT_PATH"), "r") as f:
        prompt_prefix = str(f.read())
        
    parser = NaiveQueryParser(
        card_name_dir=os.getenv("YUGIOH_CARD_HISTORY_PATH"),
    )

    completer = InContextCardsCompleter(
        model=os.getenv("MODEL_NAME"),
        endpoint=os.getenv("CHAT_COMPLETIONS_ENDPOINT"),
        prompt_prefix=prompt_prefix,
        context_source=os.getenv("YUGIOH_CARD_HISTORY_PATH"),
        parser=parser,
    )
    completion = completer.complete(
        query=query,
    )

    return completion

def in_context_rules_and_cards(query: str) -> str:
    with open(os.getenv("IN_CONTEXT_RULES_AND_CARDS_MODEL_PROMPT_PATH"), "r") as f:
        prompt_prefix = str(f.read())

    print("Creating name to id map...")
    name_to_id = {}
    for filename in tqdm(os.listdir(f"{os.getenv('YUGIOH_CARD_HISTORY_PATH')}")):
        with open(f"{os.getenv('YUGIOH_CARD_HISTORY_PATH')}{filename}") as f:
            card_info = json.load(f)
            name_to_id[card_info["name"]] = card_info["id"]

    completer = InContextRulesAndCardsCompleter(
        model=os.getenv("MODEL_NAME"),
        endpoint=os.getenv("CHAT_COMPLETIONS_ENDPOINT"),
        prompt_prefix=prompt_prefix,
        context_sources=[
            os.getenv("RULES_PERFECT_RULEBOOK_PATH"),
            os.getenv("RULES_IF_VS_WHEN"),
            os.getenv("RULES_FAST_EFFECT_TIMING"),
        ],
        card_info_dir=os.getenv("YUGIOH_CARD_HISTORY_PATH"),
        name_to_id=name_to_id,
    )

    completion = completer.complete(
        query=query,
    )

    return completion

def rag(query: str) -> str:
    with open(os.getenv("IN_CONTEXT_CARDS_MODEL_PROMPT_PATH"), "r") as f:
        prompt_prefix = str(f.read())
    # Load and process rules documents
    docs = load_documents(os.getenv("RULES_PATH"))
    vector_store = process_documents(docs)
    
    rules_chunks = vector_store.similarity_search(
        query=query,
        k=3,
    )

    print([doc.page_content for doc in rules_chunks])
    rules_context = "\nHere is some additional context from the game's rules to aid your answer generation:\n" \
        .join([doc.page_content for doc in rules_chunks])

    parser = NaiveQueryParser(
        card_name_dir=os.getenv("YUGIOH_CARD_HISTORY_PATH"),
    )

    completer = InContextCardsCompleter(
        model=os.getenv("MODEL_NAME"),
        endpoint=os.getenv("CHAT_COMPLETIONS_ENDPOINT"),
        prompt_prefix=prompt_prefix + "\n\nRelevant rules:\n" + rules_context,
        context_source=os.getenv("YUGIOH_CARD_HISTORY_PATH"),
        parser=parser,
    )
    completion = completer.complete(
        query=query,
    )

    return completion

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--method",
        choices=["base", "in_context_cards", "in_context_rules_and_cards", "rag"],
        required=True,
        help="Specify the method to use: 'base': feed the query directly into an LLM, 'in_context_cards': provide relevant cards in context, or 'in_context_rules_and_cards': provide official rulebook + relevant cards in context"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="The rulings question you want answered."
    )
    return parser.parse_args()

def main(args: Namespace) -> None:
    if args.method == "base":
        resp = base(args.query)
    elif args.method == "in_context_cards":
        resp = in_context_cards(args.query)
    elif args.method == "in_context_rules_and_cards":
        resp = in_context_rules_and_cards(args.query)
    elif args.method == "rag":
        resp = rag(args.query)
    else:
        resp = "Unknown method."
    print(resp)

if __name__ == "__main__":
    load_dotenv()
    args = parse_arguments()
    main(args)