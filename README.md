# ELOHabits

<p align="center">
  <img src="https://github.com/user-attachments/assets/75a544f3-a42b-4e11-bffd-c4f68ccfc818" alt="Habit Game Tracker Logo" width="500"/>
</p>
A program that allows users to develop habits by competing in personal proximal development.

# ELOHabits: Habit Game Tracker

ELOHabits is a gamified habit tracker (though 'tracking' is not yet an actually implemented feature 😅) that uses a simplified ELO-like rating system (think, League of Legends) to help you build and maintain habits. Challenge yourself with generated adversaries, and climb the rating ladder of your own habit.

> **Note:** This project was primarily generated by AI (ChatGPT, Qodo, GitHub Copilot, Deepseek), with my assistance for direction, review, and integration; even this Readme file is written by AI, sorry xd

## Features

- **Gamified Habit Tracking:** Each habit has a rating and rank, inspired by competitive games.
- **Custom Parameters:** Define your own parameters and weights for each habit.
- **Adversary Generation:** Challenge yourself with AI-generated adversary scores based on your history and chosen difficulty.
- **Data Persistence:** All data is stored in a local SQLite database.
- **Backup & Restore:** Easily backup or restore your habit data with ZIP files.
- **Icon & Description Support:** Personalize habits with icons and descriptions.

![Mainwindow](https://github.com/user-attachments/assets/6c10fae7-9e1a-4aa5-9101-f75452ff6289)

## Getting Started

Just download the archive, extract it, and run either the shortcut or the original .exe ("ELOHabits\dist\NEW ELOhabit 1.0.exe")

### Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)

### Your Installation (optional)

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/ELOHabits.git
    cd ELOHabits
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the application:**
    ```sh
    python habit_tracker_gui.py
    ```

### Building an Executable

To build a standalone executable (Windows):

```sh
pip install pyinstaller
pyinstaller --onefile --windowed habit_tracker_gui.py --icon=habit_icon.ico
```

The executable will be in the `dist/` folder.

## Project Structure

- [`habit_tracker_gui.py`](habit_tracker_gui.py): Main GUI application.
- [`habit_model.py`](habit_model.py): Habit and HabitManager logic.
- [`db/database.py`](db/database.py): Database helpers and schema.
- [`data/`](data/): Stores your SQLite database and backups.
- [`photos/`](photos/): Optional icons for habits.
- [`backups/`](backups/): Backup scripts and some older files.

## Acknowledgements

- This project was primarily generated by AI (ChatGPT, Qodo, GitHub Copilot, Deepseek), with my assistance for direction, review, and integration;
- Thanks to the open-source Python community for libraries such as Tkinter, NumPy, and Pillow.
