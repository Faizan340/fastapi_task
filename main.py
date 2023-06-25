import os
import psycopg2

from psycopg2 import Error
# import mysql.connector
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials


app = FastAPI()
security = HTTPBasic()

# Loading environment variables from .env file
load_dotenv()

# PostgreSQL database connection settings
pg_host = os.getenv("PG_HOST")
pg_port = os.getenv("PG_PORT")
pg_user = os.getenv("PG_USER")
pg_password = os.getenv("PG_PASSWORD")
pg_database = os.getenv("PG_DATABASE")

# Creating a PostgreSQL connection
try:
    db_connection = psycopg2.connect(
        host=pg_host,
        port=pg_port,
        user=pg_user,
        password=pg_password,
        database=pg_database
    )
except Error as e:
    print("Error connecting to PostgreSQL database:", e)

# # MySQL database connection settings
# mysql_host = "localhost"
# mysql_user = "your_mysql_username"
# mysql_password = "your_mysql_password"
# mysql_database = "your_mysql_database"

# # Creating a MySQL connection
# db_connection = mysql.connector.connect(
#     host=mysql_host,
#     user=mysql_user,
#     password=mysql_password,
#     database=mysql_database
# )

# Placeholder for storing tasks
tasks = []

# Model for ToDo task
class Task(BaseModel):
    id: int
    title: str
    description: str
    done: bool

# Authentication
def get_current_username(credentials: HTTPBasicCredentials):
    correct_username = "admin"
    correct_password = "password"
    if (credentials.username == correct_username and
            credentials.password == correct_password):
        return credentials.username
    raise HTTPException(
        status_code=401,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )

# Routes
@app.get("/tasks", response_model=List[Task])
def get_tasks(username: str = Depends(get_current_username)):
    return tasks

@app.post("/tasks", response_model=Task)
def create_task(task: Task, username: str = Depends(get_current_username)):
    tasks.append(task)
    return task

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, username: str = Depends(get_current_username)):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task, username: str = Depends(get_current_username)):
    for i, t in enumerate(tasks):
        if t.id == task_id:
            tasks[i] = task
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, username: str = Depends(get_current_username)):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")


# Closing the PostgreSQL connection when the server stops
@app.on_event("shutdown")
def shutdown_event():
    db_connection.close()
