import subprocess

# Define the Python script as a string
text = """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


import uvicorn
uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
"""

# Path to the Python executable in the virtual environment
python_venv_path = r"C:\Users\ALL USER\Desktop\others_programing\source code\ubuntu\NLP\QueenDahyun_nlp\dahwin\Scripts\python.exe"

import subprocess

# Define the Python script as a string
text = """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
"""

# Define the path to the Python 3.11 interpreter
python_3_11_path = r"C:\Users\ALL USER\Desktop\others_programing\source code\ubuntu\NLP\QueenDahyun_nlp\dahwin\Scripts\python.exe"

# Use subprocess to run the code
process = subprocess.Popen([python_3_11_path, "-c", text])
process.wait()
