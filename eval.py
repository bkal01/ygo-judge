import json
import os

from argparse import ArgumentParser, Namespace
from dotenv import load_dotenv
from tqdm import tqdm

from completion.completer import Completer
from completion.base_completer import BaseCompleter
from completion.in_context_cards_completer import InContextCardsCompleter


def evaluate_with_human_feedback(responses_dir: str) -> float:
    correct_count = 0
    total_count = 0
    
    for filename in os.listdir(responses_dir):
        with open(f"{responses_dir}{filename}", "r") as f:
            response_data = json.load(f)

        print(f"Question: {response_data['question']}\n")
        print(f"Correct Answer: {response_data['answer']}\n")
        print(f"LLM Answer: {response_data['llm_answer']}\n")
        
        while True:
            user_feedback = input("Was the LLM's response correct? Enter yes or no:\n").strip().lower()
            if user_feedback in ["yes", "no"]:
                break
            else:
                print("Please enter 'yes' or 'no'.")
        
        if user_feedback == "yes":
            correct_count += 1
        
        total_count += 1
    
    accuracy = correct_count / total_count if total_count > 0 else 0.0
    return accuracy

def generate_eval_responses(completer: Completer) -> None:
    for filename in tqdm(os.listdir(os.environ["TEST_QA_PATH"])):
        if os.path.isfile(f"{os.environ['TEST_RESPONSES_PATH']}{completer.method}/{filename}"):
            continue
        with open(f"{os.environ['TEST_QA_PATH']}{filename}", "r") as f:
            qa_test_data = json.load(f)
            question = qa_test_data["qaData"]["en"]["question"]
            llm_answer = completer.complete(question)

        eval_json = {
            "title": qa_test_data["qaData"]["en"]["title"],
            "question": qa_test_data["qaData"]["en"]["question"],
            "answer": qa_test_data["qaData"]["en"]["answer"],
            "llm_answer": llm_answer,
        }
        with open(f"{os.environ['TEST_RESPONSES_PATH']}{completer.method}/{filename}", "w") as f:
            json.dump(eval_json, f, indent=4)

def eval_base() -> None:
    with open(os.environ["BASE_MODEL_PROMPT_PATH"], "r") as f:
        prompt_prefix = str(f.read())
    completer = BaseCompleter(
        model=os.environ["XAI_API_MODEL_NAME"],
        endpoint=os.environ["XAI_API_CHAT_COMPLETIONS_ENDPOINT"],
        prompt_prefix=prompt_prefix,
    )

    generate_eval_responses(completer)

def eval_in_context_cards() -> None:
    with open(os.environ["IN_CONTEXT_CARDS_MODEL_PROMPT_PATH"], "r") as f:
        prompt_prefix = str(f.read())

    print("Creating name to id map...")
    name_to_id = {}
    for filename in tqdm(os.listdir(f"{os.environ['YUGIOH_CARD_HISTORY_PATH']}")):
        with open(f"{os.environ['YUGIOH_CARD_HISTORY_PATH']}{filename}") as f:
            card_info = json.load(f)
            name_to_id[card_info["name"]] = card_info["id"]

    completer = InContextCardsCompleter(
        model=os.environ["XAI_API_MODEL_NAME"],
        endpoint=os.environ["XAI_API_CHAT_COMPLETIONS_ENDPOINT"],
        prompt_prefix=prompt_prefix,
        context_source=os.environ["YUGIOH_CARD_HISTORY_PATH"],
        name_to_id=name_to_id,
    )
    generate_eval_responses(completer)

def eval_in_context_rules_and_cards() -> None:
    return

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate evaluation responses"
    )
    parser.add_argument(
        "--grade",
        action="store_true",
        help="Grade evaluation responses"
    )
    parser.add_argument(
        "--method",
        choices=["base", "in_context_cards", "in_context_rules_and_cards"],
        required=True,
        help="Specify the method to use: 'base': feed the query directly into an LLM, 'in_context_cards': provide relevant cards in context, or 'in_context_rules_and_cards': provide official rulebook + relevant cards in context"
    )
    return parser.parse_args()

def run_eval(args: Namespace) -> None:
    if args.generate:
        if args.method == "base":
            eval_base()
        elif args.method == "in_context_cards":
            eval_in_context_cards()
        elif args.method == "in_context_rules_and_cards":
            eval_in_context_rules_and_cards()
    if args.grade:
        accuracy = evaluate_with_human_feedback(f"{os.environ['TEST_RESPONSES_PATH']}{args.method}/")
        print(f"Grading accuracy: {accuracy}")

if __name__ == "__main__":
    load_dotenv()
    args = parse_arguments()
    run_eval(args)