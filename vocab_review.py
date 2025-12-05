import argparse
import time
import random

MAX_CHAPTERS = 1

def load_questions(num_questions: int = 1) -> dict:
    words = {}

    # Load questions from select files
    try:
        if num_questions > MAX_CHAPTERS:
            raise ValueError(f"num_questions cannot exceed {MAX_CHAPTERS}")
        
        for i in range(1, num_questions+1):
            with open(f"vocab/{i}.txt", "r", encoding="utf-8") as file:
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
        else:
            print(f"Incorrect. The correct answer is '{spanish[index]}'.\n")
            incorrect.append(spanish[index])
            num_wrong += 1

    print("\nTime's up!")
    print(f"You got {num_correct} correct and {num_wrong} wrong in {time_limit} seconds.")
    print("Your words you got wrong: ")
    for word in incorrect:
        print(word)

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