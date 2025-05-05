import csv
import os
import random
import statistics
import json
from collections import deque

class Habit:
    def __init__(self, name, params, initial_rating=1200, window_size=30, k_factor=20):
        self.name = name
        self.params = params
        self.rating = initial_rating
        self.scores = deque(maxlen=window_size)
        self.k_factor = k_factor
        self.history_file = f"habit_{name}.csv"
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        self.scores.append(float(row['total_score']))
                        self.rating = float(row['rating'])
                    except (KeyError, ValueError):
                        continue

    def save_session(self, values, total_score, adv_score, delta):
        file_exists = os.path.exists(self.history_file)
        with open(self.history_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                headers = ['session', 'total_score', 'adv_score', 'delta', 'rating'] + list(values.keys())
                writer.writerow(headers)

            session_num = len(self.scores)
            row = [session_num, total_score, adv_score, delta, self.rating] + list(values.values())
            writer.writerow(row)

    def generate_adversary(self, difficulty):
        if not self.scores:
            base = sum(weight * 1 for weight in self.params.values())
            actual = random.uniform(base * 0.8, base * 1.2)
            return (base * 0.8, base * 1.2, actual)

        mu = statistics.mean(self.scores)
        
        # Calculate standard deviation with fallback
        if len(self.scores) > 1:
            sigma = statistics.stdev(self.scores)
        else:
            sigma = mu * 0.2  # Default to 20% of mean for new habits

        # Define ranges based on difficulty
        if difficulty == "easy":
            low = max(0, mu - 1.5 * sigma)
            high = mu
        elif difficulty == "hard":
            low = mu
            high = mu + 1.5 * sigma
        else:  # normal
            low = max(0, mu - sigma)
            high = mu + sigma

        # Generate actual score within defined range
        actual = random.uniform(low, high)
        return (low, high, actual)

    def calculate_score(self, values):
        return sum(value * self.params.get(param, 0) for param, value in values.items())

    def update_rating(self, user_score, adv_score):
        expected = 1 / (1 + 10 ** ((adv_score - self.rating) / 400))
        actual = 1 if user_score > adv_score else 0.5 if user_score == adv_score else 0
        delta = self.k_factor * (actual - expected)
        self.rating += delta
        return delta

class HabitManager:
    def __init__(self):
        self.habits = {}
        self.current_habit = None
        self.load_habits()

    def create_habit(self, name, params):
        self.habits[name] = Habit(name, params)
        self.save_habits()

    def delete_habit(self, name):
        if name in self.habits:
            del self.habits[name]
            history_file = f"habit_{name}.csv"
            if os.path.exists(history_file):
                os.remove(history_file)
            self.save_habits()

    def set_current_habit(self, name):
        self.current_habit = self.habits.get(name)

    def update_habit_params(self, name, new_params):
        if name in self.habits:
            self.habits[name].params = new_params
            self.save_habits()

    def save_habits(self):
        habit_data = {
            name: {
                'params': habit.params,
                'rating': habit.rating,
                'k_factor': habit.k_factor
            }
            for name, habit in self.habits.items()
        }
        with open('habits.json', 'w') as f:
            json.dump(habit_data, f, indent=4)

    def load_habits(self):
        if os.path.exists('habits.json'):
            with open('habits.json', 'r') as f:
                habit_data = json.load(f)
                for name, data in habit_data.items():
                    self.habits[name] = Habit(
                        name=name,
                        params=data['params'],
                        initial_rating=data.get('rating', 1200),
                        k_factor=data.get('k_factor', 20)
                    )
