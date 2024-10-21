import os
import random

def read_questions_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    questions = []
    current_question = {}

    for line in lines:
        line = line.strip()
        
        # Bỏ qua dòng trống
        if not line:
            continue
        
        if line[0].isdigit():  # Nhận diện câu hỏi bắt đầu bằng số
            if "question" in current_question and "answer" in current_question:
                questions.append(current_question)
            current_question = {"question": line}
        elif line.startswith(("A.", "B.", "C.", "D.", "E.")):
            if "options" not in current_question:
                current_question["options"] = []
            current_question["options"].append(line)
        elif line.isalpha() and len(line) == 1:  # Đáp án đơn lẻ
            current_question["answer"] = line

    if "question" in current_question and "answer" in current_question:
        questions.append(current_question)

    return questions

def quiz_user(questions):
    correct = 0

    for question in questions:
        # Clear màn hình trước khi hiện câu hỏi
        clear_screen()

        print(question["question"])
        for option in question["options"]:
            print(option)
        
        # Lấy đáp án từ người dùng và kiểm tra tính hợp lệ
        user_answer = ""
        while user_answer not in ["A", "B", "C", "D", "E"]:
            user_answer = input("\nNhập đáp án của bạn (A, B, C, D, E): ").strip().upper()
            if user_answer not in ["A", "B", "C", "D", "E"]:
                print("Đáp án không hợp lệ, vui lòng nhập lại.")
        
        # Kiểm tra kết quả
        if user_answer == question["answer"]:
            print("Chính xác!")
            correct += 1
        else:
            print(f"Sai! Đáp án đúng là: {question['answer']}")
        
        # Đợi một chút trước khi chuyển câu hỏi
        input("\nNhấn Enter để tiếp tục...")

    clear_screen()
    print(f"Bạn đã trả lời đúng {correct}/{len(questions)} câu hỏi.")
    print(f"Powered by ledangquangdangquang.")

def clear_screen():
    # Clear màn hình
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    filename = "questions.txt"
    questions = read_questions_from_file(filename)

    # Hỏi người dùng có muốn random câu hỏi không
    shuffle_choice = input("Bạn có muốn random câu hỏi không? (y/n): ").strip().lower()
    if shuffle_choice == 'y':
        random.shuffle(questions)

    quiz_user(questions)

if __name__ == "__main__":
    main()
