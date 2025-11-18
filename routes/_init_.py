class Task:
    def __init__(self, id, title, description, due_date,
                 importance, complexity, energy, completed=False):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.importance = importance
        self.complexity = complexity
        self.energy = energy
        self.completed = completed

tasks = []
_next_id = 1

def get_next_id():
    global _next_id
    task_id = _next_id
    _next_id += 1
    return task_id

def find_task(task_id: int):
    for t in tasks:
        if t.id == task_id:
            return t
    return None

# EXPORTS
__all__ = ["Task", "tasks", "get_next_id", "find_task"]
