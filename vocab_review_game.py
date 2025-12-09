import argparse
import time
import random
from player_stats import load_word_data, save_game_data, update_player_stats_entry

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser("Spanish Vocab Review Game")
    parser.add_argument("-c", "--chapter", metavar="", help="Which chapter to practice", type=int, default=0)
    parser.add_argument("-u", "--unlimited", action="store_true", help="Endless mode (no time limit)", default=False)
    parser.add_argument("-t", "--time_limit", metavar="", help="Amount of time per game (in seconds)", type=int, default=60)
    parser.add_argument("-e", "--english", action="store_true", help="Quiz reading spanish words instead of writing them", default=False)
    parser.add_argument("-w", "--weights", action="store_true", help="Show weights for each word", default=False)
    args = parser.parse_args()
    return args

def next_question(history_correct: list, history_incorrect: list, show_weights: bool) -> int:
    num_words = len(history_correct)
    weights = []
    for i in range(num_words):
        weight = (1 + history_incorrect[i]) / (1 + history_correct[i])
        weights.append(weight)
    selected_index = random.choices(range(num_words), weights=weights, k=1)[0]
    if show_weights:
        print(f"Weights: {weights}")
    return selected_index

def game(word_data: dict, time_limit: int = 60, unlimited: bool = False, english_mode: bool = False, show_weights: bool = False) -> dict:
    # Prepare word lists
    spanish = []
    english = []
    history_correct = []
    history_incorrect = []
    chapter_of_words = []
    for chapter in word_data.values():
        for stat in chapter.values():
            spanish.append(stat["spanish"])
            english.append(stat["english"])
            history_correct.append(stat["num_correct"])
            history_incorrect.append(stat["num_wrong"])
            chapter_of_words.append(stat["chapter"])

    # Prepare per game stats
    initial_time = time.time()
    num_correct = 0
    num_wrong = 0
    correct = []
    incorrect = []
    if unlimited:
        time_limit = 3600  # 1 hour for unlimited mode

    # Start game loop
    while ((time.time() - initial_time) < time_limit):
        index = next_question(history_correct, history_incorrect, show_weights)
        if english_mode:
            print(f"What is the English translation of '{spanish[index]}'?")
            answer = input()
            correct_answer = english[index]
        else:
            print(f"What is the Spanish translation of '{english[index]}'?")
            answer = input()
            correct_answer = spanish[index]

        if answer.lower() == "exit" or answer.lower() == "q" or answer.lower() == "quit":
            break
        elif answer.lower() == correct_answer.lower():
            print("Correct!\n")
            num_correct += 1
            correct.append(correct_answer)
            update_player_stats_entry(chapter_of_words[index], english[index], spanish[index], True)
            history_correct[index] += 1
        else:
            print(f"Incorrect. The correct answer is '{correct_answer}'.\n")
            incorrect.append(correct_answer)
            num_wrong += 1
            update_player_stats_entry(chapter_of_words[index], english[index], spanish[index], False)
            history_incorrect[index] += 1

    # Game over message and stats
    print("\nTime's up!")
    print(f"You got {num_correct} correct and {num_wrong} wrong in {time_limit} seconds.")
    print("Your words you got wrong: ")
    for word in incorrect:
        print(word)
    
    # Determines chapter for saving
    if sum(chapter_of_words)/len(chapter_of_words) % 1 == 0:
        chapter = chapter_of_words[0]
    else:
        chapter = 0
    save_game_data(chapter, num_correct, num_wrong, time_limit, correct, incorrect)

def main():
    # Get settings from command line arguments
    args = parse_arguments()

    # Game loops for multiple rounds if needed
    while True:
        # Load words (english, spanish, num_correct, num_wrong) from player data and textbook files
        word_data = load_word_data(args.chapter)

        # Starts game
        game(word_data, time_limit=args.time_limit, unlimited=args.unlimited, english_mode=args.english, show_weights=args.weights)

        # Replay prompt
        print("Do you want to play again? (y/n)")
        answer = input()
        if answer.lower() != "y":
            break

if __name__ == "__main__":
    main()