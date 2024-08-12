import json

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @classmethod
    def load_all(cls):
        try:
            with open('users.json') as file:
                data = json.load(file)
                return [cls(user['username'], user['password']) for user in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @classmethod
    def save_all(cls, users):
        with open('users.json', 'w') as file:
            json.dump([user.__dict__ for user in users], file, indent=4)

    @classmethod
    def find_by_username(cls, username):
        users = cls.load_all()
        for user in users:
            if user.username == username:
                return user
        return None

    @classmethod
    def add_user(cls, new_user):
        users = cls.load_all()
        if cls.find_by_username(new_user.username):
            return False
        users.append(new_user)
        cls.save_all(users)
        return True
