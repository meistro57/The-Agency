"""Minimal ComfyUI-like node editor placeholder."""
from flask import Flask, request, render_template_string

app = Flask(__name__)
NODES: dict[str, str] = {}

TEMPLATE = """
<!doctype html>
<title>Node Editor</title>
<h1>ComfyUI Node Editor</h1>
<form method="post">
  Name: <input name="name" />
  Text: <input name="text" />
  <input type="submit" />
</form>
<ul>
{% for n, t in nodes.items() %}<li><b>{{n}}</b>: {{t}}</li>{% endfor %}
</ul>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        text = request.form.get("text", "")
        if name:
            NODES[name] = text
    return render_template_string(TEMPLATE, nodes=NODES)


if __name__ == "__main__":
    app.run(port=5050)
