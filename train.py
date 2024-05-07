from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import json
import os
import string
import random

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_intents(file_path):
    with open(file_path, 'r') as file:
        intents = json.load(file)
    return intents

def save_intents(intents, file_path):
    with open(file_path, 'w') as file:
        json.dump(intents, file, indent=4)

def generate_random_filename():
    return ''.join(random.choices(string.ascii_lowercase, k=6))

@app.route('/')
def index():
    return render_template('train.html')

@app.route('/add_intent', methods=['POST'])
def add_intent():
    tag = request.form['tag']
    pattern = request.form['pattern']
    response = request.form['response']
    response_type = request.form.get('response_type')
    link = request.form.get('link')
    file = request.files.get('file')

    intents = load_intents('intents.json')

    new_intent = {
        'tag': tag,
        'patterns': [pattern],
        'responses': []
    }

    if response_type == 'link':
        new_intent['responses'].append({
            'text': response,
            'link': link if link else None
        })
    elif response_type == 'file' and file:
        filename = generate_random_filename() + '_' + file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_link = url_for('uploaded_file', filename=filename)
        new_intent['responses'].append({
            'text': response,
            'link': file_link
        })

    intents['intents'].append(new_intent)
    save_intents(intents, 'intents.json')

    return jsonify({'success': True, 'intent': new_intent})  # Return JSON response

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
