import json

class User:
    def __init__(self, username, password, rated=None):
        self.username = username
        self.password = password
        self.rated = rated or []

class UserFacade:
    def __init__(self, file_path='users.json'):
        self.file_path = file_path

    def load_all_users(self):
        try:
            with open(self.file_path) as file:
                data = json.load(file)
                return [User(user['username'], user['password'], user.get('rated', [])) for user in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_all_users(self, users):
        with open(self.file_path, 'w') as file:
            json.dump([user.__dict__ for user in users], file, indent=4)

    def find_user_by_username(self, username):
        users = self.load_all_users()
        for user in users:
            if user.username == username:
                return user
        return None

    def add_user(self, new_user):
        users = self.load_all_users()
        if self.find_user_by_username(new_user.username):
            return False  # User already exists
        users.append(new_user)
        self.save_all_users(users)
        return True

    def add_rating(self, username, workout_id, rating):
        users = self.load_all_users()
        user = self.find_user_by_username(username)
        
        if user:
            # Remove any existing rating for the workout_id
            user.rated = [r for r in user.rated if r['id'] != workout_id]
            # Add the new rating
            user.rated.append({'id': workout_id, 'rating': rating})
            self.save_all_users(users)
            return True
        return False
