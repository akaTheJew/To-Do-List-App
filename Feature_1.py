# Module Inititalization 
from flask import Flask, request,jsonify

import requests

name = 1
psw = 2
mail = 3

# Creating Instance of Flask Class
app = Flask(__name__)

# Route for the root URL
@app.route('/')
def index():
    return 'Welcome to the Login API!'


# Route for signup with POST method
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json  # Get JSON data from request body
    # Extract username, password, and email from JSON data
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Inputing your data 
    # Perform user signup logic here
    if password == psw and username == name:
        
    # For simplicity, just return the received data
        return jsonify({'message': 'Successfull Authentication'}), 200
    else: 
        return jsonify({'message': 'Wrong Authentication!!'}), 401
    


# Initializing the Flask Application
if __name__ == '__main__':
    app.run(debug=True)


