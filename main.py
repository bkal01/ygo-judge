import os

from argparse import ArgumentParser, Namespace
from dotenv import load_dotenv

from completion.base_completer import BaseCompleter

def base(query: str) -> str:
    completer = BaseCompleter(
        model=os.environ["XAI_API_MODEL_NAME"],
        endpoint=os.environ["XAI_API_COMPLETIONS_ENDPOINT"],
    )
    completion = completer.complete(
        query=query
    )
    return completion

def in_context_cards(query: str) -> str:
    return "in context cards" + query

def in_context_rules_and_cards(query: str) -> str:
    return "in context rules and cards" + query

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