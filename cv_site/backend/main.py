from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from detect_onnx import ONNXDetector
from detect_pt import PTDetector
import shutil
import uuid
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Указывай адрес фронта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаём папки, если их нет
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# detector = ONNXDetector("model/model_5783f.onnx")
detector = PTDetector("model/model_5783f.pt", device="cuda")

SUPPORTED_IMAGE_EXTS = {"jpg", "jpeg", "png"}
SUPPORTED_VIDEO_EXTS = {"mp4", "avi", "mov", "mkv"}


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if not ext:
        raise HTTPException(
            status_code=400, detail="Файл без расширения не поддерживается."
        )
    if ext not in SUPPORTED_IMAGE_EXTS and ext not in SUPPORTED_VIDEO_EXTS:
        raise HTTPException(status_code=400, detail=f"Формат .{ext} не поддерживается.")

    # Проверка размера файла до сохранения
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > detector.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Размер файла превышает {detector.MAX_FILE_SIZE // (1024*1024)} МБ.",
        )

    filename = f"uploads/{uuid.uuid4()}.{ext}"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_path = f"outputs/{uuid.uuid4()}.{ext}"

    try:
        if ext in SUPPORTED_IMAGE_EXTS:
            detector.run_on_image(filename, output_path)
        elif ext in SUPPORTED_VIDEO_EXTS:
            detector.run_on_video(filename, output_path)
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый тип файла.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")

    return {"output_path": output_path}
