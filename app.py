from flask import Flask, render_template, redirect, request
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starbobinho'



@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('user')
    password = request.form.get('password')

    with open('users.json') as usersTemp:
        users = json.load(usersTemp)
        cont = 0
        for user in users:            
            if user['username'] == username and user['password'] == password:
                return render_template('user_screen.html')
            
            if cont >= len(users) or user['username'] not in users or user['password'] != password:
                return render_template('error.html', error='Username/Password incorrect')
            
    return redirect('/')