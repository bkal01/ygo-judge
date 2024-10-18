import json
import os

from argparse import ArgumentParser, Namespace
from dotenv import load_dotenv
from tqdm import tqdm

from src.completion.base_completer import BaseCompleter
from src.completion.in_context_cards_completer import InContextCardsCompleter
from src.completion.in_context_rules_and_cards_completer import InContextRulesAndCardsCompleter

def base(query: str) -> str:
    with open(os.environ["BASE_MODEL_PROMPT_PATH"], "r") as f:
        prompt_prefix = str(f.read())
    completer = BaseCompleter(
        model=os.environ["MODEL_NAME"],
        endpoint=os.environ["CHAT_COMPLETIONS_ENDPOINT"],
        prompt_prefix=prompt_prefix,
    )
    completion = completer.complete(
        query=query
    )
    return completion

def in_context_cards(query: str) -> str:
    with open(os.environ["IN_CONTEXT_CARDS_MODEL_PROMPT_PATH"], "r") as f:
        prompt_prefix = str(f.read())

    print("Creating name to id map...")
    name_to_id = {}
    for filename in tqdm(os.listdir(f"{os.environ['YUGIOH_CARD_HISTORY_PATH']}")):
        with open(f"{os.environ['YUGIOH_CARD_HISTORY_PATH']}{filename}") as f:
            card_info = json.load(f)
            name_to_id[card_info["name"]] = card_info["id"]

    completer = InContextCardsCompleter(
        model=os.environ["MODEL_NAME"],
        endpoint=os.environ["CHAT_COMPLETIONS_ENDPOINT"],
        prompt_prefix=prompt_prefix,
        context_source=os.environ["YUGIOH_CARD_HISTORY_PATH"],
        name_to_id=name_to_id,
    )
    completion = completer.complete(
        query=query,
    )

    return completion

def in_context_rules_and_cards(query: str) -> str:
    with open(os.environ["IN_CONTEXT_RULES_AND_CARDS_MODEL_PROMPT_PATH"], "r") as f:
        prompt_prefix = str(f.read())

    print("Creating name to id map...")
    name_to_id = {}
    for filename in tqdm(os.listdir(f"{os.environ['YUGIOH_CARD_HISTORY_PATH']}")):
        with open(f"{os.environ['YUGIOH_CARD_HISTORY_PATH']}{filename}") as f:
            card_info = json.load(f)
            name_to_id[card_info["name"]] = card_info["id"]

    completer = InContextRulesAndCardsCompleter(
        model=os.environ["MODEL_NAME"],
        endpoint=os.environ["CHAT_COMPLETIONS_ENDPOINT"],
        prompt_prefix=prompt_prefix,
        context_sources=[
            os.environ["RULES_PERFECT_RULEBOOK_PATH"],
            os.environ["RULES_IF_VS_WHEN"],
            os.environ["RULES_FAST_EFFECT_TIMING"]
        ],
        card_info_dir=os.environ["YUGIOH_CARD_HISTORY_PATH"],
        name_to_id=name_to_id,
    )

    completion = completer.complete(
        query=query,
    )

    return completion

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--method",
        choices=["base", "in_context_cards", "in_context_rules_and_cards"],
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
    else:
        resp = "Unknown method."
    print(resp)

if __name__ == "__main__":
    load_dotenv()
    args = parse_arguments()
    main(args)