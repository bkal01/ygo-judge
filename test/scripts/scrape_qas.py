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
    url = f"{os.getenv('YGORESOURCES_API_QA_URL')}{id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Status {response.status_code}: failed to retrieve data for id {id}.")
    return ""

if __name__ == "__main__":
    random.seed(1)
    qa_filenames = os.listdir(os.getenv("YUGIOH_QA_HISTORY_PATH"))
    unseen_qa_filenames = []
    for i in range(len(qa_filenames)):
        if qa_filenames[i] not in os.listdir(os.getenv("RAW_OFFICIAL_QA_EVAL_PATH")):
            unseen_qa_filenames.append(qa_filenames[i])
            
    # Generate test files.
    for filename in random.sample(unseen_qa_filenames, k=100):
        id = int(filename.replace(".json", ""))
        save_path = f"{os.getenv('RAW_OFFICIAL_QA_EVAL_PATH')}{id}.json"
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

