# deployer.py

from agents.agent_base import BaseAgent
import os
import subprocess

class DeployerAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Deployment Manager"
        self.description = "Packages and deploys the application (Docker, CI, etc.)"

    def deploy_project(self, file_paths: list):
        print(f"\n🚀 [{self.role}] Deploying project...")

        # Step 1: Generate Dockerfile if missing
        docker_path = os.path.join(self.config.PROJECTS_DIR, "Dockerfile")
        if not os.path.exists(docker_path):
            self._generate_dockerfile(file_paths)

        # Step 2: Build Docker image
        self._build_docker_image()

        # Step 3: Run container (optional)
        self._run_container()

        print("✅ Deployment complete.")

    def _generate_dockerfile(self, file_paths: list):
        app_entry = "main.py"
        if not any("main.py" in path for path in file_paths):
            app_entry = file_paths[0] if file_paths else "app.py"

        dockerfile = f"""
        # Auto-generated Dockerfile
        FROM python:3.10-slim
        WORKDIR /app
        COPY . .
        RUN pip install -r requirements.txt || true
        CMD ["python", "{app_entry}"]
        """

        docker_path = os.path.join(self.config.PROJECTS_DIR, "Dockerfile")
        with open(docker_path, "w") as f:
            f.write(dockerfile.strip())

        print("📦 Dockerfile generated.")

    def _build_docker_image(self):
        print("🔧 Building Docker image...")
        try:
            subprocess.run(
                ["docker", "build", "-t", "the-agency-app", self.config.PROJECTS_DIR],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker build failed: {e}")

    def _run_container(self):
        print("🐳 Running Docker container...")
        try:
            subprocess.run(
                ["docker", "run", "-d", "--rm", "-p", "8080:8080", "the-agency-app"],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to run container: {e}")
