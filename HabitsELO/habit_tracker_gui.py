import tkinter as tk
from tkinter import ttk, messagebox
from habit_model import HabitManager

class HabitTrackerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Habit Game Tracker")
        master.geometry("700x450")

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

        # Middle frame for parameter input and difficulty selection
        middle_frame = ttk.Frame(self.master)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Parameters subframe
        self.param_frame = ttk.Frame(middle_frame)
        self.param_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Difficulty and adversary info
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=10)

        ttk.Label(right_frame, text="Difficulty:").pack(anchor=tk.W, pady=(0, 5))
        ttk.OptionMenu(right_frame, self.difficulty, "normal", "easy", "normal", "hard").pack(fill=tk.X)

        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(right_frame, text="Adversary Score Range:").pack(anchor=tk.W)
        self.adv_range_var = tk.StringVar(value="Select a habit to see")
        ttk.Label(right_frame, textvariable=self.adv_range_var, font=('', 10, 'bold')).pack(pady=5)

        ttk.Button(right_frame, text="Generate Adversary", command=self.generate_adversary).pack(fill=tk.X, pady=5)

        # Submit and controls frame
        bottom_frame = ttk.Frame(self.master)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(bottom_frame, text="Submit Session", command=self.submit_session).pack(side=tk.RIGHT)

        # Results display
        self.results_frame = ttk.Frame(self.master)
        self.results_frame.pack(fill=tk.BOTH, padx=10, pady=(0, 10))

        ttk.Label(self.results_frame, text="Session Results", font=('', 12, 'bold')).pack(anchor=tk.W)
        self.results_text = tk.Text(self.results_frame, height=8, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, pady=5)

        # Try again button
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
            self.adv_range_var.set("No habits available")

    def clear_param_fields(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()

    def on_habit_select(self, event=None):
        habit_name = self.habit_combobox.get()
        if not habit_name:
            return

        self.manager.set_current_habit(habit_name)
        habit = self.manager.current_habit
        self.clear_param_fields()

        # Create headers
        ttk.Label(self.param_frame, text="Parameter", font=('', 10, 'bold')).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.param_frame, text="Value", font=('', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(self.param_frame, text="Weight", font=('', 10, 'bold')).grid(row=0, column=2, padx=5, pady=2)

        # Add tooltip or help text
        help_text = "Weights determine how much each parameter contributes to your final score."
        ttk.Label(self.param_frame, text=help_text, font=('', 8, 'italic'), wraplength=300).grid(row=1, column=0, columnspan=3, padx=5, pady=2, sticky=tk.W)

        # Create input fields for each parameter
        row = 2  # Start from row 2 after headers and help text
        self.current_values.clear()
        self.weight_vars.clear()

        for i, (param, weight) in enumerate(habit.params.items()):
            # Parameter label
            ttk.Label(self.param_frame, text=param.capitalize()).grid(row=row, column=0, padx=5, pady=2, sticky=tk.E)

            # Value entry
            val_var = tk.DoubleVar(value=0)
            self.current_values[param] = val_var
            ttk.Entry(self.param_frame, textvariable=val_var, width=8).grid(row=row, column=1, padx=5, pady=2)

            # Weight display
            weight_var = tk.DoubleVar(value=weight)
            self.weight_vars[param] = weight_var
            ttk.Label(self.param_frame, textvariable=weight_var).grid(row=row, column=2, padx=5, pady=2)

            row += 1

        # Reset adversary info and results on habit change
        self.adv_range_var.set("Generate a new adversary")
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.try_again_button.config(state=tk.DISABLED)
        if hasattr(self, 'adv_range'):
            delattr(self, 'adv_range')

    def show_new_habit_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Create New Habit")

        ttk.Label(dialog, text="Habit Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        params_frame = ttk.Frame(dialog)
        params_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        param_entries = []

        def add_param_field():
            row = len(param_entries)
            param_name = ttk.Entry(params_frame, width=15)
            param_name.grid(row=row, column=0, padx=2)
            param_weight = ttk.Entry(params_frame, width=5)
            param_weight.grid(row=row, column=1, padx=2)
            param_entries.append((param_name, param_weight))

        add_param_field()  # Initial empty field

        ttk.Button(dialog, text="Add Parameter", command=add_param_field).grid(row=2, column=0, pady=5)

        def save_habit():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a habit name")
                return

            params = {}
            for param_entry, weight_entry in param_entries:
                pname = param_entry.get().strip().lower()
                pweight = weight_entry.get()

                if not pname:
                    continue

                try:
                    params[pname] = float(pweight)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid weight for {pname}")
                    return

            if not params:
                messagebox.showerror("Error", "At least one parameter required")
                return

            self.manager.create_habit(name, params)
            self.refresh_habit_list()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save_habit).grid(row=2, column=1, pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=2, column=2, pady=5)

    def edit_current_habit(self):
        habit_name = self.habit_combobox.get()
        if not habit_name:
            return

        habit = self.manager.current_habit
        if not habit:
            return

        dialog = tk.Toplevel(self.master)
        dialog.title(f"Edit Habit: {habit_name}")

        ttk.Label(dialog, text="Parameters and Weights", font=('', 10, 'bold')).grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        ttk.Label(dialog, text="Weights determine how much each parameter contributes to your final score.\n"
                              "Higher weights mean the parameter has more impact on your total.",
                  wraplength=300).grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

        params_frame = ttk.Frame(dialog)
        params_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Headers
        ttk.Label(params_frame, text="Parameter Name").grid(row=0, column=0, padx=2)
        ttk.Label(params_frame, text="Weight").grid(row=0, column=1, padx=2)

        param_entries = []

        # Add existing parameters
        for i, (param, weight) in enumerate(habit.params.items()):
            param_name = ttk.Entry(params_frame, width=15)
            param_name.insert(0, param)
            param_name.grid(row=i+1, column=0, padx=2)

            param_weight = ttk.Entry(params_frame, width=5)
            param_weight.insert(0, str(weight))
            param_weight.grid(row=i+1, column=1, padx=2)

            param_entries.append((param_name, param_weight))

        def add_param_field():
            row = len(param_entries) + 1
            param_name = ttk.Entry(params_frame, width=15)
            param_name.grid(row=row, column=0, padx=2)
            param_weight = ttk.Entry(params_frame, width=5)
            param_weight.grid(row=row, column=1, padx=2)
            param_entries.append((param_name, param_weight))

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        ttk.Button(button_frame, text="Add Parameter", command=add_param_field).pack(side=tk.LEFT, padx=5)

        def save_edits():
            params = {}
            for param_entry, weight_entry in param_entries:
                pname = param_entry.get().strip().lower()
                pweight = weight_entry.get()

                if not pname:
                    continue

                try:
                    params[pname] = float(pweight)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid weight for {pname}")
                    return

            if not params:
                messagebox.showerror("Error", "At least one parameter required")
                return

            self.manager.update_habit_params(habit_name, params)
            self.refresh_habit_list()
            dialog.destroy()

        ttk.Button(button_frame, text="Save", command=save_edits).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_current_habit(self):
        name = self.habit_combobox.get()
        if not name:
            return

        if messagebox.askyesno("Confirm Delete", f"Delete habit '{name}'?"):
            self.manager.delete_habit(name)
            self.refresh_habit_list()

    def generate_adversary(self):
        if not self.manager.current_habit:
            messagebox.showerror("Error", "No habit selected")
            return

        habit = self.manager.current_habit
        adv_low, adv_high, _ = habit.generate_adversary(self.difficulty.get())
        self.adv_range = (adv_low, adv_high)
        self.adv_range_var.set(f"{adv_low:.1f} - {adv_high:.1f}")

        # Clear previous results and reset try again button
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.try_again_button.config(state=tk.DISABLED)

    def submit_session(self):
        if not self.manager.current_habit:
            messagebox.showerror("Error", "No habit selected")
            return

        if not hasattr(self, 'adv_range'):
            messagebox.showerror("Error", "Please generate an adversary first")
            return

        try:
            values = {param: var.get() for param, var in self.current_values.items()}
        except tk.TclError:
            messagebox.showerror("Error", "Invalid input values")
            return

        adv_low, adv_high = self.adv_range
        habit = self.manager.current_habit
        _, _, adv_actual = habit.generate_adversary(self.difficulty.get())

        user_score = habit.calculate_score(values)
        delta = habit.update_rating(user_score, adv_actual)
        habit.scores.append(user_score)
        habit.save_session(values, user_score, adv_actual, delta)

        result_text = (
            f"Adversary Range: {adv_low:.1f} - {adv_high:.1f}\n"
            f"Adversary Actual: {adv_actual:.1f}\n"
            f"Your Score: {user_score:.1f}\n"
            f"Result: {'Victory' if user_score > adv_actual else 'Draw' if user_score == adv_actual else 'Defeat'}\n"
            f"Rating Change: {delta:+.1f} → New Rating: {habit.rating:.1f}"
        )

        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)
        self.results_text.config(state=tk.DISABLED)

        self.try_again_button.config(state=tk.NORMAL)
        delattr(self, 'adv_range')

    def reset_form(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)

        self.adv_range_var.set("Generate a new adversary")

        for var in self.current_values.values():
            var.set(0)

        self.try_again_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerGUI(root)
    root.mainloop()
