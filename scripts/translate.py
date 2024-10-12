import json
import os
import re
import unicodedata

from googletrans import Translator



def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
        
def get_card_name_mapping(card_ids):
    """
    given a list of card_ids, returns a mapping of JA card names to EN card names.
    """
    ja_to_en = {}
    ja_to_id = {}
    id_to_en = {}
    for card_id in card_ids:
        ja_card = load_json(f"data/ygoresources/yugioh-card-history/ja/{card_id}.json")
        en_card = load_json(f"data/ygoresources/yugioh-card-history/en/{card_id}.json")
    
        ja_to_en[ja_card["name"]] = en_card["name"]
        ja_to_id[ja_card["name"]] = card_id
        id_to_en[card_id] = en_card["name"]
    return ja_to_en, ja_to_id, id_to_en


def replace_card_names_with_ids(text, ja_to_id):
    def replace(match):
        ja_name = match.group(1)
        ja_name_normalized = unicodedata.normalize('NFKC', ja_name)
        return f"__{ja_to_id.get(ja_name_normalized, ja_name)}__"
    return re.sub(r'「(.+?)」', replace, text)

def replace_ids_with_card_names(text, id_to_en):
    def replace(match):
        card_id = int(match.group(1))
        return id_to_en.get(card_id, f"__{card_id}__")
    return re.sub(r"__(\d+)__", replace, text)

def translate_qa_file(input_file, output_file):
    qa_data = load_json(input_file)
    
    name_mapping, ja_to_id, id_to_en = get_card_name_mapping(qa_data["mentionedCards"])
    print(ja_to_id)
    print(id_to_en)
    
    translator = Translator()
    for field in ["title", "question", "answer"]:
        ja_text = qa_data[field]
        ja_text_with_en_card_names = replace_card_names_with_ids(ja_text, ja_to_id)
        result = translator.translate(ja_text_with_en_card_names, src="ja", dest="en")
        print(field, result.text)
        result_with_card_names = replace_ids_with_card_names(result.text, id_to_en)
        qa_data[field] = result_with_card_names
    print(qa_data)
    
print(translate_qa_file("data/ygoresources/yugioh-qa-history/3.json", ""))
