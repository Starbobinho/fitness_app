from flask import Flask, render_template, redirect, request, session
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starbobinho'

def generate_new_id(workouts):
    if not workouts:
        return 0
    return max(workout['id'] for workout in workouts) + 1

@app.route('/')
def home():
    return render_template('login.html')

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
            cont = len(users)
            print(cont)
            for user in users:
                print(username, user['username'])
                cont -= 1            
                if username != user['username'] and cont == 0:
                    users.append(usuario)
                    print("Adicionou")
                    break
                if username == user['username']:
                    return render_template('error.html', error='Username already in use')
                
            with open('users.json', 'w') as usuarioTemp:
                json.dump(users, usuarioTemp, indent=4)
        return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('user')
    password = request.form.get('password')

    with open('users.json') as usersTemp:
        users = json.load(usersTemp)
        for user in users:    
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                return redirect('/user_screen')
            
            if user not in users:
                print(f"{user}")
                return render_template('error.html', error='Username incorrect/not found')
            
    return redirect('/')
    
@app.route('/user_screen', methods=['POST', 'GET'])
def user_screen():
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    method = request.method

    try:
        with open('workouts.json') as workoutsTemp:
            workouts = json.load(workoutsTemp)
    except FileNotFoundError:
        workouts = []
    except json.JSONDecodeError:
        return render_template('error.html', error='Error reading workouts data')

    # Filtragem dos treinos do usuário
    pre_made_workouts = [workout for workout in workouts if 'users' in workout]
    user_workouts = [workout for workout in workouts if 'username' in workout and workout['username'] == username]

    if method == 'GET':
        return render_template('user_screen.html', pre_made_workouts=pre_made_workouts, user_workouts=user_workouts, logged_in=True)
    
    if method == 'POST':
        button_clicked = request.form.get('button')
        if button_clicked == 'button-a':
            if username not in pre_made_workouts[0].get('users', []):
                pre_made_workouts[0].setdefault('users', []).append(username)
            with open('workouts.json', 'w') as workoutsTemp:
                json.dump(workouts, workoutsTemp, indent=4)
            return redirect('/user_screen')
        elif button_clicked == 'button-b':
            if username not in pre_made_workouts[1].get('users', []):
                pre_made_workouts[1].setdefault('users', []).append(username)
            with open('workouts.json', 'w') as workoutsTemp:
                json.dump(workouts, workoutsTemp, indent=4)
            return redirect('/user_screen')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/make_workout', methods=['POST','GET'])
def make_workout():
    if request.method == 'GET':
        return render_template('make_workout.html', logged_in=True)
    if request.method == 'POST':
        workout_name = request.form.get('workout_name')
        exercises = request.form.get('exercises')
        
        if not workout_name or not exercises:
            return render_template('error.html', error='All fields are required')
        
        exercises_list = [exercise.strip() for exercise in exercises.split(',')]
        
        if 'username' not in session:
            return render_template('error.html', error='User not logged in')
        
        username = session['username']
        
        try:
            with open('workouts.json', 'r') as workoutsTemp:
                workouts = json.load(workoutsTemp)
        except FileNotFoundError:
            workouts = []

        new_workout = {
            'id': generate_new_id(workouts),
            'username': username,
            'workout_name': workout_name,
            'exercises': exercises_list
        }
        workouts.append(new_workout)
        
        with open('workouts.json', 'w') as workoutsTemp:
            json.dump(workouts, workoutsTemp, indent=4)
        
        return redirect('/user_screen')

@app.route('/edit_workout/<int:workout_id>', methods=['POST', 'GET'])
def edit_workout(workout_id):
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    method = request.method

    try:
        with open('workouts.json') as workoutsTemp:
            workouts = json.load(workoutsTemp)
    except FileNotFoundError:
        workouts = []
    except json.JSONDecodeError:
        return render_template('error.html', error='Error reading workouts data')

    # Encontrar o treino específico para editar
    workout_to_edit = next((workout for workout in workouts if workout.get('username') == username and workout.get('id') == workout_id), None)

    if method == 'GET':
        if not workout_to_edit:
            return render_template('error.html', error='Workout not found')
        return render_template('edit_workout.html', workout=workout_to_edit, logged_in=True)
    
    if method == 'POST':
        workout_name = request.form.get('workout_name')
        exercises = request.form.get('exercises')
        
        if not workout_name or not exercises:
            return render_template('error.html', error='All fields are required')
        
        exercises_list = [exercise.strip() for exercise in exercises.split(',')]
        
        # Atualizar treino
        if workout_to_edit:
            workout_to_edit['workout_name'] = workout_name
            workout_to_edit['exercises'] = exercises_list
            with open('workouts.json', 'w') as workoutsTemp:
                json.dump(workouts, workoutsTemp, indent=4)
        
        return redirect('/user_screen')

@app.route('/delete_workout/<int:workout_id>')
def delete_workout(workout_id):
    if 'username' not in session:
        return redirect('/')

    username = session['username']

    try:
        with open('workouts.json') as workoutsTemp:
            workouts = json.load(workoutsTemp)
    except FileNotFoundError:
        workouts = []
    except json.JSONDecodeError:
        return render_template('error.html', error='Error reading workouts data')

    # Filtrar os treinos que não correspondem ao treino que deve ser excluído
    updated_workouts = [workout for workout in workouts if not (workout.get('username') == username and workout.get('id') == workout_id)]

    with open('workouts.json', 'w') as workoutsTemp:
        json.dump(updated_workouts, workoutsTemp, indent=4)

    return redirect('/user_screen')
