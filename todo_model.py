#todo_model.py


import os

import json

from datetime import date, datetime
from pathlib import Path



script_dir = Path(__file__).resolve().parent 
print(script_dir)

lists_locations = Path(script_dir / "lists")
lists_locations.mkdir(exist_ok=True)

day_dict = {"Sunday":0, "Monday":1, "Tuseday":2, "Wednesday":3, "Thursday":4, "Friday":5, "Saturday":6}


class todo_list():
    """
    Todolist class object, will hold list of task objects in this todolist
    """
    def __init__(self, name, tasks=None, new=True):

        self.name = name
        self.tasks = tasks if tasks is not None else []

        
        self.file_name = f"lists/{name.replace(" ", "_")}-TheGoodToDoList.json"


        

        
        if new:
            self.save_to_file()

        
        
        print("Successfully created todo list " + self.name + "\n")

    def to_dict(self):
        tasks_dict = []
        for task in self.tasks:
            tasks_dict.append(task.to_dict())
        return {
            "name": self.name,
            "tasks": tasks_dict,
        }

    @classmethod
    def from_dict(cls, data):
        tasks_dict = data["tasks"]
        tasks_list = []
        for item in tasks_dict:
            tasks_list.append(task.from_dict(item))
        return cls(
            name=data["name"],
            tasks=tasks_list,
            new=False
        )

    @classmethod
    def load_from_file(cls, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def addTask(self, task_text, deadline_date=None, completion_status="incomplete", priority_level=None, task_time_stamp=None):
        self.tasks.append(task(task_text, 
                                deadline = deadline_date if deadline_date else None, 
                                status = completion_status if completion_status else None,
                                priority = priority_level if priority_level else None,
                                time = task_time_stamp if task_time_stamp else None))
        
        # with open( script_dir / self.file_name, "a") as o:
        #     o.write(f"{self.tasks[-1].to_dict()} \n \n")

    def import_task(self, task_text, deadline_date, completion_status, priority_level, task_time_stamp):
        self.tasks.append(task(task_text, 
                        deadline = deadline_date, 
                        status = completion_status,
                        priority = priority_level,
                        time = task_time_stamp))

    def show_tasks(self):
        for i in range(len(self.tasks)):
            print(f"{i+1}. {self.tasks[i]}")

    # def updateFile(self):
    #     with open(f"{self.file_name}", "w") as f:
    #         f.write(f"{self.name}\n\n")

    #         for i in self.tasks:
    #             f.write(f"{i}\n\n")

    def deleteSelf(self):
        if os.path.exists(self.file_name):
            os.remove(self.file_name)
        else:
            print("File does not exist")

    def save_to_file(self):
        with open(self.file_name, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


    


class task():
    def __init__(self, task_text, deadline=None, status="incomplete", priority=None, time=None, notes=None): 
        self.task_text = task_text
        self.deadline = deadline
        self.status = status
        self.priority = priority 
        self.time = time if time else str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.notes = notes


    def to_dict(self):
        return {
            "task_text": self.task_text,
            "deadline": self.deadline,
            "status": self.status,
            "priority": self.priority, 
            "time": self.time,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            task_text=data["task_text"],
            deadline=data["deadline"],
            status=data["status"],
            priority=data["priority"],
            time=data["time"],
            notes=data["notes"],
        )

    def setText(self, t):
        self.task_text = t

    def setDeadline(self, d):
        self.deadline = d

    def setStatus(self, s):
        self.status = s 

    def setPriority(self, p):
        self.priority = p

    def setTime(self, t):
        self.time = t

    def setNotes(self, n):
        self.notes = n
    


    def __repr__(self):

        return f"""Name: {self.task_text}
        Deadline: {self.deadline}
        Status: {self.status}
        Priority: {self.priority}
        Time Created: {self.time}"""
    
def import_files():
    """
    imports previously created and saved lists from script_dir/lists
    """
    imported_lists = []
    saved_lists = [f.name for f in lists_locations.iterdir() if f.is_file()]


    for saved_list in saved_lists:

        full_path = Path(lists_locations / saved_list)
        imported_lists.append(todo_list.load_from_file(full_path))
        
                    
    return imported_lists


