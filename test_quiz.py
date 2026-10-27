from quiz import parse_questions

# original Questions.txt format; question 3 has no answer and is skipped
qs, skipped = parse_questions("1. Q one\nA. x\nB. y\nB\n\n2. Q two\nA. x\nB. y\nC. z\nA\n3. no answer\nA. x\n")
assert len(qs) == 2 and skipped == 1, (qs, skipped)
assert qs[0] == {"question": "1. Q one", "options": ["A. x", "B. y"], "answer": "B"}
assert qs[1]["answer"] == "A" and len(qs[1]["options"]) == 3

# "Câu" prefix, lowercase a), wrapped question line, "Đáp án:" line
qs, _ = parse_questions("Câu 1: Thủ đô của\nViệt Nam là?\na) Huế\nb) Hà Nội\nĐáp án: b\n")
assert qs == [{"question": "1. Thủ đô của Việt Nam là?", "options": ["A. Huế", "B. Hà Nội"], "answer": "B"}], qs

# inline options, correct option marked with a star
qs, _ = parse_questions("Câu 2. Chọn đúng\nA. Sắt   *B. Kẽm   C. Đồng\n")
assert qs == [{"question": "2. Chọn đúng", "options": ["A. Sắt", "B. Kẽm", "C. Đồng"], "answer": "B"}], qs

# "(A)" markers, trailing star, answer must be one of the options
qs, skipped = parse_questions("3) Q\n(A) x\n(B) y *\n4. Q\nA. x\nB. y\nĐáp án đúng: D\n")
assert qs == [{"question": "3. Q", "options": ["A. x", "B. y"], "answer": "B"}] and skipped == 1, (qs, skipped)

# answer key at the end of the file; "Đáp án:" on its own line followed by the letter
qs, skipped = parse_questions("1. Q\nA. x\nB. y\n2. Q\nA. x\nB. y\n3. Q\nA. x\nB. y\nĐáp án:\nB\n"
                              "BẢNG ĐÁP ÁN\n1-B, 2.A\n")
assert [q["answer"] for q in qs] == ["B", "A", "B"] and skipped == 0, (qs, skipped)
qs, _ = parse_questions("1. Q\nA. x\nB. y\nAnswers: 1-B\n")
assert qs[0]["answer"] == "B", qs

# .docx: paragraphs become lines, <w:br/> becomes a newline, XML entities are decoded
import io, zipfile
from quiz import docx_text
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    z.writestr("word/document.xml", '<w:document><w:body>'
               '<w:p><w:pPr/><w:r><w:t>Câu 1: A &amp; B?</w:t></w:r></w:p>'
               '<w:p><w:r><w:t xml:space="preserve">A. x</w:t><w:br/><w:t>B. y</w:t></w:r></w:p>'
               '<w:p><w:r><w:t>Đáp án: B</w:t></w:r></w:p></w:body></w:document>')
text = docx_text(buf.getvalue())
assert text == "Câu 1: A & B?\nA. x\nB. y\nĐáp án: B", repr(text)
assert parse_questions(text)[0][0]["answer"] == "B"

# the bundled sample files still parse
for name in ("Questions.txt", "Questions1.txt", "Questions2.txt"):
    with open(name, encoding="utf-8") as f:
        qs, skipped = parse_questions(f.read())
    assert qs and skipped == 0, name
print("ok")
