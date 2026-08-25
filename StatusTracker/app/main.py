from re import S
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from sqlalchemy import select

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Broken Task API")


@app.get("/")
def root():
    return {"message": "Broken Task API"}


# Changes not being committed. TODO: Commit changes
# Actually have to update database
# Completed should = false on initial creation
@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    print("CREATING TASK")
    new_task = models.Task(
        title=task.title,
        description=task.description,
        # starting off with completion = False but is default behavior already
        #completed = False
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# 
@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):

    statement = select(models.Task).where(models.Task.id == task_id)
    task = db.execute(statement).scalar()

    if task is None:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found",
    )
    return task

#TODO: Implement
# should be able to update title and description + completion status
@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):

    statement = select(models.Task).where(models.Task.id == task_id)
    retrievedTask = db.execute(statement).scalar()

    if retrievedTask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.title:
        retrievedTask.title = task.title

    if task.description:
        retrievedTask.description = task.description
    
    if task.completed:
        retrievedTask.completed = task.completed



    db.commit()
    return retrievedTask


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    # Only deleting first row of database. TODO: FIX THIS
    #task = db.query(models.Task).order_by(models.Task.id).first()
    statement = select(models.Task).where(models.Task.id == task_id)
    task = db.execute(statement).scalar()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()
    return None
