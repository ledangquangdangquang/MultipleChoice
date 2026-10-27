import html
import io
import json
import os
import re
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(ROOT, "web", "index.html")
PORT = 8000
MAX_UPLOAD = 10 * 1024 * 1024  # .docx files with images get big


def list_files():
    return sorted(f for f in os.listdir(ROOT) if f.endswith(".txt"))


# "1. ...", "1) ...", "Câu 1: ...", "Question 1 ..."
Q_RE = re.compile(r"^(?:(?:câu|cau|question)\s*(\d+)\s*[.:)\-]?|(\d+)\s*[.:)])\s*(.*)$", re.I)
# "A. ...", "a) ...", "(A) ...", "*B. ..." (star marks the correct option)
OPT_MARK = re.compile(r"(\*?)\(?([A-Ea-e])\s*[.):]\s+")
ANS_PREFIX = re.compile(r"^(?:đáp án(?: đúng)?|dap an(?: dung)?|answer|ans)\s*[:.\-]?\s*\(?([A-E])\b", re.I)
ANS_BARE = re.compile(r"^\(?([A-Ea-e])\)?\.?$")
# answer key at the end of the file: a "Đáp án:" / "Answers:" header, then lines like "1-B, 2.A 3) c"
KEY_HEAD = re.compile(r"^(?:bảng đáp án|bang dap an|đáp án|dap an|answers?|answer key)\s*:?\s*(.*)$", re.I)
KEY_LINE = re.compile(r"(?:\s*\d+\s*[-.:)]?\s*[A-Ea-e]\b[\s,;.|]*)+")
KEY_PAIR = re.compile(r"(\d+)\s*[-.:)]?\s*([A-Ea-e])\b")


def split_options(line):
    """Split "A. x B. y C. z" into [(star, letter, text)], only on markers that continue the A, B, C... run."""
    # shortcut: option text like "A. Vitamin B. 12" splits at "B. "; upgrade if real files hit it
    marks = [m for m in OPT_MARK.finditer(line) if m.start() == 0 or line[m.start() - 1].isspace()]
    keep = marks[:1]
    for m in marks[1:]:
        if m[2].upper() == chr(ord(keep[-1][2].upper()) + 1):
            keep.append(m)
    return [(m[1], m[2].upper(), line[m.end():nxt.start() if nxt else None].strip())
            for m, nxt in zip(keep, keep[1:] + [None])]


# Superset of legacy/main.py's format (can't import it: msvcrt is Windows-only).
# Returns (questions normalized to Questions.txt shape, number of questions skipped).
def parse_questions(text):
    raw, key, in_key, cur = [], {}, False, None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if in_key and KEY_LINE.fullmatch(line):
            key.update((n, a.upper()) for n, a in KEY_PAIR.findall(line))
            cur = None
            continue
        in_key = False

        if cur and (m := ANS_PREFIX.match(line) or ANS_BARE.match(line)):
            cur["answer"] = m[1].upper()
        elif (m := KEY_HEAD.match(line)) and (not m[1] or KEY_LINE.fullmatch(m[1])):
            in_key = True
            # an empty "Đáp án:" keeps cur, so "Đáp án:" followed by "B" on the next line still works
            if m[1]:
                cur = None
            key.update((n, a.upper()) for n, a in KEY_PAIR.findall(m[1]))
        elif m := Q_RE.match(line):
            cur = {"n": m[1] or m[2], "text": m[3].strip(), "options": [], "answer": None}
            raw.append(cur)
        elif cur and OPT_MARK.match(line):
            for star, letter, body in split_options(line):
                if body.endswith("*"):
                    star, body = "*", body[:-1].strip()
                cur["options"].append(f"{letter}. {body}")
                if star:
                    cur["answer"] = letter
        elif cur:  # wrapped line: continues the last option, or the question if no options yet
            if cur["options"]:
                cur["options"][-1] += " " + line
            else:
                cur["text"] = f'{cur["text"]} {line}'.strip()

    questions = []
    for q in raw:
        answer = q["answer"] or key.get(q["n"])
        if answer in [o[0] for o in q["options"]] and len(q["options"]) >= 2:
            questions.append({"question": f'{q["n"]}. {q["text"]}', "options": q["options"], "answer": answer})
    return questions, len(raw) - len(questions)


def docx_text(data):
    """Paragraph text of a .docx, one paragraph per line. Word's automatic list numbering is not included."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        info = z.getinfo("word/document.xml")
        if info.file_size > 20 * MAX_UPLOAD:  # zip bomb guard
            raise ValueError("Document is too large")
        xml = z.read(info).decode("utf-8")
    # turn line breaks and tabs into text runs so they survive the <w:t> extraction below
    xml = re.sub(r"<w:(?:br|cr)\b[^>]*/>", "<w:t>\n</w:t>", xml)
    xml = re.sub(r"<w:tab/>", "<w:t>\t</w:t>", xml)
    return "\n".join(html.unescape("".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", p)))
                     for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S))


class Handler(BaseHTTPRequestHandler):
    def send(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, data):
        self.send(200, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        path = unquote(self.path.split("?")[0])
        if path == "/":
            with open(INDEX, "rb") as f:
                self.send(200, "text/html; charset=utf-8", f.read())
        elif path == "/api/files":
            self.send_json(list_files())
        # whitelist check against the listing blocks path traversal
        elif path.startswith("/api/files/") and path[len("/api/files/"):] in list_files():
            with open(os.path.join(ROOT, path[len("/api/files/"):]), encoding="utf-8") as f:
                self.send_json(parse_questions(f.read())[0])
        else:
            self.send(404, "text/plain", b"Not found")

    # Uploaded file is parsed and returned, not saved to disk
    def do_POST(self):
        if self.path != "/api/parse":
            return self.send(404, "text/plain", b"Not found")
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= MAX_UPLOAD:
            return self.send(413, "text/plain", b"File is empty or too large")
        data = self.rfile.read(length)
        try:
            if data.startswith(b"PK\x03\x04"):  # zip container: .docx
                text = docx_text(data)
            else:
                # utf-8-sig: Notepad files may start with a BOM that hides the first question number
                text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return self.send(400, "text/plain", b"Use a UTF-8 .txt file or a .docx file (old .doc is not supported)")
        except (zipfile.BadZipFile, KeyError, ValueError):
            return self.send(400, "text/plain", b"Could not read this .docx file")
        questions, skipped = parse_questions(text)
        self.send_json({"questions": questions, "skipped": skipped})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Running at {url}  (Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
