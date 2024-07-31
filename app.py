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
        for user in users:    
            if user['username'] == username and user['password'] == password:
                return redirect('/user_screen')
            
            if user not in users:
                print(f"{user}")
                return render_template('error.html', error='Username incorrect/not found')
            
    return redirect('/')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if confirmation != password:
            return render_template('error.html', error='Passwords different')
        
        usuario = {'username': username,'password': password}
        
        #checagem de usuarios e adição dele ao JSON
        with open('users.json') as usersTemp:
            users = json.load(usersTemp)
            cont = 0
            for user in users:            
                if user['username'] == username:
                    return render_template('error.html', error='Username already in use')
                else:
                    users.append(usuario)
                    break
            with open('users.json', 'w') as usuarioTemp:
                json.dump(users, usuarioTemp, indent=4)
        return redirect('/')
    
@app.route('/user_screen', methods=['POST', 'GET'])
def user_screen():
    method = request.method
    if method == 'GET':
        with open('workouts.json') as workoutsTemp:
            workouts = json.load(workoutsTemp)
            exercises = []
            for workout in workouts:
                for muscle in workout.values():
                    if isinstance(muscle, int):
                        continue
                    else:
                        exercises.append(muscle)
            
            return render_template('user_screen.html', exercises=exercises)
    if method == 'POST':
        with open('workouts.json') as workoutsTemp:
            workouts = json.load(workoutsTemp)
            exercises = []
            for workout in workouts:
                for muscle in workout.values():
                    if isinstance(muscle, int):
                        continue
                    else:
                        exercises.append(muscle)
            button_clicked = request.form.get('button')
            if button_clicked == 'button-a':
                print("Botão a")
                return render_template('user_screen.html', exercises=exercises, workout="Workout A")
            elif button_clicked == 'button-b':
                print("Botão b")
                return render_template('user_screen.html', exercises=exercises, workout="Workout B")