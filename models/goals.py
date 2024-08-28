import json

class Goal:
    def __init__(self, goal_id, user_id, title, description, deadline, status="in progress"):
        self.goal_id = goal_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.deadline = deadline
        self.status = status

    @classmethod
    def load_goals(cls):
        try:
            with open('goals.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @classmethod
    def save_goals(cls, goals_data):
        with open('goals.json', 'w') as f:
            json.dump(goals_data, f, indent=4)

    @classmethod
    def add_goal(cls, user_id, title, description, deadline):
        goals_data = cls.load_goals()

        new_goal_id = len(goals_data.get(user_id, [])) + 1
        new_goal = cls(
            goal_id=new_goal_id,
            user_id=user_id,
            title=title,
            description=description,
            deadline=deadline
        )

        if user_id not in goals_data:
            goals_data[user_id] = []

        goals_data[user_id].append(new_goal.__dict__)
        cls.save_goals(goals_data)
        return new_goal

    @classmethod
    def edit_goal(cls, user_id, goal_id, title=None, description=None, deadline=None, status=None):
        goals_data = cls.load_goals()
        user_goals = goals_data.get(user_id, [])

        for goal in user_goals:
            if goal['goal_id'] == goal_id:
                if title:
                    goal['title'] = title
                if description:
                    goal['description'] = description
                if deadline:
                    goal['deadline'] = deadline
                if status:
                    goal['status'] = status

                cls.save_goals(goals_data)
                return goal
        return None

    @classmethod
    def remove_goal(cls, user_id, goal_id):
        goals_data = cls.load_goals()
        user_goals = goals_data.get(user_id, [])

        goals_data[user_id] = [goal for goal in user_goals if goal['goal_id'] != goal_id]

        cls.save_goals(goals_data)
        return True
