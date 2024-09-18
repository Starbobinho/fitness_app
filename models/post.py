import json

class Post:
    @staticmethod
    def load_all():
        try:
            with open('posts.json') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_all(posts):
        with open('posts.json', 'w') as file:
            json.dump(posts, file, indent=4)

    @staticmethod
    def generate_new_id():
        posts = Post.load_all()
        if not posts:
            return 1
        return max(post['id'] for post in posts) + 1

    @staticmethod
    def find_by_id(post_id):
        posts = Post.load_all()
        for post in posts:
            if post['id'] == post_id:
                return post
        return None

    @staticmethod
    def add_response(post_id, username, content):
        posts = Post.load_all()
        post = next((p for p in posts if p['id'] == post_id), None)
        if post:
            post['replies'].append({'username': username, 'content': content})
            Post.save_all(posts)
