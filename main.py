import os
import random
import msvcrt

directory = "."  # Đường dẫn đến thư mục, "." là thư mục hiện tại

# List of .txt file 
filenames = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".txt")]

def read_questions_from_file(filename):
    """Read questions from a file and return as a list of dictionaries"""
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    questions = []
    current_question = {}

    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Identify questions starting with a number
        if line[0].isdigit():  
            if "question" in current_question and "answer" in current_question:
                questions.append(current_question)
            current_question = {"question": line}
        elif line.startswith(("A.", "B.", "C.", "D.", "E.")):
            current_question.setdefault("options", []).append(line)
        elif line.isalpha() and len(line) == 1:  # Single letter answer
            current_question["answer"] = line

    # Add the last question if it's complete
    if "question" in current_question and "answer" in current_question:
        questions.append(current_question)

    return questions

def quiz_user(questions, is_retry=False):
    """Run a quiz for the user and save wrong answers for a retry"""
    correct = 0
    wrong_questions = []
    count = 1
    for question in questions:
        clear_screen()
        print(f"({count}/{len(questions)})\n {question["question"]}")
        for option in question["options"]:
            print(option)        
        mapping = {
            "1": "A",
            "2": "B",
            "3": "C",
            "4": "D",
            "5": "E"
        }


        valid_keys = ["A", "B", "C", "D", "E", "1", "2", "3", "4", "5"]
        user_answer = ""

        while user_answer not in valid_keys:
            print("\nInput your answer (A, B, C, D, E or 1-5): ", end="", flush=True)
            key = msvcrt.getch()

            # Nếu là phím đặc biệt (mũi tên, chức năng), đọc thêm 1 byte để bỏ qua
            if key in (b'\x00', b'\xe0'):
                msvcrt.getch()
                print("invalid key!!!")
                continue

            try:
                user_answer = key.decode('utf-8').strip().upper()
            except UnicodeDecodeError:
                continue  # Nếu không giải mã được, đợi người dùng nhập lại

            if user_answer not in valid_keys:
                print("invalid key!!!")

        # Kiểm tra kết quả 
        if (user_answer in ["A", "B", "C", "D", "E"] and user_answer == question["answer"]) or \
           (user_answer in ["1", "2", "3", "4", "5"] and mapping[user_answer] == question["answer"]):
            print(f"{user_answer}\nCorrect!")
            correct += 1
        else:
            print(f"{user_answer}\nIncorrect! The correct answer is: {question['answer']}")
            if not is_retry:  # Only add incorrect answers if it's not a retry
                wrong_questions.append(question)    
        count += 1
        # Đợi một chút trước khi chuyển câu hỏi
        input("\nPress Enter to continue...")

    clear_screen()
    print(f"You answered {correct}/{len(questions)} questions correctly.")
    print("© 2025 by ledangquangdangquang.")
    input("\nPress Enter to continue...")
    
    # If there are incorrect answers, allow a one-time retry
    if wrong_questions and not is_retry:
        print("\nNow you will retry the incorrect questions once.")
        input("Press Enter to continue...")
        quiz_user(wrong_questions, is_retry=True)  # Retry incorrect questions with is_retry=True


def clear_screen():
    """Clear the screen depending on the operating system"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Run the main program in an infinite loop"""
    while True:
        clear_screen()
        print("Choose a file you want to use: ")
        for i, filename in enumerate(filenames):
            print(f"{i + 1}. {os.path.basename(filename)}")
        print("0. EXIT")

        # Get user's file selection
        your_choice = input("Enter your choice: ").strip()
        if your_choice == "0":
            clear_screen()
            print("© 2025 by ledangquangdangquang.")
            break
        elif your_choice not in map(str, range(1, len(filenames) + 1)):
            print("Invalid choice, please try again.")
            input("Press Enter to continue...")
            continue

        clear_screen()
        chosen_file = filenames[int(your_choice) - 1]
        questions = read_questions_from_file(chosen_file)
        print("You are using the file:", os.path.basename(chosen_file))

        # Ask if the user wants to randomize questions
        shuffle_choice = input("Do you want to randomize the questions? (y/n): ").strip().lower()
        if shuffle_choice == 'y':
            random.shuffle(questions)

        quiz_user(questions)

if __name__ == "__main__":
    main() 
