from datetime import datetime
import os
from pathlib import Path
import sqlite3

TEXTBOOK_VOCAB_PATH = "textbook_vocab"
PLAYER_STATISTICS_PATH = "player_statistics"
DB_PATH = os.path.join(PLAYER_STATISTICS_PATH, "kenta_vocab_stats.db")
MAX_CHAPTERS = sum(1 for p in Path(TEXTBOOK_VOCAB_PATH).iterdir() if p.is_file())

# Helper function to load words from a textbook_vocab chapter file
# Retunrs a dictionary of spanish: english pairs for the given chapter
def add_chapter_to_words(chapter: int) -> dict:
    words = {}
    current_file = os.path.join(TEXTBOOK_VOCAB_PATH, f"chapter_{chapter}.txt")
    with open(current_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                spanish, english = line.split("\\")
                words[spanish] = english
    return words

# Returns a dictionary of chapter dictionaries, each chapter dictionary contains spanish: english pairs
def load_textbook_words(chapter: int = 0) -> dict:
    textbook_words = {}
    all_chapters = False

    try:
        # Evaluate user input for chapter loading
        # If chapter is 0, load all chapters
        # Also check if chapter is within valid range
        if chapter == 0:
            all_chapters = True
        elif chapter > 0 and chapter <= MAX_CHAPTERS:
            pass
        else:
            raise Exception(f"Chapter number must be between 0 and {MAX_CHAPTERS}.")
        
        # Load words from specified chapters into list of dictionaries
        if all_chapters:
            for i in range(1, MAX_CHAPTERS + 1):
                textbook_words[i] = add_chapter_to_words(i)
        else:
            textbook_words[chapter] = add_chapter_to_words(chapter)
    except Exception as e:
        print(f"Error loading textbook words: {e}")
        exit()

    return textbook_words

# Create the player_stats table if it does not exist
def create_table() -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter INTEGER,
                    english TEXT,
                    spanish TEXT,
                    num_correct INTEGER,
                    num_wrong INTEGER
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
        exit()

# Returns a dictionary of chapter dictionaries, each chapter dictionary contains indexes for each word and its stats as a dictionary
def load_player_stats(chapter: int) -> dict:
    player_stats = {}

    # Ensure the database and table exist
    create_table()

    # Load player statistics from the database
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if chapter == 0:
                for i in range(1, MAX_CHAPTERS + 1):
                    cursor.execute("SELECT * FROM player_stats WHERE chapter=?", (i,))
                    rows = cursor.fetchall()
                    player_stats[i] = {}
                    for row in rows:
                        player_stats[i][row[0]] = {
                            "chapter": row[1],
                            "english": row[2],
                            "spanish": row[3],
                            "num_correct": row[4],
                            "num_wrong": row[5]
                        }
            else:
                cursor.execute("SELECT * FROM player_stats WHERE chapter=?", (chapter,))
                rows = cursor.fetchall()
                player_stats[chapter] = {}
                for row in rows:
                    player_stats[chapter][row[0]] = {
                        "chapter": row[1],
                        "english": row[2],
                        "spanish": row[3],
                        "num_correct": row[4],
                        "num_wrong": row[5]
                    }

    except Exception as e:
        print(f"Error loading player statistics: {e}")
        exit()
    
    return player_stats

def create_player_stats_entry(chapter: int, english: str, spanish: str) -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO player_stats (chapter, english, spanish, num_correct, num_wrong)
                VALUES (?, ?, ?, 0, 0)
            """, (chapter, english, spanish))
            conn.commit()
    except Exception as e:
        print(f"Error creating player stats entry: {e}")
        exit()

def load_word_data(chapter: int = 0) -> dict:
    # Dictionary of chapter dictionaries
    textbook_words = load_textbook_words(chapter)

    # Dictionary of chapter dictionaries, each dictionary has a chapter of dictionaries
    player_stats = load_player_stats(chapter)

    # For each chapter in the textbook words, check if each word exists in player stats
    # If not, create a new entry in player stats
    if chapter == 0:
        for i in range(1, MAX_CHAPTERS + 1):
            for spanish, english in textbook_words[i].items():
                found = False
                for stats in player_stats[i].values():
                    if stats["chapter"] == i and stats["english"] == english and stats["spanish"] == spanish:
                        found = True
                        break
                if not found:
                    create_player_stats_entry(i, english, spanish)

    # If loading a specific chapter, check only that chapter
    else:
        for spanish, english in textbook_words[chapter].items():
            found = False
            for stats in player_stats.values():
                if stats["chapter"] == chapter and stats["english"] == english and stats["spanish"] == spanish:
                    found = True
                    break
            if not found:
                create_player_stats_entry(chapter, english, spanish)
    
    # Reload player stats to include any new entries
    player_stats = load_player_stats(chapter)

    return player_stats

def save_game_data(chapter: str = 0, num_correct: int = 0, num_wrong: int = 0, time_limit: int = 60, correct: list = [], incorrect: list = []) -> None:
    try:
        save_file = os.path.join("player_statistics", f"{datetime.now().strftime('%Y-%m-%d')}.txt")
        with open(save_file, "a", encoding="utf-8") as f:
            f.write(f"{time_limit=}, {chapter=}, {num_correct=}, {num_wrong=}, {incorrect=}, {correct=}\n")
       
    except Exception as e:
        print(f"Error saving data: {e}")

def update_player_stats_entry(chapter: int, english: str, spanish: str, correct: bool) -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if correct:
                cursor.execute("""
                    UPDATE player_stats
                    SET num_correct = num_correct + 1
                    WHERE chapter = ? AND english = ? AND spanish = ?
                """, (chapter, english, spanish))
            else:
                cursor.execute("""
                    UPDATE player_stats
                    SET num_wrong = num_wrong + 1
                    WHERE chapter = ? AND english = ? AND spanish = ?
                """, (chapter, english, spanish))
            conn.commit()
    except Exception as e:
        print(f"Error updating player stats entry: {e}")
        exit()