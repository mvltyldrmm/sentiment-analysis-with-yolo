from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import shutil
import os
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import aiofiles
import cv2
from detector import fonk
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/', response_class=HTMLResponse)  # basic get view
async def getRoot():
    async with aiofiles.open("templates/index.html", mode="r") as f:
        data = await f.read()
    return data


@app.get('/detect', response_class=HTMLResponse)
async def proceed():
    async with aiofiles.open("templates/emotions.html", mode="r") as f:
        data = await f.read()
    return data


@app.post("/upload")
def emotiondetection(image: UploadFile = File(...)):
    save_file(image, path="temp", save_as="temp")
    return{"text": "File Uploaded Successfully"}


@app.post("/predict")
def emotions():
    result_detection = fonk("temp/temp.webm")
    return {"RESULT :": result_detection}


def save_file(uploaded_file, path=".", save_as="default"):
    extension = os.path.splitext(uploaded_file.filename)[-1]
    temp_file = os.path.join(path, save_as + extension)
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return temp_file
