from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import requests
import random
import string
import re
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_intents(file_path):
    with open(file_path, 'r') as file:
        intents = json.load(file)
    return intents

def generate_tag(user_input):
    # Clean the input text
    cleaned_input = re.sub(r'[^\w\s]', '', user_input)
    cleaned_input = cleaned_input.lower()
    # Remove stopwords
    stopwords = ['in', 'of', 'the', 'and', 'for', 'on', 'at', 'to', 'a', 'an']
    cleaned_input = ' '.join(word for word in cleaned_input.split() if word not in stopwords)
    # Replace spaces with underscores
    cleaned_input = cleaned_input.replace(' ', '_')
    return cleaned_input

def get_random_response(intent):
    return random.choice(intent['responses'])

def get_response(intents, query):
    query_lower = query.lower()  
    for intent in intents['intents']:
        patterns_lower = [pattern.lower() for pattern in intent['patterns']]
        if query_lower in patterns_lower:
            response = get_random_response(intent)
            if 'text' in response and 'link' in response['text']:
                return response['text']['text'], response['text']['link']
            else:
                return response['text'], response['link']
    return None, None

def capture_conversation(intents, user_input=None, response=None, link=None):
    if user_input and response and not any(intent['patterns'][0].lower() == user_input.lower() for intent in intents['intents']):
        new_tag = generate_tag(user_input)
        intent = {
            'tag': new_tag,
            'patterns': [user_input],
            'responses': [{'text': response, 'link': link}]  # Modified to include link
        }
        intents['intents'].append(intent)
        with open('intents.json', 'w') as file:
            json.dump(intents, file, indent=4)
        print("Conversation saved to intents.json:", user_input, response)
    else:
        print("Response already exists in intents.json or input is empty:", user_input, response)

def search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    api_key = "your_api_key"
    cx = "your_cx"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("items"):
            result = data["items"][0]["snippet"]
            link = data["items"][0]["link"]
            return result, link
    except Exception as e:
        print("An error occurred:", e)
    return None, None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    intents = load_intents('intents.json')
    if user_input.lower() == "exit":
        capture_conversation(intents)
        return jsonify({'response': 'Goodbye!'})
    text_response, link_response = get_response(intents, user_input)
    if text_response:
        if link_response:
            response_message = f"{text_response}<br><a href='{link_response}' target='_blank'>More Details</a>"
        else:
            response_message = text_response
        capture_conversation(intents, user_input, text_response, link_response)
        return jsonify({'response': response_message})
    else:
        result, link = search(user_input)
        if result and link:
            capture_conversation(intents, user_input, result, link)  
            return jsonify({'result': result, 'link': link})
        else:
            return jsonify({'no_result': True})

@app.route('/save', methods=['POST'])
def save():
    intents = load_intents('intents.json')
    capture_conversation(intents)
    return jsonify({'saved': True})

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
