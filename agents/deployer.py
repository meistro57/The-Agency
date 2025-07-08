# deployer.py

import os
import subprocess
import logging
from agents.agent_base import BaseAgent
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DeployerAgent(BaseAgent):
    """
    Builds and runs the generated project using a container tool.
    """

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Deployment Manager"
        self.description = "Builds container image and launches container"
        self.container_tool = getattr(config, "CONTAINER_TOOL", "docker")

    def generate_plan(self, user_prompt: str):
        """Not applicable for deployer agent (returns empty)."""
        return {}

    def deploy_project(self, file_paths: List[str]) -> None:
        """
        Deploys the project via Docker: creates Dockerfile, builds, and runs the image.

        Args:
            file_paths (List[str]): List of generated project files.
        """
        logger.info("🚀 Deploying project...")

        self._generate_dockerfile(file_paths)
        self._build_docker_image()
        self._run_container()

    def _generate_dockerfile(self, file_paths: List[str]) -> None:
        """
        Creates a Dockerfile using the primary Python file as entrypoint.

        Args:
            file_paths (List[str]): Generated file paths to scan.
        """
        if not file_paths:
            logger.error("❌ No generated files provided for Dockerfile creation.")
            return

        python_files = [f for f in file_paths if f.endswith(".py")]
        node_files = [f for f in file_paths if f.endswith(".js") or f.endswith(".ts")]

        if python_files:
            entry = "main.py" if "main.py" in python_files else python_files[0]
            dockerfile = f"""
            # Auto-generated Dockerfile
            FROM python:3.10-slim
            WORKDIR /app
            COPY . .
            RUN pip install -r requirements.txt || true
            CMD [\"python\", \"{os.path.basename(entry)}\"]
            """
        elif node_files:
            entry = "server.js" if "server.js" in node_files else node_files[0]
            dockerfile = f"""
            # Auto-generated Dockerfile
            FROM node:20-alpine
            WORKDIR /app
            COPY . .
            RUN npm install || true
            CMD [\"node\", \"{os.path.basename(entry)}\"]
            """
        else:
            logger.error("❌ No valid application entrypoint found for Dockerfile.")
            return

        try:
            docker_path = os.path.join(self.config.PROJECTS_DIR, "Dockerfile")
            with open(docker_path, "w") as f:
                f.write(dockerfile.strip())
            logger.info("📦 Dockerfile generated.")
        except Exception as e:
            logger.error(f"❌ Failed to write Dockerfile: {e}")

    def _build_docker_image(self, image_name: str = "the-agency-app") -> None:
        """
        Builds the Docker image.

        Args:
            image_name (str): Docker image name.
        """
        logger.info(f"🔧 Building {self.container_tool} image '{image_name}'...")

        try:
            subprocess.run(
                [self.container_tool, "build", "-t", image_name, self.config.PROJECTS_DIR],
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {self.container_tool} build failed: {e}")
            logger.info(f"💡 Ensure {self.container_tool} is installed, running, and your Dockerfile is valid.")
        except FileNotFoundError:
            logger.error(f"❌ {self.container_tool} not found. Is it installed and in your PATH?")

    def setup_github_workflow(self) -> None:
        """Create a minimal GitHub Actions workflow for CI tests."""
        workflows = os.path.join(self.config.PROJECTS_DIR, ".github", "workflows")
        os.makedirs(workflows, exist_ok=True)
        ci_path = os.path.join(workflows, "ci.yml")
        workflow = """
        name: CI
        on: [push]
        jobs:
          build:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v3
              - uses: actions/setup-python@v4
                with:
                  python-version: '3.11'
              - run: pip install -r requirements.txt
              - run: pytest -q
        """
        try:
            with open(ci_path, "w", encoding="utf-8") as f:
                f.write(workflow.strip())
            logger.info("📝 GitHub Actions workflow created.")
        except Exception as e:
            logger.error(f"❌ Failed to write workflow: {e}")

    def auto_push_to_github(self, repo_url: str) -> None:
        """Push the generated project to a GitHub repository."""
        logger.info(f"📤 Pushing project to {repo_url}")
        proj = self.config.PROJECTS_DIR
        cmds = [
            ["git", "init"],
            ["git", "add", "-A"],
            ["git", "commit", "-m", "auto deploy"],
            ["git", "remote", "add", "origin", repo_url],
            ["git", "push", "-u", "origin", "main"]
        ]
        for cmd in cmds:
            try:
                subprocess.run(cmd, cwd=proj, check=True)
            except Exception as e:
                logger.error(f"❌ Git command failed: {e}")
                break

    def _run_container(self, image_name: str = "the-agency-app", port: str = "8090") -> None:
        """
        Runs the Docker container.

        Args:
            image_name (str): Docker image name to run.
            port (str): Host:container port mapping.
        """
        logger.info(f"🐳 Running container '{image_name}' on port {port} using {self.container_tool}...")

        try:
            subprocess.run(
                [self.container_tool, "run", "-d", "--rm", "-p", f"{port}:{port}", image_name],
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to run container: {e}")
            logger.info(f"💡 Check if port {port} is free or if the image '{image_name}' exists.")
        except FileNotFoundError:
            logger.error(f"❌ {self.container_tool} not found. Is it installed and in your PATH?")
