import csv
import os
import random
import statistics
import json
from collections import deque

class Habit:
    def __init__(self, name, parameters, weights, difficulty='Normal'):
        self.name = name
        self.parameters = parameters  # List of parameter names
        self.weights = weights  # Dict: {parameter_name: weight}
        self.difficulty = difficulty
        self.history_file = f"{name}_history.csv"
        self.elo = 1000  # Default ELO
        self.load_elo()

    def load_elo(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_line = lines[-1].strip().split(',')
                    self.elo = float(last_line[-1])

    def save_session(self, user_score, adversary_score, result):
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['User Score', 'Adversary Score', 'Result', 'New ELO'])

        with open(self.history_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([user_score, adversary_score, result, self.elo])

    def calculate_score(self, performance):
        return sum(performance[param] * self.weights.get(param, 1) for param in self.parameters)

    def generate_adversary_score(self):
        recent_scores = []
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        recent_scores.append(float(row['User Score']))
                    except:
                        pass
        avg = sum(recent_scores[-5:]) / min(len(recent_scores[-5:]), 5) if recent_scores else 10

        if self.difficulty == 'Easy':
            return random.uniform(0.7, 0.9) * avg
        elif self.difficulty == 'Hard':
            return random.uniform(1.1, 1.3) * avg
        return random.uniform(0.9, 1.1) * avg

    def update_elo(self, user_score, adversary_score):
        result = 1 if user_score > adversary_score else 0 if user_score < adversary_score else 0.5
        expected_score = 1 / (1 + 10 ** ((adversary_score - user_score) / 400))
        k = 32
        self.elo += k * (result - expected_score)
        self.elo = round(self.elo, 2)
        self.save_session(user_score, adversary_score, result)
        return result

    def __init__(self, name, params, initial_rating=500, window_size=30, k_factor=20):
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
        self.habits[name] = Habit(name, params, initial_rating=500, k_factor=20)
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
                        initial_rating=data.get('rating', 500),
                        k_factor=data.get('k_factor', 20)
                    )
