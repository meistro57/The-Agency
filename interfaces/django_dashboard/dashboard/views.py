from django.shortcuts import render
from django.http import HttpResponse
import threading
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from main import run_agency

LOG_FILE = os.path.join("logs", "agency.log")
WATCH_DIR = "tasks"

os.makedirs(WATCH_DIR, exist_ok=True)


def index(request):
    logs = _tail_log(LOG_FILE)
    return render(request, "index.html", {"logs": logs})


def run_prompt(request):
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        if prompt:
            threading.Thread(target=run_agency, args=(prompt,), daemon=True).start()
    return HttpResponse("Started", status=202)


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


# start watcher on import
FileWatcher(WATCH_DIR).start()

# Simple node editor using Django instead of Flask
NODES: dict[str, str] = {}


def node_editor(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        text = request.POST.get("text", "")
        if name:
            NODES[name] = text
    return render(request, "nodes.html", {"nodes": NODES})
