from flask import Flask, request, render_template_string
import threading
import time
import os
import sys

# Ensure the project root is on the Python path when run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import run_agency

TEMPLATE = """
<!doctype html>
<title>The Agency Dashboard</title>
<h1>The Agency Dashboard</h1>
<form method="post" action="/run">
  <input name="prompt" style="width:300px" placeholder="Enter prompt"/>
  <input type="submit" value="Run" />
</form>
<h3>Upload Blueprint</h3>
<form id="up" action="/upload" method="post" enctype="multipart/form-data">
  <input type="file" name="file" />
  <input type="submit" value="Upload" />
</form>
<script>
document.addEventListener('dragover', e=>e.preventDefault());
document.addEventListener('drop', e=>{
  e.preventDefault();
  const file=e.dataTransfer.files[0];
  if(!file) return;
  const form=new FormData();
  form.append('file', file);
  fetch('/upload',{method:'POST',body:form});
});
</script>
<h2>Logs</h2>
<pre>{{logs}}</pre>
"""

app = Flask(__name__)

LOG_FILE = os.path.join("logs", "agency.log")
WATCH_DIR = "tasks"

os.makedirs(WATCH_DIR, exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    logs = _tail_log(LOG_FILE)
    return render_template_string(TEMPLATE, logs=logs)


@app.route("/run", methods=["POST"])
def run():
    prompt = request.form.get("prompt", "").strip()
    if prompt:
        threading.Thread(target=run_agency, args=(prompt,), daemon=True).start()
    return "Started", 202


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if file:
        content = file.read().decode("utf-8", errors="ignore").strip()
        if content:
            threading.Thread(target=run_agency, args=(content,), daemon=True).start()
    return "Uploaded", 202


def _tail_log(path, lines=20):
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        data = f.readlines()[-lines:]
    return "".join(data)


class FileWatcher:
    def __init__(self, directory):
        self.directory = directory
        self.seen = set()

    def start(self):
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            for fname in os.listdir(self.directory):
                path = os.path.join(self.directory, fname)
                if path not in self.seen:
                    self.seen.add(path)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            prompt = f.read().strip()
                        if prompt:
                            run_agency(prompt)
                    except Exception:
                        pass
            time.sleep(2)


if __name__ == "__main__":
    FileWatcher(WATCH_DIR).start()
    app.run(port=5000)
