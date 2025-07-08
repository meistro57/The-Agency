The Agency is an open-source multi-agent system that autonomously generates, tests, and deploys software solutions.

### Multi-Agent Software Generation System

**Project Codename:** The Agency

**Objective:** Build an open-source, boundary-pushing AI agent system that can autonomously generate, test, and deploy complete software solutions across web, CLI, full-stack, and ML domains.

---

### Project Folder Structure
```
The-Agency/
├── config.py              # Global settings (models, keys, DB, etc.)
├── main.py                # Entry point: orchestrates The Agency
├── agents/                # Folder: all specialized agent modules
│   ├── __init__.py
│   ├── architect.py       # Breaks down the user request into a project plan
│   ├── coder.py           # Generates code based on architect plan
│   ├── tester.py          # Executes and evaluates tests
│   ├── reviewer.py        # Uses GPT-4 to review and give feedback
│   ├── fixer.py           # Uses test feedback to auto-repair code
│   ├── deployer.py        # Creates Docker/CI/CD and deploys
│   ├── memory.py          # SQLite-based memory and task recall
│   └── task_manager.py    # Maintains current task list and their status
├── tools/                 # Folder: shared utilities
│   ├── context_loader.py  # Retrieves relevant code snippets or docs
│   └── tools.py           # Misc helpers like run_python_code(), etc.
├── interfaces/            # Optional: user input & UX layers
│   ├── cli_interface.py   # For terminal input/output
│   ├── django_dashboard/  # Django-based dashboard and node editor
│   ├── node_editor.py     # Flask-based visual editor (legacy)
│   └── qt_interface.py    # Qt-based GUI
├── projects/              # Folder: auto-generated projects (default path)
                            # Each run creates a subfolder named after the prompt
├── logs/                  # Folder: runtime logs, test results
├── requirements.txt       # Python dependencies
└── README.md              # System overview and usage
```

### Phase 1 File Count: ~15 Core Files

- Modular, extendable, and plug-in friendly.
- Full control over which model (local or GPT-4) handles each task.

### README Preview
```
# 🧠 The Agency

The Agency is an autonomous AI system designed to write, test, debug, review, and deploy software solutions entirely on its own. Built for developers, makers, tinkerers, and the terminally curious, The Agency transforms prompts into production-ready code.

## 🚨 What Makes It Different?

The Agency combines multiple specialized AI agents:
- 🧱 **ArchitectAgent**: Breaks down your idea into structured files and tech stacks
- ✍️ **CoderAgent**: Writes working code using open-source models (Qwen, Codestral via Ollama)
- 🧪 **TesterAgent**: Executes the code, runs unit tests, captures logs
- 👁️ **ReviewerAgent**: Uses GPT-4 to provide high-quality QA feedback
- 🔧 **FixerAgent**: Repairs broken or low-quality code
- 🚀 **DeployerAgent**: Packages the project into a Docker container and runs it

### Agent Modules

| Module | Description |
| --- | --- |
| `main_agent.py` – **MainAgent** | Coordinates the entire workflow |
| `supervisor.py` – **SupervisorAgent** | Validates outputs for sanity |
| `architect.py` – **ArchitectAgent** | Breaks down user prompts into a structured software plan |
| `coder.py` – **CoderAgent** | Generates source code from the plan |
| `tester.py` – **TesterAgent** | Runs unit tests and captures logs |
| `reviewer.py` – **ReviewerAgent** | Provides GPT‑4 based code reviews |
| `fixer.py` – **FixerAgent** | Applies automated fixes based on test results |
| `deployer.py` – **DeployerAgent** | Builds Docker images and launches containers |
| `product_creator.py` – **ProductCreatorAgent** | Creates e-commerce listings |
| `rl_optimizer.py` – **RLOptimizerAgent** | Tunes agent performance via RL |
| `failsafe.py` – **FailsafeAgent** | Monitors runtime for critical errors |
| `self_learner.py` – **SelfLearnerAgent** | Continuously improves agent skills |
| `evolution_logger.py` – **EvolutionLogger** | Tracks system learning over time |
| `memory.py` – **MemoryManager** | Persists state using an optional SQLite backend |
| `task_manager.py` – **TaskManager** | Tracks outstanding and completed tasks |

All while using:
- 🧠 SQLite-based persistent memory
- 🗂️ A modular architecture for future agent extensions
- 🛡️ Open-source LLMs (via Ollama) for code generation with GPT-4 used for critical review.
  Agents default to these local models but can target OpenAI by setting `CODE_MODEL`.

## 🧰 Use Cases
- Generate full-stack web apps from a description
- Spin up FastAPI+React dashboards with auth
- Auto-patch broken scripts from test results
- Write & run ML pipelines
- Build deployment pipelines on autopilot
- Monitor output with a failsafe agent
- View progress via the Django dashboard
- Annotate planning blueprints for clarity

## 💽 Requirements
- Python 3.10+
- Docker (for deployment/testing)
- OpenAI API key (for GPT-4 review agent)
- Optional: Ollama running Qwen2 or Codestral models (the `setup.sh` script pulls a base model automatically)
- `python-dotenv` for loading `.env` files

## 🔌 Setup
```bash
git clone https://github.com/meistro57/The-Agency.git
cd The-Agency
./setup.sh    # optional: manually create .venv and pull a base model
./install_and_test_ollama.sh  # installs Ollama and verifies the Qwen model
./deploy.sh   # updates code, installs deps if needed, then launches The Agency
python tools/env_check.py     # verify Python and Docker
python tools/db_setup.py      # initialize SQLite database
```

## 🧠 Configuration
Edit `config.py` or use environment variables:
```bash
export GPT4_API_KEY=your-key
export OLLAMA_MODEL=qwen:latest
export CODE_MODEL=$OLLAMA_MODEL  # defaults to Ollama model
export SQLITE_PATH=the_agency.db
export MAX_PROJECT_DIR_SIZE_MB=100
```

### Using OpenAI
The system connects to Ollama by default. To run the CoderAgent with an OpenAI
model instead, set `CODE_MODEL` to a chat model like `gpt-4o`.

## 🧪 Run via Terminal
```bash
python interfaces/cli_interface.py
# or let the deploy script handle setup and launching (opens the dashboard)
./deploy.sh
```

## 🐳 Run with Docker Compose
This repository ships with a `docker-compose.yml` that runs The Agency. Build and start everything with:
```bash
docker compose up --build
```
The application container stores persistent state in a local SQLite database.

## 🧪 Workflow
1. Accepts prompt from user (chat or file)
2. Architect breaks into structured blueprint
3. Coder generates complete files
4. Tester runs everything
5. Reviewer (GPT-4) gives feedback
6. Fixer loops back and patches
7. If all checks pass, Deployer ships it in Docker

## 🔮 Future Features
- Web interface for drag-and-drop blueprints
- Agent marketplace (plug in your own agents)
- GitHub auto-push + CI/CD integration
- Plugin-based extension architecture (dynamic agent loading included)
- Fine-tuned retrieval systems and documentation integration
- AI-driven refactoring suggestions for legacy codebases
- CLI-based project management commands
- Optional containerization support with Podman
- Product creation pipeline for e-commerce
- Reinforcement learning optimizer
- ComfyUI-style node editor interface
- Real-time collaborative editing
- GitLab integration for CI/CD
- Automated performance benchmarking
- Cloud deployment templates for AWS, Azure, and GCP
- Voice command interface
- Slack bot notifications
- Agent training analytics dashboard
- Security scanning for generated code
- Built-in plugin store
- Visual diff viewer for code changes

## 🧠 Philosophy
"Tell it what you need and it will do the rest."

Built to replace the drudgework. Built to experiment faster. Built to make makers unstoppable.
```

Let the build commence. ☕

