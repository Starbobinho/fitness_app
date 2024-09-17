import json

class Workout:
    def __init__(self, id, username=None, workout_name=None, exercises=None, users=None, ratings=None, **kwargs):
        self.id = id
        self.username = username
        self.workout_name = workout_name
        self.exercises = exercises or []
        self.users = users or []
        self.ratings = ratings or []
        # Handle any additional attributes from kwargs if needed
        for key, value in kwargs.items():
            setattr(self, key, value)

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
