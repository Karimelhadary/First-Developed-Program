from flask import Flask

app = Flask(__name__)



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
    current = _next_id
    _next_id += 1
    return current

def find_task(task_id: int):
    for t in tasks:
        if t.id == task_id:
            return t
    return None



import routes.splash
import routes.login
import routes.dashboard
import routes.tasks
import routes.insights


if __name__ == "__main__":
    app.run(debug=True)
