import argparse
import time
import random
from player_statistics.player_stats import load_word_data, save_game_data, update_player_stats_entry

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser("Spanish Vocab Review Game")
    parser.add_argument("-c", "--chapter", metavar="", help="Which chapter to practice", type=int, default=0)
    parser.add_argument("-u", "--unlimited", action="store_true", help="Endless mode (no time limit)", default=False)
    parser.add_argument("-t", "--time_limit", metavar="", help="Amount of time per game (in seconds)", type=int, default=60)
    parser.add_argument("-e", "--english", action="store_true", help="Quiz reading spanish words instead of writing them", default=False)
    args = parser.parse_args()
    return args

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

def refresh_player_stats(words: dict, player_stats: dict, chapter: int) -> None:
    any_new_words = False
    for spanish, english in words.items():
        found = False
        for stats in player_stats.values():
            if stats["chapter"] == 1 and stats["english"] == english and stats["spanish"] == spanish:
                found = True
                break
        if not found:
            create_player_stats_entry(1, english, spanish)
            any_new_words = True

    if any_new_words:
        player_stats = load_player_stats(chapter)

    return player_stats

def game(player_stats: dict, time_limit: int = 60, unlimited: bool = False, english_mode: bool = False) -> dict:
    # Prepare word lists
    chapter = player_stats[1]["chapter"]
    spanish = []
    english = []
    for stat in player_stats.values():
        spanish.append(stat["spanish"])
        english.append(stat["english"])
        if stat["chapter"] != chapter:
            chapter = "all"
        
    num_words = len(spanish)

    # Start the game
    initial_time = time.time()
    num_correct = 0
    num_wrong = 0
    correct = []
    incorrect = []
    if unlimited:
        time_limit = 3600  # 1 hour for unlimited mode

    while ((time.time() - initial_time) < time_limit):
        index = random.randint(0, num_words - 1)
        if english_mode:
            print(f"What is the English translation of '{spanish[index]}'?")
            answer = input()
            correct_answer = english[index]
        else:
            print(f"What is the Spanish translation of '{english[index]}'?")
            answer = input()
            correct_answer = spanish[index]

        if answer.lower() == "exit" or answer.lower() == "q":
            break
        elif answer == correct_answer:
            print("Correct!\n")
            num_correct += 1
            correct.append(correct_answer)
            update_player_stats_entry(player_stats[index]["chapter"], english[index], spanish[index], True)
        else:
            print(f"Incorrect. The correct answer is '{correct_answer}'.\n")
            incorrect.append(correct_answer)
            num_wrong += 1
            update_player_stats_entry(player_stats[index]["chapter"], english[index], spanish[index], False)

    # Game over
    print("\nTime's up!")
    print(f"You got {num_correct} correct and {num_wrong} wrong in {time_limit} seconds.")
    print("Your words you got wrong: ")
    for word in incorrect:
        print(word)
    save_game_data(chapter, num_correct, num_wrong, time_limit, correct, incorrect)

    return player_stats

def main():
    # Get settings from command line arguments
    args = parse_arguments()

    # Load words (english, spanish, num_correct, num_wrong) from player data and textbook files
    word_data = load_word_data(args.chapter)

    # Game loops for multiple rounds if needed
    while True:
        # Starts game and stores results
        player_stats = game(word_data, time_limit=args.time_limit, unlimited=args.unlimited, english_mode=args.english)

        # Replay prompt
        print("Do you want to play again? (y/n)")
        answer = input()
        if answer.lower() != "y":
            break

if __name__ == "__main__":
    main()