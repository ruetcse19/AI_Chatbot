from flask import Flask, render_template, request
import json
import random
import wikipedia
from googlesearch import search

app = Flask(__name__)

with open('intents.json', 'r') as file:
    intents = json.load(file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    response = chat(user_input)
    return response

def chat(user_input):
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            if pattern.lower() in user_input.lower():
                return random.choice(intent['responses'])
    return search_online(user_input)

def search_wikipedia(query):
    try:
        result = wikipedia.summary(query, sentences=2)
        return result
    except wikipedia.exceptions.DisambiguationError as e:
        return None
    except wikipedia.exceptions.PageError as e:
        return None
    except Exception as e:
        print("Error searching Wikipedia:", e)
        return None

def search_google(query):
    try:
        search_results = search(query, num=1, stop=1, pause=2)
        for result in search_results:
            return result
    except Exception as e:
        print("Error searching Google:", e)
        return None

def search_online(query):
    wikipedia_result = search_wikipedia(query)
    if wikipedia_result:
        return f'<a href="{wikipedia_result}" target="_blank">{wikipedia_result}</a>'
    else:
        google_result = search_google(query)
        if google_result:
            return f'<a href="{google_result}" target="_blank">{google_result}</a>'
        else:
            return "Sorry, I couldn't find an answer for your query."

if __name__ == '__main__':
    app.run(debug=True)
