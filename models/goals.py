import json
from abc import ABC, abstractmethod

class GoalManager(ABC):
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
    def process_goal(cls, user_id, **kwargs):
        goals_data = cls.load_goals()
        result = cls._process(goals_data, user_id, **kwargs)
        cls.save_goals(goals_data)
        return result

    @abstractmethod
    def _process(cls, goals_data, user_id, **kwargs):
        pass

class AddGoal(GoalManager):
    @classmethod
    def _process(cls, goals_data, user_id, title, description, deadline):
        new_goal_id = len(goals_data.get(user_id, [])) + 1
        new_goal = {
            "goal_id": new_goal_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "deadline": deadline,
            "status": "in progress"
        }

        if user_id not in goals_data:
            goals_data[user_id] = []
        goals_data[user_id].append(new_goal)
        return new_goal

class EditGoal(GoalManager):
    @classmethod
    def _process(cls, goals_data, user_id, goal_id, title=None, description=None, deadline=None, status=None):
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
                return goal
        return None

class RemoveGoal(GoalManager):
    @classmethod
    def _process(cls, goals_data, user_id, goal_id):
        user_goals = goals_data.get(user_id, [])
        goals_data[user_id] = [goal for goal in user_goals if goal['goal_id'] != goal_id]
        return True
