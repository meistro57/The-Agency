# main.py - Improved version with better error handling and flow control

import logging
import signal
import sys
import os
import importlib
import pkgutil
import re
import time
import requests
import json
from typing import Dict, Optional, List
from config import Config
from agents.memory import MemoryManager
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.reviewer import ReviewerAgent
from agents.fixer import FixerAgent
from agents.deployer import DeployerAgent
from agents.failsafe import FailsafeAgent
from agents.evolution_logger import EvolutionLogger
from agents.self_learner import SelfLearningAgent
from agents.product_creator import ProductCreatorAgent
from agents.rl_optimizer import RLOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agency.log")
    ]
)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs(Config.LOGS_DIR, exist_ok=True)
os.makedirs(Config.PROJECTS_DIR, exist_ok=True)

# Graceful exit handler
def handle_interrupt(sig, frame):
    logger.warning("\n🛑 Process interrupted. Shutting down gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)


class AgencyOrchestrator:
    """Main orchestrator that manages the entire Agency workflow."""
    
    def __init__(self):
        self.config = Config
        self.memory = MemoryManager(self.config)
        self.setup_complete = False
        self.agents = {}
        self.model_manager = None
        
    def setup(self) -> bool:
        """Initialize all components and verify setup."""
        logger.info("🚀 Initializing The Agency...")
        
        # Check API connections
        if not self._check_connections():
            return False
        
        # Initialize model manager
        try:
            from tools.model_manager import ModelManager
            self.model_manager = ModelManager(self.config)
            logger.info(f"📊 Available models: {self.model_manager.get_model_info()}")
        except Exception as e:
            logger.warning(f"Model manager initialization failed: {e}")
        
        # Initialize agents
        try:
            self._initialize_agents()
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            return False
        
        # Load extensions
        self._load_extensions()
        
        self.setup_complete = True
        logger.info("✅ The Agency is ready!")
        return True
    
    def _check_connections(self) -> bool:
        """Verify API endpoints are reachable."""
        logger.info("🔍 Checking API connections...")
        
        # Check Ollama
        ollama_ok = self._check_ollama()
        
        # Check OpenAI if configured
        openai_ok = True
        if hasattr(self.config, "GPT4_API_KEY") and self.config.GPT4_API_KEY and not self.config.GPT4_API_KEY.startswith("your-"):
            openai_ok = self._check_openai()
        
        # We need at least one working LLM
        if not ollama_ok and not openai_ok:
            logger.error("❌ No LLM providers available. Please configure Ollama or OpenAI.")
            return False
        
        return True
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running and has models."""
        try:
            url = self.config.OLLAMA_API_URL.rstrip("/")
            if "/api/" not in url:
                url = f"{url}/api/tags"
            else:
                url = url.replace("/api/chat", "/api/tags")
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                if models:
                    logger.info(f"✅ Ollama is running with {len(models)} models")
                    return True
                else:
                    logger.warning("⚠️ Ollama is running but has no models. Run: ollama pull qwen:7b")
                    # Try to pull a default model
                    self._pull_default_model()
                    return True
            else:
                logger.error(f"❌ Ollama returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to Ollama. Please start it with: ollama serve")
            return False
        except Exception as e:
            logger.error(f"❌ Ollama check failed: {e}")
            return False
    
    def _pull_default_model(self):
        """Try to pull a default Ollama model."""
        import subprocess
        default_model = "qwen:7b"
        try:
            logger.info(f"📥 Pulling default model: {default_model}")
            subprocess.run(["ollama", "pull", default_model], check=True, capture_output=True)
            logger.info(f"✅ Successfully pulled {default_model}")
        except Exception as e:
            logger.warning(f"Failed to pull default model: {e}")
    
    def _check_openai(self) -> bool:
        """Check if OpenAI API is configured and working."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.config.GPT4_API_KEY)
            # Try a minimal API call
            response = client.models.list()
            logger.info("✅ OpenAI API is configured and working")
            return True
        except Exception as e:
            logger.warning(f"⚠️ OpenAI API check failed: {e}")
            return False
    
    def _initialize_agents(self):
        """Initialize all core agents."""
        logger.info("🤖 Initializing agents...")
        
        agent_classes = {
            "architect": ArchitectAgent,
            "coder": CoderAgent,
            "tester": TesterAgent,
            "reviewer": ReviewerAgent,
            "fixer": FixerAgent,
            "deployer": DeployerAgent,
            "failsafe": FailsafeAgent,
            "evolution": EvolutionLogger,
            "learner": SelfLearningAgent,
            "product": ProductCreatorAgent,
            "optimizer": RLOptimizer
        }
        
        for name, agent_class in agent_classes.items():
            try:
                self.agents[name] = agent_class(self.config, self.memory)
                logger.info(f"✅ Initialized {name} agent")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {name} agent: {e}")
                # Only reviewer and fixer are truly optional
                if name not in ["reviewer", "fixer", "learner", "product", "optimizer"]:
                    raise
    
    def _load_extensions(self):
        """Load extension agents."""
        ext_dir = os.path.join(os.path.dirname(__file__), "agents", "extensions")
        if not os.path.isdir(ext_dir):
            return
        
        loaded = 0
        for _, module_name, _ in pkgutil.iter_modules([ext_dir]):
            try:
                full_name = f"agents.extensions.{module_name}"
                module = importlib.import_module(full_name)
                if hasattr(module, "Agent"):
                    agent_cls = getattr(module, "Agent")
                    self.agents[f"ext_{module_name}"] = agent_cls(self.config, self.memory)
                    loaded += 1
            except Exception as e:
                logger.warning(f"Failed to load extension {module_name}: {e}")
        
        if loaded > 0:
            logger.info(f"📦 Loaded {loaded} extension agents")
    
    def run_project(self, prompt: str) -> Dict:
        """
        Execute the complete project generation pipeline.
        
        Args:
            prompt (str): User's project description
            
        Returns:
            Dict with status and results
        """
        if not self.setup_complete:
            if not self.setup():
                return {"status": "failed", "error": "Setup failed"}
        
        # Create project directory
        project_name = self._create_project_name(prompt)
        project_dir = os.path.join(self.config.PROJECTS_DIR, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Update config to use this project directory
        self.config.PROJECTS_DIR = project_dir
        
        logger.info(f"📁 Project directory: {project_dir}")
        
        results = {
            "status": "in_progress",
            "project_name": project_name,
            "project_dir": project_dir,
            "stages": {}
        }
        
        try:
            # Stage 1: Architecture Planning
            logger.info("\n📐 Stage 1: Architecture Planning")
            plan = self._run_stage("architect", lambda: self.agents["architect"].generate_plan(prompt))
            results["stages"]["planning"] = {"status": "success" if plan else "failed", "output": plan}
            
            if not plan or not plan.get("files"):
                logger.error("❌ Architecture planning failed")
                results["status"] = "failed"
                results["error"] = "Failed to create project plan"
                return results
            
            # Stage 2: Code Generation
            logger.info("\n💻 Stage 2: Code Generation")
            code_files = self._run_stage("coder", lambda: self.agents["coder"].execute_plan(plan))
            results["stages"]["coding"] = {"status": "success" if code_files else "failed", "output": code_files}
            
            if not code_files:
                logger.error("❌ Code generation failed")
                results["status"] = "failed"
                results["error"] = "Failed to generate code"
                return results
            
            # Stage 3: Safety Check
            logger.info("\n🛡️ Stage 3: Safety Check")
            if not self._run_safety_check(code_files):
                logger.error("❌ Safety check failed")
                results["status"] = "failed"
                results["error"] = "Code failed safety check"
                return results
            results["stages"]["safety"] = {"status": "success"}
            
            # Stage 4: Testing
            logger.info("\n🧪 Stage 4: Testing")
            test_results = self._run_stage("tester", lambda: self.agents["tester"].run_tests(code_files))
            results["stages"]["testing"] = {"status": "mixed", "output": test_results}
            
            # Stage 5: Fixing (if needed)
            if self._has_test_failures(test_results) and "fixer" in self.agents:
                logger.info("\n🔧 Stage 5: Auto-Fixing")
                fixes = self._run_stage("fixer", lambda: self.agents["fixer"].fix_code(code_files, test_results))
                results["stages"]["fixing"] = {"status": "attempted", "output": fixes}
                
                # Re-test after fixes
                if fixes:
                    test_results = self._run_stage("tester", lambda: self.agents["tester"].run_tests(code_files))
                    results["stages"]["retesting"] = {"status": "mixed", "output": test_results}
            
            # Stage 6: Code Review (optional)
            if "reviewer" in self.agents and self.config.USE_GPT4_FOR_QA:
                logger.info("\n📝 Stage 6: Code Review")
                reviews = self._run_stage("reviewer", lambda: self.agents["reviewer"].review_code(code_files))
                results["stages"]["review"] = {"status": "success", "output": reviews}
            
            # Stage 7: Documentation
            logger.info("\n📚 Stage 7: Documentation")
            self._generate_documentation(project_dir, plan, results)
            
            # Final status
            results["status"] = "success"
            results["message"] = f"Project '{project_name}' generated successfully!"
            
            # Log completion
            self.agents["evolution"].log_event(f"Project completed: {project_name}")
            
        except Exception as e:
            logger.exception(f"❌ Pipeline failed with error: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def _run_stage(self, stage_name: str, func) -> any:
        """Run a pipeline stage with error handling."""
        try:
            return func()
        except Exception as e:
            logger.error(f"❌ {stage_name} stage failed: {e}")
            return None
    
    def _run_safety_check(self, code_files: List[str]) -> bool:
        """Run safety checks on generated code."""
        failsafe = self.agents["failsafe"]
        
        for path in code_files:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not failsafe.check_text(content):
                        logger.error(f"❌ Failsafe triggered for {path}")
                        return False
            except Exception as e:
                logger.warning(f"Could not check {path}: {e}")
        
        return True
    
    def _has_test_failures(self, test_results: Dict) -> bool:
        """Check if any tests failed."""
        if not test_results:
            return False
        
        for result in test_results.values():
            if isinstance(result, dict) and result.get("status") == "failed":
                return True
        return False
    
    def _generate_documentation(self, project_dir: str, plan: Dict, results: Dict):
        """Generate project documentation."""
        readme_path = os.path.join(project_dir, "README.md")
        
        readme_content = f"""# {plan.get('project_name', 'Project')}

## Overview
{plan.get('architecture_notes', 'A software project generated by The Agency.')}

## Project Type
{plan.get('project_type', 'General')}

## Tech Stack
"""
        
        tech_stack = plan.get('tech_stack', {})
        for category, tech in tech_stack.items():
            if tech:
                readme_content += f"- **{category.title()}**: {tech}\n"
        
        readme_content += f"""

## Components
"""
        
        for component in plan.get('components', []):
            readme_content += f"- **{component['name']}**: {component['description']}\n"
        
        readme_content += f"""

## Setup Instructions
1. Clone this repository
2. Install dependencies:
"""
        
        deps = plan.get('dependencies', {})
        if deps.get('python'):
            readme_content += "   ```bash\n   pip install -r requirements.txt\n   ```\n"
        if deps.get('npm'):
            readme_content += "   ```bash\n   npm install\n   ```\n"
        
        readme_content += f"""

## Security Notes
{plan.get('security_notes', 'Follow security best practices.')}

## Deployment
{plan.get('deployment_notes', 'See Dockerfile for containerized deployment.')}

---
*Generated by The Agency*
"""
        
        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            logger.info("✅ Generated README.md")
        except Exception as e:
            logger.error(f"Failed to write README: {e}")
    
    def _create_project_name(self, prompt: str) -> str:
        """Create a filesystem-friendly project name."""
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]+\b', prompt.lower())
        # Filter out common words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if words:
            # Take first few meaningful words
            name = "-".join(words[:4])
        else:
            name = "project"
        
        # Add timestamp to ensure uniqueness
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        return f"{name}-{timestamp}"[:50]  # Limit length


def run_agency(prompt: str) -> None:
    """
    Main entry point for The Agency.
    
    Args:
        prompt (str): User's project description
    """
    if not prompt or not prompt.strip():
        logger.error("❌ Prompt cannot be empty")
        return
    
    logger.info(f"📋 Project Request: {prompt}")
    
    orchestrator = AgencyOrchestrator()
    results = orchestrator.run_project(prompt)
    
    # Print summary
    print("\n" + "="*50)
    print(f"🏁 Project Generation {'Completed' if results['status'] == 'success' else 'Failed'}")
    print("="*50)
    
    if results["status"] == "success":
        print(f"✅ Project Name: {results['project_name']}")
        print(f"📁 Location: {results['project_dir']}")
        print("\n📊 Stage Results:")
        for stage, info in results["stages"].items():
            status_icon = "✅" if info["status"] == "success" else "⚠️"
            print(f"  {status_icon} {stage.title()}: {info['status']}")
        print(f"\n💡 Next Steps:")
        print(f"  1. cd {results['project_dir']}")
        print(f"  2. Read README.md for setup instructions")
        print(f"  3. Install dependencies and run the project")
    else:
        print(f"❌ Error: {results.get('error', 'Unknown error')}")
        if results.get("stages"):
            print("\n📊 Stage Results:")
            for stage, info in results["stages"].items():
                status_icon = "✅" if info.get("status") == "success" else "❌"
                print(f"  {status_icon} {stage.title()}: {info.get('status', 'not run')}")


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            # Command line argument provided
            prompt = " ".join(sys.argv[1:])
        else:
            # Interactive mode
            print("🤖 Welcome to The Agency")
            print("💡 Tell me what you want to build...")
            prompt = input("\n> ").strip()
        
        if prompt:
            run_agency(prompt)
        else:
            print("❌ No prompt provided")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.exception(f"💥 Fatal error: {e}")
        sys.exit(1)
