import json
import os
import re

from dotenv import load_dotenv
from typing import Dict, List

def has_english_translation(data: Dict) -> bool:
    return "en" in data["qaData"]

def card_infos_exists(ids: List) -> bool:
    for id in ids:
        if not os.path.isfile(f"{os.getenv('YUGIOH_CARD_HISTORY_PATH')}{id}.json"):
            return False
    return True

def replace_card_ids_with_names(data: Dict) -> str:
    card_ids = data["cards"]
    card_id_to_name = {}
    for card_id in card_ids:
        card_info_filename = f"{os.getenv('YUGIOH_CARD_HISTORY_PATH')}{card_id}.json"
        with open(card_info_filename, "r") as f:
            card_info = json.load(f)
            card_id_to_name[card_id] = card_info["name"]


    pattern = r"<<(\d+)>>"
    for key in ["title", "question", "answer"]:
        data_string = data["qaData"]["en"][key]
        new_data_string = re.sub(pattern, lambda x: card_id_to_name.get(int(x.group(1)), x.group(0)), data_string)
        data["qaData"]["en"][key] = new_data_string
    return data

if __name__ == "__main__":
    load_dotenv()
    
    for filename in os.listdir(os.getenv("RAW_OFFICIAL_QA_EVAL_PATH")):
        print(f"Checking {filename} for existing english translation...")
        with open(f"{os.getenv('RAW_OFFICIAL_QA_EVAL_PATH')}{filename}", "r") as f:
            qa_data = json.load(f)
        if has_english_translation(qa_data) and card_infos_exists(qa_data["cards"]):
            updated_qa_data = replace_card_ids_with_names(qa_data)
            with open(f"{os.getenv('PROCESSED_OFFICIAL_QA_EVAL_PATH')}{filename}", "w") as f:
                json.dump(updated_qa_data, f, indent=4)
            print(f"Processed {filename} successfully.")
        else:
            print(f"{filename} has no english translation.")
    number_of_english_qas = len(os.listdir(os.getenv("PROCESSED_OFFICIAL_QA_EVAL_PATH")))
    total_number_of_fetched_qas = len(os.listdir(os.getenv("RAW_OFFICIAL_QA_EVAL_PATH")))
    total_number_of_qas = len(os.listdir(os.getenv("YUGIOH_QA_HISTORY_PATH")))
    print(f"Number of files with english: {number_of_english_qas}. Total number of fetched QAs: {total_number_of_fetched_qas}. Total number of QAs: {total_number_of_qas}")
    print(f"Fraction of translated QAs: {number_of_english_qas / total_number_of_fetched_qas}")