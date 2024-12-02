from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import List
from tasks import process_file
import os
from pydantic import Json
import json

app = FastAPI()

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...),
                           email: str = Form(...),
                            num_questions: int = Form(...)):
    try:
        # data = json.loads(data)
        file_paths = []
        for file in files:
            file_path = f"./uploads/{file.filename}"
            os.makedirs("./uploads", exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(await file.read())

            task = process_file.apply_async(args=[file_path, email, num_questions])
            file_paths.append({"filename": file.filename, "task_id": task.id})

        return {"status": True, "process_metadata": file_paths}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
def get_status(task_id: str):
    task = process_file.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {'status': 'Task is still pending'}
    elif task.state == 'STARTED':
        response = {'status': 'Task is being processed'}
    elif task.state == 'SUCCESS':
        response = {'status': 'Task completed', 'result': task.result}
    elif task.state == 'FAILURE':
        response = {'status': 'Task failed', 'result': str(task.info)}

    return response
