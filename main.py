# from enum import Enum
# from  fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()

# class Category(Enum):
#     PERSONAL = 'personal'
#     WORK='work'

# class Todo(BaseModel):
#     title: str
#     completed: bool
#     id: int
#     category: Category

#     todos ={
#         0: Todo(title='test1', completed=True, id=0, category=Category.PERSONAL),
#         1: Todo(title='test2', completed=False, id=1, category=Category.WORK)
#     }

#     # @app.get('/')
#     # def index() -> dict:
#     #     return {'todos':todos}
from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Category(Enum):
    PERSONAL = 'personal'
    WORK = 'work'

# Define the Todo class
class Todo(BaseModel):
    title: str
    completed: bool
    id: int
    category: Category

# Define the todos dictionary outside of the Todo class
todos = {
    0: Todo(title='test1', completed=True, id=0, category=Category.PERSONAL),
    1: Todo(title='test2', completed=False, id=1, category=Category.WORK)
}

@app.get("/")
def index():
    return {"todos": todos}

@app.get("/todos/{todo_id}")
def get_todo_by_id(todo_id: int)->Todo:
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail=f'ID {todo_id} does not exist')
    return todos[todo_id]

app.get('/todos/')
def query_todo_by_completed(completed: Optional[bool]=None)->dict[str, list[Todo]]:
    if completed is None:
        filtered_todos = list(todos.values())
    else: 
         filtered_todos = [todo for todo in todos.values() if todo.completed == completed]
    # filtered_todos = [todo for todo in todos.values() if todo.completed is completed]
    return {'todos': filtered_todos}

@app.post('/')
def create_todo(todo:Todo)->dict[str, Todo]:
    if todo.id in todos:
        raise HTTPException(status_code=400, detail=f'ID {todo.id} already exists')
    todos[todo.id] = todo
    return {'todo': todo}

@app.put('/todos/{todo_id}')
def update_todo(todo_id, todo:Todo)->dict[str, Todo]:
    todos[todo_id] = todo
    return {'todo':Todo}

@app.delete('/todos/{todo_id}')
def delete_todo(todo_id:int)->dict[str, Todo]:
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail=f'ID {todo_id} does not exist.')
    todo = todos.pop(todo_id)
    return {'todo':Todo}