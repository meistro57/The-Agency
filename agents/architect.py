# agents/architect.py - Improved version with better prompt engineering

import os
import re
import json
import logging
from agents.agent_base import BaseAgent
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ArchitectAgent(BaseAgent):
    """
    Enhanced ArchitectAgent with better planning capabilities and structured output.
    """

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "System Architect"
        self.description = "Decomposes user prompt into a software plan"
        
        # Try to use the best model for architecture tasks
        try:
            from tools.model_manager import ModelManager
            mm = ModelManager(config)
            self.preferred_model = mm.get_best_model_for_task("architecture") or "gpt-4o"
        except:
            self.preferred_model = "gpt-4o"

    def generate_plan(self, user_prompt: str) -> dict:
        """
        Generates a comprehensive software architecture plan.
        
        Args:
            user_prompt (str): The prompt describing what software to build.
            
        Returns:
            dict: A validated and normalized software plan dictionary.
        """
        logger.info(f"\n🧠 [{self.role}] Planning architecture...")
        
        # First, analyze what type of project this is
        project_type = self._analyze_project_type(user_prompt)
        
        # Generate appropriate plan based on project type
        planning_prompt = self._create_planning_prompt(user_prompt, project_type)
        
        try:
            plan_response = self.call_llm(
                prompt=planning_prompt,
                model=self.preferred_model,
                system="You are a senior software architect. Always respond with valid JSON only."
            )
            
            logger.debug("📝 Raw plan response:\n" + plan_response)
            plan = self.extract_json_from_response(plan_response)
            plan = self._enhance_plan(plan, project_type)
            plan = self.normalize_plan(plan)
            
        except Exception as e:
            logger.error(f"❌ Failed to parse architecture plan: {e}")
            # Use a robust fallback plan
            plan = self._create_fallback_plan(user_prompt, project_type)
        
        # Validate plan has required fields
        if not plan.get("files") or len(plan["files"]) == 0:
            logger.warning("⚠️ Plan has no files. Adding default structure...")
            plan["files"] = self._get_default_files_for_type(project_type)
        
        # Save to memory
        self.memory.save(f"{self.__class__.__name__}::plan", plan)
        self.memory.save(f"{self.__class__.__name__}::project_type", project_type)
        
        logger.info(f"✅ Plan created: {len(plan.get('files', []))} files, {len(plan.get('components', []))} components")
        return plan

    def _analyze_project_type(self, user_prompt: str) -> str:
        """Analyze the prompt to determine project type."""
        prompt_lower = user_prompt.lower()
        
        # Keywords for different project types
        project_types = {
            "web_fullstack": ["website", "web app", "full stack", "react", "vue", "angular", "frontend and backend"],
            "api": ["api", "rest", "graphql", "microservice", "backend only", "server"],
            "cli": ["cli", "command line", "terminal", "console app", "script"],
            "data_pipeline": ["etl", "data pipeline", "scraper", "crawler", "data processing"],
            "ml": ["machine learning", "ml", "ai model", "neural network", "prediction"],
            "game": ["game", "snake", "tetris", "puzzle", "arcade"],
            "mobile": ["mobile app", "ios", "android", "react native"],
            "desktop": ["desktop app", "gui", "pyqt", "electron", "tkinter"],
            "automation": ["automation", "bot", "automate", "workflow"],
            "static_site": ["landing page", "static site", "portfolio", "blog", "documentation"]
        }
        
        for project_type, keywords in project_types.items():
            if any(keyword in prompt_lower for keyword in keywords):
                logger.info(f"Detected project type: {project_type}")
                return project_type
        
        # Default to general web app
        return "web_fullstack"

    def _create_planning_prompt(self, user_prompt: str, project_type: str) -> str:
        """Create a detailed planning prompt based on project type."""
        
        type_specific_guidance = {
            "web_fullstack": """
Focus on:
- Frontend framework (React/Vue/Angular/Vanilla)
- Backend framework (Express/FastAPI/Django)
- Database choice (PostgreSQL/MongoDB/SQLite)
- Authentication and security
- API design (REST/GraphQL)
- State management
- Responsive design
""",
            "api": """
Focus on:
- API framework (FastAPI/Express/Flask)
- Database and ORM
- Authentication (JWT/OAuth)
- Rate limiting
- API documentation (Swagger/OpenAPI)
- Error handling
- Testing strategy
""",
            "cli": """
Focus on:
- Argument parsing
- Configuration management
- Output formatting
- Error handling
- Help documentation
- Installation/distribution
""",
            "ml": """
Focus on:
- Data preprocessing pipeline
- Model architecture
- Training scripts
- Evaluation metrics
- Model serving/deployment
- Data storage
- Visualization
"""
        }
        
        guidance = type_specific_guidance.get(project_type, "")
        
        return f"""
You are a senior software architect. A user has asked you to build:
"{user_prompt}"

Project Type Detected: {project_type}

{guidance}

Create a comprehensive software architecture plan with:

1. Components: List all major system components
2. Tech Stack: Specific technologies for each component
3. Files: Complete list of files with clear descriptions
4. Dependencies: Required packages/libraries
5. Architecture: High-level system design
6. Security: Key security considerations
7. Deployment: How to deploy the system

Return ONLY a valid JSON object with this structure:
{{
    "project_name": "descriptive-project-name",
    "project_type": "{project_type}",
    "components": [
        {{
            "name": "component-name",
            "description": "what it does",
            "technology": "specific tech used"
        }}
    ],
    "tech_stack": {{
        "frontend": "technology or null",
        "backend": "technology",
        "database": "technology or null",
        "other": ["additional technologies"]
    }},
    "files": [
        {{
            "path": "relative/path/to/file.ext",
            "description": "detailed description of what this file does",
            "component": "which component it belongs to"
        }}
    ],
    "dependencies": {{
        "python": ["package1", "package2"],
        "npm": ["package1", "package2"],
        "system": ["docker", "redis"]
    }},
    "architecture_notes": "High-level architecture description",
    "security_notes": "Key security considerations",
    "deployment_notes": "Deployment instructions"
}}

Ensure the plan is production-ready and follows best practices.
"""

    def _enhance_plan(self, plan: dict, project_type: str) -> dict:
        """Enhance the plan with additional standard files."""
        
        # Add standard files that are often missing
        standard_files = []
        
        # Check if we have a README
        if not any(f.get("path", "").lower() == "readme.md" for f in plan.get("files", [])):
            standard_files.append({
                "path": "README.md",
                "description": "Project documentation with setup and usage instructions",
                "component": "documentation"
            })
        
        # Check for requirements/package files
        has_requirements = any("requirements.txt" in f.get("path", "") for f in plan.get("files", []))
        has_package_json = any("package.json" in f.get("path", "") for f in plan.get("files", []))
        
        if not has_requirements and plan.get("tech_stack", {}).get("backend") in ["flask", "fastapi", "django", "python"]:
            standard_files.append({
                "path": "requirements.txt",
                "description": "Python dependencies",
                "component": "configuration"
            })
        
        if not has_package_json and plan.get("tech_stack", {}).get("frontend") in ["react", "vue", "angular", "javascript"]:
            standard_files.append({
                "path": "package.json",
                "description": "Node.js dependencies and scripts",
                "component": "configuration"
            })
        
        # Add .gitignore
        if not any(".gitignore" in f.get("path", "") for f in plan.get("files", [])):
            standard_files.append({
                "path": ".gitignore",
                "description": "Git ignore file for version control",
                "component": "configuration"
            })
        
        # Add environment config
        if project_type in ["web_fullstack", "api"] and not any(".env" in f.get("path", "") for f in plan.get("files", [])):
            standard_files.append({
                "path": ".env.example",
                "description": "Example environment variables",
                "component": "configuration"
            })
        
        # Add Dockerfile for deployable projects
        if project_type in ["web_fullstack", "api", "ml"] and not any("Dockerfile" in f.get("path", "") for f in plan.get("files", [])):
            standard_files.append({
                "path": "Dockerfile",
                "description": "Docker container configuration",
                "component": "deployment"
            })
        
        # Add tests directory
        if not any("test" in f.get("path", "").lower() for f in plan.get("files", [])):
            if plan.get("tech_stack", {}).get("backend") == "python":
                standard_files.append({
                    "path": "tests/test_main.py",
                    "description": "Unit tests for main functionality",
                    "component": "testing"
                })
            elif plan.get("tech_stack", {}).get("backend") in ["javascript", "node"]:
                standard_files.append({
                    "path": "tests/main.test.js",
                    "description": "Unit tests for main functionality",
                    "component": "testing"
                })
        
        # Add the standard files to the plan
        if "files" not in plan:
            plan["files"] = []
        plan["files"].extend(standard_files)
        
        return plan

    def _get_default_files_for_type(self, project_type: str) -> List[Dict[str, str]]:
        """Get default file structure based on project type."""
        
        default_structures = {
            "web_fullstack": [
                {"path": "frontend/src/App.js", "description": "Main React application component", "component": "frontend"},
                {"path": "frontend/src/index.js", "description": "React application entry point", "component": "frontend"},
                {"path": "frontend/src/index.css", "description": "Global styles", "component": "frontend"},
                {"path": "frontend/package.json", "description": "Frontend dependencies", "component": "frontend"},
                {"path": "backend/server.py", "description": "FastAPI server with API endpoints", "component": "backend"},
                {"path": "backend/models.py", "description": "Database models", "component": "backend"},
                {"path": "backend/routes.py", "description": "API route handlers", "component": "backend"},
                {"path": "backend/requirements.txt", "description": "Python dependencies", "component": "backend"},
                {"path": "docker-compose.yml", "description": "Multi-container Docker setup", "component": "deployment"},
                {"path": "README.md", "description": "Project documentation", "component": "documentation"}
            ],
            "api": [
                {"path": "app/main.py", "description": "FastAPI application entry point", "component": "api"},
                {"path": "app/routes.py", "description": "API route definitions", "component": "api"},
                {"path": "app/models.py", "description": "Pydantic models for request/response", "component": "api"},
                {"path": "app/database.py", "description": "Database connection and setup", "component": "api"},
                {"path": "app/auth.py", "description": "Authentication and authorization", "component": "api"},
                {"path": "requirements.txt", "description": "Python dependencies", "component": "configuration"},
                {"path": "Dockerfile", "description": "Container configuration", "component": "deployment"},
                {"path": ".env.example", "description": "Environment variables example", "component": "configuration"},
                {"path": "README.md", "description": "API documentation", "component": "documentation"},
                {"path": "tests/test_api.py", "description": "API endpoint tests", "component": "testing"}
            ],
            "cli": [
                {"path": "src/main.py", "description": "CLI entry point with argument parsing", "component": "core"},
                {"path": "src/commands.py", "description": "Command implementations", "component": "core"},
                {"path": "src/utils.py", "description": "Utility functions", "component": "core"},
                {"path": "src/config.py", "description": "Configuration management", "component": "core"},
                {"path": "requirements.txt", "description": "Python dependencies", "component": "configuration"},
                {"path": "setup.py", "description": "Package setup for distribution", "component": "configuration"},
                {"path": "README.md", "description": "CLI usage documentation", "component": "documentation"},
                {"path": "tests/test_cli.py", "description": "CLI command tests", "component": "testing"}
            ],
            "ml": [
                {"path": "src/data_loader.py", "description": "Data loading and preprocessing", "component": "data"},
                {"path": "src/model.py", "description": "Model architecture definition", "component": "model"},
                {"path": "src/train.py", "description": "Training script with metrics", "component": "training"},
                {"path": "src/evaluate.py", "description": "Model evaluation and metrics", "component": "evaluation"},
                {"path": "src/predict.py", "description": "Inference script", "component": "inference"},
                {"path": "notebooks/exploration.ipynb", "description": "Data exploration notebook", "component": "analysis"},
                {"path": "requirements.txt", "description": "Python dependencies", "component": "configuration"},
                {"path": "README.md", "description": "Model documentation and usage", "component": "documentation"},
                {"path": "tests/test_model.py", "description": "Model unit tests", "component": "testing"}
            ]
        }
        
        return default_structures.get(project_type, default_structures["web_fullstack"])

    def _create_fallback_plan(self, user_prompt: str, project_type: str) -> dict:
        """Create a robust fallback plan when LLM fails."""
        logger.warning("Using fallback plan generation")
        
        # Extract potential project name from prompt
        words = user_prompt.lower().split()[:5]
        project_name = "-".join(word for word in words if len(word) > 2)[:30] or "project"
        
        base_plan = {
            "project_name": project_name,
            "project_type": project_type,
            "components": [
                {"name": "core", "description": "Main application logic", "technology": "Python/JavaScript"},
                {"name": "api", "description": "API endpoints", "technology": "FastAPI/Express"},
                {"name": "database", "description": "Data persistence", "technology": "SQLite/PostgreSQL"}
            ],
            "tech_stack": {
                "frontend": "React" if project_type == "web_fullstack" else None,
                "backend": "FastAPI" if "python" in user_prompt.lower() else "Express",
                "database": "PostgreSQL",
                "other": ["Docker", "Redis"]
            },
            "files": self._get_default_files_for_type(project_type),
            "dependencies": {
                "python": ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-dotenv"],
                "npm": ["express", "dotenv", "cors"] if "node" in user_prompt.lower() else [],
                "system": ["docker", "postgresql"]
            },
            "architecture_notes": f"Standard {project_type} architecture with separation of concerns",
            "security_notes": "Implement authentication, validate inputs, use HTTPS, secure database",
            "deployment_notes": "Use Docker for containerization, deploy to cloud platform"
        }
        
        return base_plan

    def normalize_plan(self, plan: dict) -> dict:
        """
        Ensures the plan is properly formatted and complete.
        
        Args:
            plan (dict): The raw plan dictionary.
            
        Returns:
            dict: Normalized plan with consistent structure.
        """
        # Ensure all required fields exist
        plan.setdefault("project_name", "unnamed-project")
        plan.setdefault("project_type", "general")
        plan.setdefault("components", [])
        plan.setdefault("tech_stack", {})
        plan.setdefault("dependencies", {})
        plan.setdefault("architecture_notes", "")
        plan.setdefault("security_notes", "")
        plan.setdefault("deployment_notes", "")
        
        # Normalize files field
        raw_files = plan.get("files", [])
        normalized_files = []
        
        if isinstance(raw_files, dict):
            # Convert dict to list format
            for path, description in raw_files.items():
                normalized_files.append({
                    "path": path.strip(),
                    "description": str(description).strip(),
                    "component": "unknown"
                })
        elif isinstance(raw_files, list):
            for file_item in raw_files:
                if isinstance(file_item, dict) and "path" in file_item:
                    normalized_files.append({
                        "path": file_item["path"].strip(),
                        "description": file_item.get("description", "Auto-generated file").strip(),
                        "component": file_item.get("component", "unknown")
                    })
                elif isinstance(file_item, str):
                    normalized_files.append({
                        "path": file_item.strip(),
                        "description": "Auto-generated file",
                        "component": "unknown"
                    })
        
        plan["files"] = normalized_files
        
        # Validate file paths
        validated_files = []
        for file_spec in plan["files"]:
            path = file_spec["path"]
            # Skip invalid paths
            if not path or ".." in path or path.startswith("/"):
                logger.warning(f"Skipping invalid path: {path}")
                continue
            # Ensure path uses forward slashes
            file_spec["path"] = path.replace("\\", "/")
            validated_files.append(file_spec)
        
        plan["files"] = validated_files
        
        # Log plan summary
        logger.info(f"Normalized plan: {plan['project_name']} ({plan['project_type']})")
        logger.info(f"Components: {[c['name'] for c in plan['components']]}")
        logger.info(f"Files: {len(plan['files'])}")
        
        return plan
