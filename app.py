from flask import Flask, render_template, redirect, request, session
from models.user import User, UserFacade
from models.workout import Workout
from models.diet import Diet
from models.goals import GoalManager, AddGoal, EditGoal, RemoveGoal
from models.post import Post
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starbobinho'

api_key = 'iKAAv5nhVv9vmVU2haYAjRMUwhWYfR4C6hoGyja7'

user_facade = UserFacade()

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
            return render_template('error.html', error='Passwords do not match')
        
        new_user = User(username, password, [])
        if not user_facade.add_user(new_user):  # Usando o método da UserFacade
            return render_template('error.html', error='Username already in use')

        return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('password')

        user = user_facade.find_user_by_username(username)  # Usando o método da UserFacade
        if user and user.password == password:
            session['username'] = username
            session['user_id'] = username
            return redirect('/user_screen')
    
    return render_template('error.html', error='Incorrect username or password')

@app.route('/user_screen', methods=['POST', 'GET'])
def user_screen():
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    method = request.method

    workouts = Workout.load_all()

    for workout in workouts:
        workout.average_rating = Workout.calculate_average_rating(workout.ratings)
    
    # Filtra os treinos com id=0 e id=1 para pre_made_workouts
    pre_made_workouts = [[exercise for exercise in group] for workout in workouts if workout.id in [0, 1] for group in workout.exercises]
    
    # Filtra os treinos do usuário
    user_workouts = [workout for workout in workouts if workout.username == username]

    all_workouts = [workout for workout in workouts if workout.id > 1]
    #in [u.username for u in workouts if u.id in [0, 1]]
    #print(f"WORKOUTS_TESTS:{workouts_tests[2]}\n, USER_WORKOUTS:{user_workouts}\n, PRE_MADE_WORKOUTS{pre_made_workouts}")
    print(f"{workouts[0].workout_name} {workouts[0].users}")
    if method == 'GET':
        if username in workouts[0].users:
            return render_template('user_screen.html', pre_made_workouts=pre_made_workouts, user_workouts=user_workouts, all_workouts=all_workouts, plan=1, logged_in=True)
        elif username in workouts[1].users:
            return render_template('user_screen.html', pre_made_workouts=pre_made_workouts, user_workouts=user_workouts, all_workouts=all_workouts, plan=2, logged_in=True)
        else:
            return render_template('user_screen.html', pre_made_workouts=pre_made_workouts, user_workouts=user_workouts, all_workouts=all_workouts, plan="Not chosen yet", logged_in=True)
    
    if method == 'POST':
        button_clicked = int(request.form.get('button'))
        workout_id = button_clicked # Define o treino selecionado (0 ou 1)
        workout = Workout.find_by_id(workout_id)

        # Carregar todos os treinos
        workouts = Workout.load_all()

        # Verificar se o usuário já está em um dos treinos (id=0 ou id=1)
        for w in workouts:
            if w.id in [0, 1] and username in w.users:
                # Remover o usuário do treino onde ele já está
                w.remove_user(username)

        # Adiciona o usuário ao treino escolhido
        workout.add_user(username)

        # Atualiza apenas a chave "users" dos treinos modificados
        for w in workouts:
            if w.id == workout_id:
                w.users = workout.users  # Atualiza a lista de usuários no treino escolhido

        # Salva a lista completa de treinos com as modificações
        Workout.save_all(workouts)
        return render_template('user_screen.html', pre_made_workouts=pre_made_workouts, user_workouts=user_workouts, all_workouts=all_workouts, plan=workout_id+1, logged_in=True)

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
            exercises=exercises_list,
            type='custom'
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

@app.route('/diet', methods=['GET', 'POST'])
def diet_tracking():
    food_info = None
    error_message = None
    username = session.get('username')

    if not username:
        return redirect('/')

    diet = Diet(username)  # Inicializa a dieta do usuário atual

    if request.method == 'POST':
        if 'search' in request.form:
            food_name = request.form.get('food_name')

            # Endpoint da API
            url = 'https://api.nal.usda.gov/fdc/v1/foods/search'

            # Parâmetros da requisição
            params = {
                'api_key': api_key,
                'query': food_name,
                'pageSize': 1
            }

            # Fazendo a requisição
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data['foods']:
                    food_info = data['foods'][0]

                    # Filtrando os nutrientes desejados
                    desired_nutrients = ['Energy', 'Protein', 'Total lipid (fat)', 'Carbohydrate, by difference']
                    nutrients = [
                        {
                            'name': nutrient['nutrientName'],
                            'value': nutrient['value'],
                            'unit': nutrient['unitName'],
                            'total_value': 0  # Inicializa 'total_value'
                        }
                        for nutrient in food_info['foodNutrients']
                        if nutrient['nutrientName'] in desired_nutrients
                    ]

                    food_info = {
                        'description': food_info['description'],
                        'data_type': food_info['dataType'],
                        'fdc_id': food_info['fdcId'],
                        'nutrients': nutrients
                    }

                    # Armazenar o food_info na sessão
                    session['food_info'] = food_info
                else:
                    error_message = 'No food found.'
            else:
                error_message = f'Error: {response.status_code}'

        elif 'add' in request.form and 'food_info' in session:
            quantity = float(request.form.get('quantity', 0))  # Obtém a quantidade fornecida
            diet.add_food(session['food_info'], quantity)
            # Remove food_info da sessão após adicionar
            session.pop('food_info', None)

    # Calcula as calorias totais
    total_calories = sum(
        (nutrient.get('total_value', 0) for food in diet.foods for nutrient in food['nutrients'] if nutrient['name'] == 'Energy')
    )

    # Recupera informações armazenadas na sessão
    if 'food_info' in session:
        food_info = session['food_info']

    return render_template('diet.html', food_info=food_info, error_message=error_message, diet=diet.foods, total_calories=total_calories, logged_in=True)

@app.route('/edit_food/<int:fdc_id>', methods=['POST'])
def edit_food(fdc_id):
    username = session.get('username')
    if not username:
        return redirect('/')

    new_quantity = float(request.form.get('quantity', 0))

    diet = Diet(username)
    diet.edit_food(fdc_id, new_quantity)

    return redirect('/diet')

@app.route('/delete_food/<int:fdc_id>', methods=['POST'])
def delete_food(fdc_id):
    username = session.get('username')
    if not username:
        return redirect('/')

    diet = Diet(username)
    diet.delete_food(fdc_id)

    return redirect('/diet')

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    user_id = session.get('user_id')  # Obtém o ID do usuário logado da sessão
    if not user_id:
        return redirect('/login')  # Redireciona para a página de login se não estiver logado

    if request.method == 'POST':
        action = request.form.get('action')
        goal_id = request.form.get('goal_id')

        if action == 'add':
            AddGoal.process_goal(
                user_id=user_id,
                title=request.form['title'],
                description=request.form['description'],
                deadline=request.form['deadline']
            )
        elif action == 'edit' and goal_id:
            EditGoal.process_goal(
                user_id=user_id,
                goal_id=int(goal_id),
                title=request.form.get('title'),
                description=request.form.get('description'),
                deadline=request.form.get('deadline'),
                status=request.form.get('status')
            )
        elif action == 'delete' and goal_id:
            RemoveGoal.process_goal(user_id=user_id, goal_id=int(goal_id))

        return redirect('/goals')

    goals=GoalManager.load_goals().get(user_id, [])
    return render_template('goals.html', goals=goals, logged_in=True)

@app.route('/rate_workout', methods=['POST'])
def rate_workout():
    rating = int(request.form.get('rating'))
    workout_id = int(request.form.get('plan'))
    is_user_workout = request.form.get('is_user_workout') == 'true'

    username = session.get('username')
    if not username:
        return redirect('/login')  # Redirecionar para o login se não houver usuário na sessão

    workout = Workout.find_by_id(workout_id)
    if workout:
        workout.add_rating(username, rating)
        # Atualiza o workout no arquivo JSON
        workouts = Workout.load_all()
        for w in workouts:
            if w.id == workout_id:
                w.ratings = workout.ratings
        Workout.save_all(workouts)

        # Atualiza a avaliação do usuário
        user_facade = UserFacade()  # Instancia UserFacade
        user_facade.add_rating(username=username, workout_id=workout_id, rating=rating)

    return redirect('/user_screen')

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            create_post()  # Cria o post chamando a função de criação
            return redirect('/forum')

    posts = Post.load_all()
    return render_template('forum.html', posts=posts, logged_in=True)

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    title = request.form.get('title')
    content = request.form.get('content')

    new_post = {
        'id': Post.generate_new_id(),
        'title': title,
        'content': content,
        'username': username,
        'replies': []
    }

    posts = Post.load_all()
    posts.append(new_post)
    Post.save_all(posts)

    return redirect('/forum')

@app.route('/reply_post', methods=['POST'])
def reply_post():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    post_id = int(request.form.get('post_id'))
    content = request.form.get('content')

    Post.add_response(post_id, username, content)

    return redirect('/forum')



if __name__ == '__main__':
    app.run(debug=True)
