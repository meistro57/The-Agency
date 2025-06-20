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
        if not file_paths or all(not f.endswith(".py") for f in file_paths):
            logger.error("❌ No valid Python files found for Dockerfile entry.")
            return

        entry = "main.py"
        if not any("main.py" in f for f in file_paths):
            entry = next((f for f in file_paths if f.endswith(".py")), "app.py")

        dockerfile = f"""
        # Auto-generated Dockerfile
        FROM python:3.10-slim
        WORKDIR /app
        COPY . .
        RUN pip install -r requirements.txt || true
        CMD ["python", "{entry}"]
        """

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

    def _run_container(self, image_name: str = "the-agency-app", port: str = "8080") -> None:
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
