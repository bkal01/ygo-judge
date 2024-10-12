import json
import os
import random
import re
import requests
import time

from dotenv import load_dotenv
from typing import Dict

load_dotenv()

def fetch_qa(id: int) -> str:
    """
    Fetches Q&A data for a single qa id from the YGOResources API.
    """
    url = f"{os.environ['YGORESOURCES_API_QA_URL']}{id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Status {response.status_code}: failed to retrieve data for id {id}.")
    return ""

def has_english_translation(data: Dict) -> bool:
    return "en" in data["qaData"]

def replace_card_ids_with_names(data: Dict) -> str:
    card_ids = data["cards"]
    card_id_to_name = {}
    for card_id in card_ids:
        card_info_filename = f"{os.environ['YUGIOH_CARD_HISTORY_PATH']}{card_id}.json"
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
    random.seed(1)
    qa_filenames = os.listdir(os.environ["YUGIOH_QA_HISTORY_PATH"])

    # Generate test files.
    for filename in random.choices(qa_filenames, k=100):
        id = int(filename.replace(".json", ""))
        save_path = f"{os.environ['TEST_QA_PATH']}{id}.json"
        if os.path.isfile(save_path):
            print(f"Test file for id {id} already exists.")
            continue
        qa_data = fetch_qa(id)
        if len(qa_data) == 0:
            print(f"failed to fetch data for id {id}")
            continue
        with open(f"{save_path}", "w") as f:
            json.dump(qa_data, f, indent=4)
        print(f"Successfully created test file {save_path}")
        time.sleep(2)


    # Delete ones without english translations.
    for filename in os.listdir(os.environ["TEST_QA_PATH"]):
        print(f"Processing {filename} for deletion...")
        with open(f"{os.environ['TEST_QA_PATH']}{filename}", "r") as f:
            qa_test_data = json.load(f)
        if not has_english_translation(qa_test_data):
            os.remove(f"{os.environ['TEST_QA_PATH']}{filename}")
            print(f"Deleted {filename}.")

    print(f"Remaining number of test files: {len(os.listdir(os.environ['TEST_QA_PATH']))}")

    # Replace card ids with card names.
    for filename in os.listdir(os.environ["TEST_QA_PATH"]):
        print(f"Replacing card ids in {filename}...")
        with open(f"{os.environ['TEST_QA_PATH']}{filename}", "r") as f:
            qa_test_data = json.load(f)
            updated_qa_test_data = replace_card_ids_with_names(qa_test_data)
        with open(f"{os.environ['TEST_QA_PATH']}{filename}", "w") as f:
            # Clear file
            json.dump(updated_qa_test_data, f, indent=4)
        print(f"Replaced card ids with card names for file {filename}")

