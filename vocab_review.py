import argparse
import time
import random
from datetime import datetime

MAX_CHAPTERS = 1

def save_data(num_correct: int = 0, num_wrong: int = 0, time_limit: int = 60, correct: list = [], incorrect: list = []):
    with open(f"save_data/{datetime.now().strftime('%Y-%m-%d')}.txt", "a", encoding="utf-8") as f:
        f.write(f"{num_correct=}, {num_wrong=}, {time_limit=}, {incorrect=}, {correct=}\n")
    return

def load_questions(num_questions: int = 1) -> dict:
    words = {}

    # Load questions from select files
    try:
        if num_questions > MAX_CHAPTERS:
            raise ValueError(f"num_questions cannot exceed {MAX_CHAPTERS}")
        
        for i in range(1, num_questions+1):
            with open(f"textbook_vocab/{i}.txt", "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        spanish, english = line.split("\\")
                        words[spanish] = english
    except ValueError as e:
        print(e)
        exit()
    except FileNotFoundError:
        print("One or more vocabulary files are missing.")
        exit()

    return words

def game(spanish: list, english: list, num_words: int, time_limit: int = 60, unlimited: bool = False):
    # Welcome message
    print("Welcome to the Spanish Noun Review Game!")
    print("This game will help you practice Spanish nouns.")
    print("Type 'exit' at any time to quit the game.")
    print("Let's begin!\n")

    # Initialize game variables
    initial_time = time.time()
    num_correct = 0
    num_wrong = 0
    correct = []
    incorrect = []
    if unlimited:
        time_limit = 3600  # 1 hour for unlimited mode

    # Game loop
    while ((time.time() - initial_time) < time_limit):
        index = random.randint(0, num_words - 1)
        print(f"What is the Spanish translation of '{english[index]}'?")
        answer = input()

        if answer.lower() == "exit" or answer.lower() == "q":
            break
        elif answer == spanish[index]:
            print("Correct!\n")
            num_correct += 1
            correct.append(spanish[index])
        else:
            print(f"Incorrect. The correct answer is '{spanish[index]}'.\n")
            incorrect.append(spanish[index])
            num_wrong += 1

    print("\nTime's up!")
    print(f"You got {num_correct} correct and {num_wrong} wrong in {time_limit} seconds.")
    print("Your words you got wrong: ")
    for word in incorrect:
        print(word)
    save_data(num_correct, num_wrong, time_limit, correct, incorrect)

def main():
    # Take in command-line arguments
    parser = argparse.ArgumentParser("Spanish Noun Review Game")
    parser.add_argument("-c", "--chapter", metavar="", help="Number of chapters to include", type=int, default=0)
    args = parser.parse_args()

    # Load questions
    words = load_questions(args.chapter)
    spanish = list(words.keys())
    english = list(words.values())
    num_words = len(spanish)

    # Start the game
    game(spanish, english, num_words, time_limit=60)

if __name__ == "__main__":
    main()