# architect.py

from agents.agent_base import BaseAgent
import os

class ArchitectAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "System Architect"
        self.description = "Decomposes user prompt into a software plan"

    def generate_plan(self, user_prompt: str) -> dict:
        print(f"\n🧠 [{self.role}] Planning based on user prompt...")
        
        planning_prompt = f"""
        You are a senior software architect. A user has asked you to build the following:
        \"\"\"{user_prompt}\"\"\"

        Break this into a clear software architecture plan:
        - List major components (frontend, backend, database, etc.)
        - Recommend appropriate technologies and frameworks
        - Define core files/modules and what they will do
        - Suggest a folder structure
        - Include anything the developer needs to know before coding
        Return in JSON format with keys: components, tech_stack, files, notes.
        """

        plan_response = self.call_llm(prompt=planning_prompt, model="ollama", system="You are a software architect.")
        
        try:
            plan = self.safe_json_parse(plan_response)
            self.memory.save("project_plan", plan)
            print("✅ Plan successfully created and saved.")
            return plan
        except Exception as e:
            print("❌ Failed to parse architecture plan:", e)
            return {}

    def safe_json_parse(self, raw_text: str) -> dict:
        import json
        import re

        # Try to extract JSON if there's junk around it
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
        return json.loads(json_match.group(0))
