# task_manager.py

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.completed = []

    def add_task(self, task: str):
        self.tasks.append(task)

    def complete_task(self, task: str):
        if task in self.tasks:
            self.tasks.remove(task)
            self.completed.append(task)

    def has_remaining(self) -> bool:
        return len(self.tasks) > 0

    def next_task(self):
        return self.tasks[0] if self.tasks else None

    def summary(self) -> dict:
        return {
            "pending": self.tasks,
            "completed": self.completed
        }
