import json
import os

from googletrans import Translator

faq_dir = "data/ygoresources/yugioh-faq-history"
qa_dir = "data/ygoresources/yugioh-qa-history"

faq_filename = f"{faq_dir}/4007.json"

translator = Translator()


directory = os.fsencode(qa_dir)
for file in os.listdir(directory):
    file = os.fsdecode(file)
    if not file.endswith(".json"):
        continue
    filename = f"{qa_dir}/{file}"
    with open(filename) as f:
        qa_data = json.load(f)
        print(qa_data["fid"])