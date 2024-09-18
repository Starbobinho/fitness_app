import json

class Workout:
    def __init__(self, id, username=None, workout_name=None, exercises=None, users=None, ratings=None, **kwargs):
        self.id = id
        self.username = username
        self.workout_name = workout_name
        self.exercises = exercises or []
        self.users = users or []
        self.ratings = ratings if isinstance(ratings, list) and all(isinstance(r, dict) for r in ratings) else []
        # Handle any additional attributes from kwargs if needed
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def calculate_average_rating(ratings):
        if not ratings:
            return 0
        total_rating = sum(r['rating'] for r in ratings)
        return total_rating / len(ratings)

    @classmethod
    def load_all(cls):
        try:
            with open('workouts.json') as file:
                data = json.load(file)
                return [cls(**workout) for workout in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @classmethod
    def save_all(cls, workouts):
        with open('workouts.json', 'w') as file:
            json.dump([workout.__dict__ for workout in workouts], file, indent=4)

    @classmethod
    def find_by_id(cls, workout_id):
        workouts = cls.load_all()
        for workout in workouts:
            if workout.id == workout_id:
                return workout
        return None

    @classmethod
    def delete_by_id(cls, workout_id):
        workouts = cls.load_all()
        workouts = [workout for workout in workouts if workout.id != workout_id]
        cls.save_all(workouts)

    @classmethod
    def generate_new_id(cls):
        workouts = cls.load_all()
        if not workouts:
            return 1
        return max(workout.id for workout in workouts) + 1

    def add_user(self, user):
        if user not in self.users:
            self.users.append(user)

    def remove_user(self, user):
        if user in self.users:
            self.users.remove(user)

    @classmethod
    def add_user_to_workout(cls, workout_id, user):
        workouts = cls.load_all()
        workout = cls.find_by_id(workout_id)
        
        if workout:
            workout.add_user(user)
            cls.save_all(workouts)
            return True
        return False

    @classmethod
    def remove_user_from_workout(cls, workout_id, user):
        workouts = cls.load_all()
        workout = cls.find_by_id(workout_id)
        
        if workout:
            workout.remove_user(user)
            cls.save_all(workouts)
            return True
        return False
    
    def add_rating(self, username, rating):
        # Remove qualquer avaliação anterior do usuário para este treino
        self.ratings = [r for r in self.ratings if r['username'] != username]
        # Adiciona a nova avaliação
        self.ratings.append({'username': username, 'rating': rating})