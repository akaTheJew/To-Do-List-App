# Module Inititalization 
import sqlite3  #Import sqlite3 library
import requests #Import requests library 
import logging  #Import python logging library
import datetime #Import the date time python module 
import jwt #Import Json Web Tokens 
from flask import Flask, request, jsonify, g, make_response
from collections import OrderedDict

# Creating Instance of Flask Class
app = Flask(__name__)


# Connect to SQLite database
conn = sqlite3.connect('todo.db')
cursor = conn.cursor()
# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')

# Create tasks table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT NOT NULL,
        description TEXT,
        due_date DATE,
        priority TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
''')

# Commit changes to the database
conn.commit()
cursor.close()
conn.close()


def generate_token(user_id):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours= 2)
    payload = {
        'user_id': user_id,
        'expiration': expiration_time.isoformat()  # Convert to ISO format string
    }
    token = jwt.encode(payload, 'your_secret_key', algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, 'your_secret_key', algorithms = ['HS256'])
        return payload 
    except jwt.ExpiredSignatureError:
        return jsonify({'message':'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message':'Token is invalid'}), 401



@app.before_request
def authenticate():
    token = request.headers.get('Authorization')
    if token:
        token = token.split(' ')[1] #Extract token from 'Bearer <token>'
        payload = verify_token(token)
        if isinstance(payload, dict):
            g.user_id = payload.get('user_id')
            return
        return jsonify({'message':'Unauthorized'}), 401
    '''
        if payload:
            g.user_id = payload['user_id']# Attach user ID to Flask global context (g)
            return
        return jsonify({'message':'Unauthorized'}), 401
    '''
#Protect an endpoint
@app.route('/protected_resource')
def protected_resource():
    user_id = g.user_id # Access user ID from global context
    # Use the user ID to fetch or manipulate resources

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # Create a new connection for this thread 
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username,password))
    existing_user = cursor.fetchone()
    
    
    try:
        if existing_user:
            return jsonify({'message':'The user already exists kindly'})
        
        cursor.execute('INSERT INTO users(username, password, email) VALUES (?,?,?)', (username, password, email))
        conn.commit()
        
        cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]  # Assuming user_id is the first column

        token = generate_token(user_id)
        response = make_response(jsonify({'message':'User registered successfully'}),200)
        response.headers['Authorization'] = 'Bearer ' + token
    
        return token
    
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message':'Error occured during user registration'}), 500
    finally:    
        cursor.close()
        conn.close()



@app.route('/login', methods = ['GET'])
def login_user():
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    existing_user = cursor.fetchone()
    
    try:
        if existing_user:
            return jsonify({'message':f'Welcome {username} to your profile'}), 200
        else:
            return jsonify({'message':'Invalid Username or Password'}), 401
    except sqlite3.Error as e:
        return jsonify({'message':'Error occured during login'}), 500
    finally:    
        cursor.close()
        conn.close()


    
@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.json
    task_name = data.get('task_name')
    description = data.get('description')
    due_date = data.get('due_date')
    priority = data.get('priority')
    user_id = data.get('user_id')  # Assuming user ID is provided in the request
    
    
    # Create a new connection for this thread 
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    
    try: 
        cursor.execute('INSERT INTO tasks (task_name, description, due_date, priority, user_id) VALUES (?,?,?,?,?)', (task_name, description, due_date, priority, user_id))
        conn.commit()
        return jsonify({'message':'Task created successfully'}), 200
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message':'Error occured when creating a task'}), 500
    finally:
        cursor.close()
        conn.close()
    
    
@app.route('/view_tasks', methods=['GET'])
def get_tasks():
    # Create a new connection for this thread 
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
    
        task_list = []
        for task in tasks:
            task_item = {
                'task_id': task[0],
                'task_name': task[1],
                'description': task[2],
                'due_date': task[3],
                'priority': task[4],
                'user_id': task[5]
            }
            task_list.append(task_item)
        conn.commit()
        return jsonify ({'message':'Tasks displayed successfully', 'tasks':task_list}), 200
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message':'Error occuren when viewing tasks'}), 500
    finally:        
        cursor.close()
        conn.close()
    
# Route for editing a task with PUT method
@app.route('/edit_task/<int:task_id>', methods=['PUT'])
def edit_task(task_id):
    data = request.json
    
    # Extract updated task details from request data
    updated_task_name = data.get('task_name')
    updated_description = data.get('description')
    updated_due_date = data.get('due_date')
    updated_priority = data.get('priority')

    # Create a new connection for this thread 
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    try:
        # Execute SQL UPDATE command to modify task details in the database
        cursor.execute('''
            UPDATE tasks 
            SET task_name = ?, description = ?, due_date = ?, priority = ?
            WHERE task_id = ?
        ''', (updated_task_name, updated_description, updated_due_date, updated_priority, task_id))
        conn.commit()
        return jsonify({'message':'Task edited successfully'}), 200
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify ({'message':'Error occured when editing a task'}), 500   
    finally:   
    # Close cursor and connection to the database
        cursor.close()
        conn.close()

# Route for deleting a task with the DELETE method
@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    # Create a new connection for this thread 
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    try:
        # Execute SQL DELETE command to remove task from the database
        cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
        conn.commit()
        return jsonify({'message':'Task deleted successfully'}), 200
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'message':'Error occured when deleting a task'}), 500
    finally:
    # Commit changes to the database    
        cursor.close()
        conn.close()
    
# Run the Flask App
if __name__ == '__main__':
    try:
        # Your database connection setup code here

        # Run the Flask app
        app.run(debug=True)

    finally:
        # Close the database connection when the application exits
        conn.close()