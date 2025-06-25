import os
import random
import msvcrt
import time
import shutil
import textwrap

directory = "."

filenames = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".txt")]

BOX_WIDTH = 100  # cố định chiều rộng hộp

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_questions_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    questions = []
    current_question = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line[0].isdigit():  
            if "question" in current_question and "answer" in current_question:
                questions.append(current_question)
            current_question = {"question": line}
        elif line.startswith(("A.", "B.", "C.", "D.", "E.")):
            current_question.setdefault("options", []).append(line)
        elif line.isalpha() and len(line) == 1:
            current_question["answer"] = line

    if "question" in current_question and "answer" in current_question:
        questions.append(current_question)

    return questions

def wrap_lines(lines, width):
    wrapped = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, width=width))
    return wrapped

def display_box(lines):
    terminal_width, terminal_height = shutil.get_terminal_size()
    content_width = BOX_WIDTH - 4
    wrapped_lines = wrap_lines(lines, content_width)
    box_height = len(wrapped_lines) + 2

    top_padding = max(0, (terminal_height - box_height) // 2)
    print("\n" * top_padding, end="")

    left_padding = max(0, (terminal_width - BOX_WIDTH) // 2)
    pad = " " * left_padding

    print(pad + "┌" + "─" * (BOX_WIDTH - 2) + "┐")
    for line in wrapped_lines:
        print(pad + f"│ {line.ljust(content_width)} │")
    print(pad + "└" + "─" * (BOX_WIDTH - 2) + "┘")

    return left_padding

def display_centered_box(lines):
    terminal_width, terminal_height = shutil.get_terminal_size()
    content_width = BOX_WIDTH - 4
    wrapped_lines = wrap_lines(lines, content_width)
    wrapped_lines = [line.center(content_width) for line in wrapped_lines]
    box_height = len(wrapped_lines) + 2

    top_padding = max(0, (terminal_height - box_height) // 2)
    print("\n" * top_padding, end="")

    left_padding = max(0, (terminal_width - BOX_WIDTH) // 2)
    pad = " " * left_padding

    print(pad + "┌" + "─" * (BOX_WIDTH - 2) + "┐")
    for line in wrapped_lines:
        print(pad + f"│ {line} │")
    print(pad + "└" + "─" * (BOX_WIDTH - 2) + "┘")

    return left_padding

def quiz_user(questions, is_retry=False):
    correct = 0
    wrong_questions = []
    count = 1
    start = time.time()

    for question in questions:
        clear_screen()

        lines = [f"--- {count}/{len(questions)} ---".center(BOX_WIDTH - 4)]
        lines.append("─" * (BOX_WIDTH - 4))
        lines.extend(textwrap.wrap(question["question"], width=BOX_WIDTH - 4))
        lines.extend(question["options"])
        left_pad = display_box(lines)

        mapping = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E"}
        valid_keys = list(mapping.keys()) + list(mapping.values())
        user_answer = ""

        print("\n" + " " * left_pad + "Your answer (A–E or 1–5): ", end="", flush=True)
        while user_answer not in valid_keys:
            key = msvcrt.getch()
            if key in (b'\x00', b'\xe0'):
                msvcrt.getch()
                continue
            try:
                user_answer = key.decode('utf-8').strip().upper()
            except UnicodeDecodeError:
                continue

        print("\n")
        if (user_answer in mapping.values() and user_answer == question["answer"]) or \
           (user_answer in mapping and mapping[user_answer] == question["answer"]):
            print(" " * left_pad + f"{user_answer} - ✅ Correct!")
            correct += 1
        else:
            print(" " * left_pad + f"{user_answer} - ❌ Incorrect!")
            print(" " * left_pad + f"The correct answer is: {question['answer']}")
            if not is_retry:
                wrong_questions.append(question)

        count += 1
        print("\n" + " " * left_pad + "Press Enter to continue...", end="")
        input()

    clear_screen()
    end = time.time()
    elapsed = (end - start) / 60
    lines = [
        f"You answered {correct}/{len(questions)} questions correctly.",
        f"Completed in {elapsed:.2f} minutes.",
        "© 2025 by ledangquangdangquang.",
    ]
    display_centered_box(lines)
    print("\n" + " " * left_pad +  "Press Enter to continue...", end="")
    input()
    clear_screen()
    if wrong_questions and not is_retry:
        display_centered_box(["Retrying incorrect questions now..."])
        print("\n" + " " * left_pad +  "Press Enter to continue...", end="")  
        input()
        quiz_user(wrong_questions, is_retry=True)

def main():
    while True:
        clear_screen()
        box_lines = ["Choose a file to use:"]
        for i, filename in enumerate(filenames):
            box_lines.append(f"{i + 1}. {os.path.basename(filename)}")
        box_lines.append("0. EXIT")

        left_pad = display_box(box_lines)
        print("\n" + " " * left_pad + "Enter your choice: ", end="")
        your_choice = input().strip()

        if your_choice == "0":
            clear_screen()
            display_centered_box(["Goodbye!", "© 2025 by ledangquangdangquang."])
            break
        elif your_choice not in map(str, range(1, len(filenames) + 1)):
            clear_screen()
            display_centered_box(["Invalid choice!", "Press Enter to try again."])
            input()
            continue

        chosen_file = filenames[int(your_choice) - 1]
        questions = read_questions_from_file(chosen_file)

        clear_screen()
        combined_lines = [
            f"You are using: {os.path.basename(chosen_file)}",
            "",
            "Shuffle the questions?"
        ]
        left_pad = display_centered_box(combined_lines)
        print("\n" + " " * left_pad + "Your choice (y/n): ", end="")
        shuffle_choice = input().strip().lower()
        if shuffle_choice == 'y':
            random.shuffle(questions)

        quiz_user(questions)

if __name__ == "__main__":
    main()
