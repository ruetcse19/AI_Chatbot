import json

def train():
    with open('intents.json', 'r') as file:
        intents = json.load(file)
        
    for intent in intents['intents']:
        print(intent)

if __name__ == '__main__':
    train()
