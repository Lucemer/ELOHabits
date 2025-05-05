import tkinter as tk
from tkinter import ttk, messagebox
import os
from habit_model import HabitManager

class HabitTrackerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Habit Game Tracker")
        master.geometry("700x500")

        self.manager = HabitManager()
        self.current_values = {}
        self.weight_vars = {}
        self.difficulty = tk.StringVar(value="normal")

        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', padding=6)
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)

        self.create_widgets()
        self.refresh_habit_list()

    def create_widgets(self):
        # Top frame for habit selection and management
        top_frame = ttk.Frame(self.master)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(top_frame, text="Select Habit:").pack(side=tk.LEFT, padx=5)
        self.habit_combobox = ttk.Combobox(top_frame, state='readonly')
        self.habit_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.habit_combobox.bind('<<ComboboxSelected>>', self.on_habit_select)

        ttk.Button(top_frame, text="New Habit", command=self.show_new_habit_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Edit Habit", command=self.edit_current_habit).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Delete Habit", command=self.delete_current_habit).pack(side=tk.LEFT)

        # Middle frame for parameters and difficulty
        middle_frame = ttk.Frame(self.master)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Parameters subframe
        self.param_frame = ttk.Frame(middle_frame)
        self.param_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Right frame for difficulty, rating, adversary
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=10)

        ttk.Label(right_frame, text="Difficulty:").pack(anchor=tk.W, pady=(0,5))
        ttk.OptionMenu(right_frame, self.difficulty, "normal", "easy", "normal", "hard").pack(fill=tk.X)

        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(right_frame, text="Current Rating:").pack(anchor=tk.W)
        self.rating_var = tk.StringVar(value="N/A")
        ttk.Label(right_frame, textvariable=self.rating_var, font=('',10,'bold')).pack(pady=5)

        ttk.Label(right_frame, text="Adversary Range:").pack(anchor=tk.W, pady=(10,0))
        self.adv_range_var = tk.StringVar(value="Generate adversary")
        ttk.Label(right_frame, textvariable=self.adv_range_var, font=('',10,'bold')).pack(pady=5)

        ttk.Button(right_frame, text="Generate Adversary", command=self.generate_adversary).pack(fill=tk.X, pady=5)

        # Bottom frame for session submit
        bottom_frame = ttk.Frame(self.master)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(bottom_frame, text="Submit Session", command=self.submit_session).pack(side=tk.RIGHT)

        # Results display
        self.results_frame = ttk.Frame(self.master)
        self.results_frame.pack(fill=tk.BOTH, padx=10, pady=(0,10))
        ttk.Label(self.results_frame, text="Session Results", font=('',12,'bold')).pack(anchor=tk.W)
        self.results_text = tk.Text(self.results_frame, height=6, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, pady=5)
        self.try_again_button = ttk.Button(self.results_frame, text="Try Another Session", command=self.reset_form)
        self.try_again_button.pack(side=tk.RIGHT)
        self.try_again_button.config(state=tk.DISABLED)

    def refresh_habit_list(self):
        habits = list(self.manager.habits.keys())
        self.habit_combobox['values'] = habits
        if habits:
            self.habit_combobox.set(habits[0])
            self.on_habit_select()
        else:
            self.habit_combobox.set('')
            self.clear_param_fields()
            self.rating_var.set("N/A")
            self.adv_range_var.set("No habits available")

    def clear_param_fields(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()

    def on_habit_select(self, event=None):
        name = self.habit_combobox.get()
        if not name:
            return
        self.manager.set_current_habit(name)
        habit = self.manager.current_habit

        # Update rating
        self.rating_var.set(f"{habit.rating:.1f}")

        # Display parameters
        self.clear_param_fields()
        ttk.Label(self.param_frame, text="Parameter", font=('',10,'bold')).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(self.param_frame, text="Value", font=('',10,'bold')).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(self.param_frame, text="Weight", font=('',10,'bold')).grid(row=0, column=2, padx=5, pady=2)

        self.current_values.clear()
        self.weight_vars.clear()
        for i, (param, weight) in enumerate(habit.params.items(), start=1):
            ttk.Label(self.param_frame, text=param.capitalize()).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            val_var = tk.DoubleVar(value=0)
            self.current_values[param] = val_var
            ttk.Entry(self.param_frame, textvariable=val_var, width=8).grid(row=i, column=1, padx=5)
            weight_var = tk.DoubleVar(value=weight)
            self.weight_vars[param] = weight_var
            ttk.Label(self.param_frame, textvariable=weight_var).grid(row=i, column=2, padx=5)

        self.adv_range_var.set("Generate adversary")
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.try_again_button.config(state=tk.DISABLED)
        if hasattr(self, 'adv_range'):
            delattr(self, 'adv_range')

    def generate_adversary(self):
        habit = self.manager.current_habit
        low, high, actual = habit.generate_adversary(self.difficulty.get())
        self.adv_range = (low, high)
        self.adv_range_var.set(f"{low:.1f} - {high:.1f}")
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.try_again_button.config(state=tk.DISABLED)

    def submit_session(self):
        habit = self.manager.current_habit
        if not hasattr(self, 'adv_range'):
            messagebox.showerror("Error", "Please generate an adversary first")
            return

        values = {param: var.get() for param, var in self.current_values.items()}
        user_score = habit.calculate_score(values)
        low, high = self.adv_range
        _, _, adv_actual = habit.generate_adversary(self.difficulty.get())

        delta = habit.update_rating(user_score, adv_actual)
        habit.scores.append(user_score)
        habit.save_session(values, user_score, adv_actual, delta)

        # Update UI
        self.rating_var.set(f"{habit.rating:.1f}")
        result = 'Victory' if user_score > adv_actual else 'Draw' if user_score == adv_actual else 'Defeat'
        text = (
            f"Adversary Range: {low:.1f} - {high:.1f}\n"
            f"Adversary Actual: {adv_actual:.1f}\n"
            f"Your Score: {user_score:.1f}\n"
            f"Result: {result}\n"
            f"Rating Change: {delta:+.1f}"
        )
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)
        self.try_again_button.config(state=tk.NORMAL)
        delattr(self, 'adv_range')

    def reset_form(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.adv_range_var.set("Generate adversary")
        for var in self.current_values.values():
            var.set(0)
        self.try_again_button.config(state=tk.DISABLED)

    def show_new_habit_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Create New Habit")
        ttk.Label(dialog, text="Habit Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        params_frame = ttk.Frame(dialog)
        params_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        param_entries = []
        def add_field():
            idx = len(param_entries)
            p_ent = ttk.Entry(params_frame, width=15)
            w_ent = ttk.Entry(params_frame, width=5)
            p_ent.grid(row=idx, column=0, padx=2)
            w_ent.grid(row=idx, column=1, padx=2)
            param_entries.append((p_ent, w_ent))
        add_field()
        ttk.Button(dialog, text="Add Parameter", command=add_field).grid(row=2, column=0, pady=5)

        def save_habit():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a habit name")
                return
            params = {}
            for p_ent, w_ent in param_entries:
                p = p_ent.get().strip().lower()
                try:
                    w = float(w_ent.get())
                except ValueError:
                    messagebox.showerror("Error", f"Invalid weight for {p}")
                    return
                if p:
                    params[p] = w
            if not params:
                messagebox.showerror("Error", "At least one parameter required")
                return
            self.manager.create_habit(name, params)
            self.refresh_habit_list()
            dialog.destroy()
        ttk.Button(dialog, text="Save", command=save_habit).grid(row=2, column=1)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=2, column=2)

    def edit_current_habit(self):
        name = self.habit_combobox.get()
        habit = self.manager.current_habit
        if not habit:
            return
        dialog = tk.Toplevel(self.master)
        dialog.title(f"Edit Habit: {name}")

        params_frame = ttk.Frame(dialog)
        params_frame.pack(padx=5, pady=5)
        param_entries = []
        for idx, (p, w) in enumerate(habit.params.items()):
            p_ent = ttk.Entry(params_frame, width=15)
            p_ent.insert(0, p)
            w_ent = ttk.Entry(params_frame, width=5)
            w_ent.insert(0, str(w))
            p_ent.grid(row=idx, column=0, padx=2)
            w_ent.grid(row=idx, column=1, padx=2)
            param_entries.append((p_ent, w_ent))

        def add_edit_field():
            idx = len(param_entries)
            p_ent = ttk.Entry(params_frame, width=15)
            w_ent = ttk.Entry(params_frame, width=5)
            p_ent.grid(row=idx, column=0, padx=2)
            w_ent.grid(row=idx, column=1, padx=2)
            param_entries.append((p_ent, w_ent))
        ttk.Button(dialog, text="Add Parameter", command=add_edit_field).pack(pady=5)

        def save_edits():
            new_params = {}
            for p_ent, w_ent in param_entries:
                p = p_ent.get().strip().lower()
                try:
                    w = float(w_ent.get())
                except ValueError:
                    messagebox.showerror("Error", f"Invalid weight for {p}")
                    return
                if p:
                    new_params[p] = w
            if not new_params:
                messagebox.showerror("Error", "At least one parameter required")
                return
            self.manager.update_habit_params(name, new_params)
            self.refresh_habit_list()
            dialog.destroy()
        ttk.Button(dialog, text="Save", command=save_edits).pack(side=tk.LEFT, padx=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)

    def delete_current_habit(self):
        name = self.habit_combobox.get()
        if not name:
            return
        if messagebox.askyesno("Confirm Delete", f"Delete habit '{name}'?"):
            self.manager.delete_habit(name)
            self.refresh_habit_list()

if __name__ == "__main__":
    root = tk.Tk()
    icon_path = "habit_icon3.ico"
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print(f"Warning: Icon file '{icon_path}' not found. Using default icon.")
    app = HabitTrackerGUI(root)
    root.mainloop()
