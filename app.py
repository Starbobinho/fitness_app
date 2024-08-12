from flask import Flask, render_template, redirect, request, session
from models.user import User
from models.workout import Workout

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starbobinho'

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
        
        new_user = User(username, password)
        if not User.add_user(new_user):
            return render_template('error.html', error='Username already in use')

        return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('user')
    password = request.form.get('password')

    user = User.find_by_username(username)
    if user and user.password == password:
        session['username'] = username
        return redirect('/user_screen')
    
    return render_template('error.html', error='Username incorrect/not found')

@app.route('/user_screen', methods=['POST', 'GET'])
@app.route('/user_screen', methods=['POST', 'GET'])
def user_screen():
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    method = request.method

    workouts = Workout.load_all()
    
    # Filtra os treinos com id=0 e id=1 para pre_made_workouts
    pre_made_workouts = [workout for workout in workouts if workout.id in [0, 1]]
    
    # Filtra os treinos do usuário
    user_workouts = [workout for workout in workouts if workout.username == username]

    if method == 'GET':
        return render_template('user_screen.html', pre_made_workouts=pre_made_workouts, user_workouts=user_workouts, logged_in=True)
    
    if method == 'POST':
        button_clicked = request.form.get('button')
        workout_id = int(button_clicked.split('-')[-1])
        workout = Workout.find_by_id(workout_id)
        if workout and username not in workout.users:
            workout.users.append(username)
            Workout.save_all(workouts)
        return redirect('/user_screen')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/make_workout', methods=['POST', 'GET'])
def make_workout():
    if request.method == 'GET':
        return render_template('make_workout.html', logged_in=True)
    if request.method == 'POST':
        workout_name = request.form.get('workout_name')
        exercises = request.form.get('exercises')
        
        if not workout_name or not exercises:
            return render_template('error.html', error='All fields are required')
        
        exercises_list = [exercise.strip() for exercise in exercises.split(',')]
        username = session['username']
        
        new_workout = Workout(
            id=Workout.generate_new_id(),
            username=username,
            workout_name=workout_name,
            exercises=exercises_list
        )
        workouts = Workout.load_all()
        workouts.append(new_workout)
        Workout.save_all(workouts)
        
        return redirect('/user_screen')

@app.route('/edit_workout/<int:workout_id>', methods=['POST', 'GET'])
def edit_workout(workout_id):
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    method = request.method

    workout = Workout.find_by_id(workout_id)
    if workout and workout.username != username:
        return render_template('error.html', error='Unauthorized access')

    if method == 'GET':
        if not workout:
            return render_template('error.html', error='Workout not found')
        return render_template('edit_workout.html', workout=workout.__dict__, logged_in=True)
    
    if method == 'POST':
        workout_name = request.form.get('workout_name')
        exercises = request.form.get('exercises')
        
        if not workout_name or not exercises:
            return render_template('error.html', error='All fields are required')
        
        exercises_list = [exercise.strip() for exercise in exercises.split(',')]
        
        if workout:
            workout.workout_name = workout_name
            workout.exercises = exercises_list
            workouts = Workout.load_all()
            Workout.save_all(workouts)
        
        return redirect('/user_screen')

@app.route('/delete_workout/<int:workout_id>')
def delete_workout(workout_id):
    if 'username' not in session:
        return redirect('/')

    username = session['username']

    workout = Workout.find_by_id(workout_id)
    if workout and workout.username == username:
        Workout.delete_by_id(workout_id)

    return redirect('/user_screen')

if __name__ == '__main__':
    app.run(debug=True)
