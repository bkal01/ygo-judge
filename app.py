from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
from main import base, in_context_cards, in_context_rules_and_cards

app = Flask(__name__)
load_dotenv()

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    query = data['query']
    method = data['method']

    if method == "base":
        resp = base(query)
    elif method == "in_context_cards":
        resp = in_context_cards(query)
    elif method == "in_context_rules_and_cards":
        resp = in_context_rules_and_cards(query)
    else:
        resp = "Unknown method."

    return jsonify({'response': resp})

if __name__ == '__main__':
    app.run(debug=True)