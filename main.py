from argparse import ArgumentParser, Namespace

def base(query: str) -> str:
    return "base" + query

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
    print(resp)

if __name__ == "__main__":
    args = parse_arguments()
    main(args)