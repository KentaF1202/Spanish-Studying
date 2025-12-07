from datetime import datetime
import os
from pathlib import Path
import sqlite3

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTBOOK_VOCAB_PATH = os.path.join(ROOT_DIR_PATH, "textbook_vocab")
DB_PATH = "kenta_vocab_stats.db"

def add_chapter_to_words(words: dict, chapter: int) -> dict:
    current_file = os.path.join(TEXTBOOK_VOCAB_PATH, f"chapter_{chapter}.txt")
    with open(current_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                spanish, english = line.split("\\")
                words[spanish] = english
    return words

def load_textbook_words(chapter: int = 0) -> dict:
    path_obj = Path(TEXTBOOK_VOCAB_PATH)
    max_chapters = sum(1 for p in path_obj.iterdir() if p.is_file())
    textbook_words = {}
    all_chapters = False

    try:
        # Evaluate user input for chapter loading
        # If chapter is 0, load all chapters
        # Also check if chapter is within valid range
        if chapter == 0:
            all_chapters = True
        elif chapter > 0 and chapter <= max_chapters:
            pass
        else:
            raise Exception(f"Chapter number must be between 0 and {max_chapters}.")
        
        # Load words from specified chapters into dictionary
        if all_chapters:
            for i in range(1, max_chapters + 1):
                textbook_words = add_chapter_to_words(textbook_words, i)
        else:
            textbook_words = add_chapter_to_words(textbook_words, chapter)
    except Exception as e:
        print(f"Error loading textbook words: {e}")
        exit()

    return textbook_words

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

def load_player_stats(chapter: int) -> dict:
    player_stats = {}

    # Ensure the database and table exist
    create_table()

    # Load player statistics from the database
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if chapter == None:
                cursor.execute("SELECT * FROM player_stats")
            else:
                cursor.execute("SELECT * FROM player_stats WHERE chapter=?", (chapter))
            rows = cursor.fetchall()
            for row in rows:
                player_stats[row[0]] = {
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

def load_word_data(chapter: int = 0) -> dict:
    textbook_words = load_textbook_words(chapter)

    word_data = {}
    player_stats = load_player_stats(chapter)

    for spanish, english in textbook_words.items():
        found = False
        for stats in player_stats.values():
            if stats["chapter"] == 1 and stats["english"] == english and stats["spanish"] == spanish:
                found = True
                break
        if not found:
            create_player_stats_entry(1, english, spanish)
            any_new_words = True

    
    return word_data

def save_game_data(chapter: str = 0, num_correct: int = 0, num_wrong: int = 0, time_limit: int = 60, correct: list = [], incorrect: list = []) -> None:
    try:
        save_file = f"{datetime.now().strftime('%Y-%m-%d')}.txt"
        with open(save_file, "a", encoding="utf-8") as f:
            f.write(f"{time_limit=}, {chapter=}, {num_correct=}, {num_wrong=}, {incorrect=}, {correct=}\n")
       
    except Exception as e:
        print(f"Error saving data: {e}")