import sqlite3
import argparse
import os
import matplotlib.pyplot as plt

DB_PATH = "kenta_vocab_stats.db"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTBOOK_VOCAB_PATH = os.path.join(ROOT_DIR, "textbook_vocab")

# Handle case where directory might not exist yet
if os.path.exists(TEXTBOOK_VOCAB_PATH):
    MAX_CHAPTERS = sum(1 for p in os.listdir(TEXTBOOK_VOCAB_PATH) if p.endswith(".txt"))
else:
    MAX_CHAPTERS = 0

# Changed 'words' to a list to prevent index collisions between chapters
def analyze_vocab_stats(chapter: int = 0, words: list = None):
    if words is None:
        words = []
        
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT english, spanish, num_correct, num_wrong
                FROM player_stats
                WHERE chapter = ?
            """, (chapter,))
            rows = cursor.fetchall()
            
            # Append new dictionaries to the list instead of using integer keys
            for row in rows:
                entry = {
                    'english': row[0],
                    'spanish': row[1],
                    'num_correct': row[2],
                    'num_wrong': row[3]
                }
                words.append(entry)
            return words
    except Exception as e:
        print(f"Error reading player stats: {e}")
        exit()

def display_barplot(words: list):
    # 1. Define the Batch Size
    BATCH_SIZE = 50
    total_words = len(words)
    
    if total_words == 0:
        print("No vocabulary data found to plot.")
        return

    # 2. Loop through the list in steps of BATCH_SIZE
    # range(start, stop, step) generates 0, 20, 40...
    for i in range(0, total_words, BATCH_SIZE):
        
        # 3. Create the Slice (The Subset)
        # This grabs items from index 'i' up to 'i + 20'
        batch = words[i : i + BATCH_SIZE]
        
        # --- Plotting Logic (Applied to the Batch) ---
        categories = [f"{w['spanish']}" for w in batch]
        y_values_1 = [w['num_correct'] for w in batch]
        y_values_2 = [w['num_wrong'] for w in batch]

        x_indices = range(len(categories))
        width = 0.35

        fig, ax = plt.subplots(figsize=(15, 6))

        # List comprehensions for bar positioning
        rects1 = ax.bar([x - width/2 for x in x_indices], y_values_1, width, label='Correct', color='#4e79a7')
        rects2 = ax.bar([x + width/2 for x in x_indices], y_values_2, width, label='Incorrect', color='#f28e2b')

        ax.set_ylabel('Counts')
        
        # Dynamic Title to show which batch we are viewing
        start_num = i + 1
        end_num = min(i + BATCH_SIZE, total_words)
        ax.set_title(f'Vocabulary Performance: Words {start_num}-{end_num}')
        
        ax.set_xticks(x_indices)
        ax.set_xticklabels(categories)
        plt.xticks(rotation=45, ha='right')

        ax.legend()
        plt.tight_layout()
        
        # Blocks execution until the window is closed
        print(f"Displaying plot for words {start_num} to {end_num}. Close window to see next batch...")

        mngr = plt.get_current_fig_manager()
        mngr.window.wm_geometry("+12+25")
        plt.show()

if __name__ == "__main__":
    # Initialize as list
    words_data = []

    parser = argparse.ArgumentParser(description="Analyze vocabulary statistics.")
    parser.add_argument("-c", "--chapter", type=int, default=0, help="Chapter number to analyze")
    args = parser.parse_args()

    if args.chapter < 0:
        print("Chapter number must be 0 or greater.")
        exit()
    elif args.chapter == 0:
        for chap in range(1, MAX_CHAPTERS + 1):
            words_data = analyze_vocab_stats(chap, words_data)
    else:
        words_data = analyze_vocab_stats(args.chapter, words_data)
    
    display_barplot(words_data)