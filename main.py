# main.py

from config import Config
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.reviewer import ReviewerAgent
from agents.deployer import DeployerAgent
from agents.memory import MemoryManager

def run_agency(prompt):
    print("📡 Launching The Agency...")

    # Init memory/logging system
    memory = MemoryManager()

    # Step 1: Plan the build
    architect = ArchitectAgent(Config, memory)
    plan = architect.generate_plan(prompt)

    # Step 2: Generate the code
    coder = CoderAgent(Config, memory)
    code_files = coder.execute_plan(plan)

    # Step 3: Run and test the code
    tester = TesterAgent(Config, memory)
    test_results = tester.run_tests(code_files)

    # Step 4: QA with GPT-4
    reviewer = ReviewerAgent(Config, memory)
    qa_feedback = reviewer.review_code(code_files)

    # Step 5: Deploy (if tests pass and QA approves)
    deployer = DeployerAgent(Config, memory)
    if tester.all_tests_passed(test_results) and reviewer.qa_passed(qa_feedback):
        deployer.deploy_project(code_files)
    else:
        print("🛑 Deployment aborted: Fix issues first.")

if __name__ == "__main__":
    user_prompt = input("📝 What would you like The Agency to build today?\n> ")
    run_agency(user_prompt)
