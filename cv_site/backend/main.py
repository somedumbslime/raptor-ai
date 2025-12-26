from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    Header,
    Form,
    Request,
    Depends,
    Security,
)
from fastapi.middleware.cors import CORSMiddleware
from detect_onnx import ONNXDetector
from detect_pt import PTDetector
import shutil
import uuid
import os
from fastapi.staticfiles import StaticFiles
from PIL import Image
import cv2
import time
from collections import defaultdict
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# from jose import jwt, JWTError
from dotenv import load_dotenv
import requests

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("API_AUDIENCE")
ALGORITHMS = ["RS256"]
security = HTTPBearer()


# --- JWT валидация ---
# def get_jwk():
#     jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
#     return requests.get(jwks_url).json()


# JWKS = get_jwk()


# def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     try:
#         unverified_header = jwt.get_unverified_header(token)
#         rsa_key = {}
#         for key in JWKS["keys"]:
#             if key["kid"] == unverified_header["kid"]:
#                 rsa_key = {
#                     "kty": key["kty"],
#                     "kid": key["kid"],
#                     "use": key["use"],
#                     "n": key["n"],
#                     "e": key["e"],
#                 }
#         if not rsa_key:
#             raise HTTPException(401, detail="Invalid token header")
#         payload = jwt.decode(
#             token,
#             rsa_key,
#             algorithms=ALGORITHMS,
#             audience=API_AUDIENCE,
#             issuer=f"https://{AUTH0_DOMAIN}/",
#         )
#         return payload
#     except JWTError:
#         raise HTTPException(401, detail="Invalid token")


# --- Rate limiting (in-memory, для демонстрации) ---
RATE_LIMIT = 30  # запросов
RATE_PERIOD = 60  # секунд
client_requests = defaultdict(list)


def check_rate_limit(request: Request):
    ip = request.client.host
    now = time.time()
    client_requests[ip] = [t for t in client_requests[ip] if now - t < RATE_PERIOD]
    if len(client_requests[ip]) >= RATE_LIMIT:
        raise HTTPException(429, detail="Слишком много запросов. Попробуйте позже.")
    client_requests[ip].append(now)


# --- CORS ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ваш-домен",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаём папки, если их нет
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Маппинг моделей (заглушка)
MODEL_PATHS = {
    "nano": "models/model_nano.pt",
    "small": "models/model_5783f.pt",
    "medium": "models/model_medium.pt",
    "large": "models/model_large.pt",
}

SUPPORTED_IMAGE_EXTS = {"jpg", "jpeg", "png"}
SUPPORTED_VIDEO_EXTS = {"mp4", "avi", "mov", "mkv"}

# Инициализация PTDetector один раз при запуске
PT_MODELS = {
    "small": PTDetector("models/model_5783f.pt"),
    # Можно добавить другие модели, если потребуется
}

# Заглушка: классы и bbox
DEMO_DETECTIONS = [
    {"class": "tank", "confidence": 0.92, "bbox": [100, 120, 80, 60]},
    {"class": "apc", "confidence": 0.85, "bbox": [200, 220, 60, 40]},
]


def filter_boxes_by_confidence(boxes, confidence):
    """
    Фильтрует боксы по порогу confidence (best practice для postprocess).
    :param boxes: Boxes object (ultralytics)
    :param confidence: float, threshold
    :return: индексы подходящих боксов
    """
    import torch

    if hasattr(boxes, "conf"):
        confs = boxes.conf
        if isinstance(confs, torch.Tensor):
            indices = (confs >= confidence).nonzero(as_tuple=True)[0].tolist()
        else:
            indices = [i for i, c in enumerate(confs) if c >= confidence]
        return indices
    return list(range(len(boxes)))


# Старый эндпоинт для совместимости
@app.post("/predict/")
async def predict(request: Request, file: UploadFile = File(...)):
    check_rate_limit(request)
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if not ext:
        raise HTTPException(
            status_code=400, detail="Файл без расширения не поддерживается."
        )
    if ext not in SUPPORTED_IMAGE_EXTS and ext not in SUPPORTED_VIDEO_EXTS:
        raise HTTPException(status_code=400, detail=f"Формат .{ext} не поддерживается.")

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Размер файла превышает 50 МБ.",
        )

    filename = f"uploads/{uuid.uuid4()}.{ext}"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Проверка содержимого файла
    try:
        if ext in SUPPORTED_IMAGE_EXTS:
            img = Image.open(filename)
            img.verify()
        elif ext in SUPPORTED_VIDEO_EXTS:
            cap = cv2.VideoCapture(filename)
            if not cap.isOpened():
                raise Exception("Некорректный видеофайл")
            cap.release()
    except Exception:
        os.remove(filename)
        raise HTTPException(400, detail="Некорректный или повреждённый файл.")

    output_path = f"outputs/{uuid.uuid4()}.{ext}"
    shutil.copyfile(filename, output_path)

    return {"output_path": output_path}


# Новый эндпоинт для изображений
@app.post("/infer-image")
async def infer_image(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form("small"),
):
    check_rate_limit(request)
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in SUPPORTED_IMAGE_EXTS:
        raise HTTPException(
            status_code=400, detail="Только изображения поддерживаются."
        )
    if model not in PT_MODELS:
        raise HTTPException(status_code=400, detail="Модель не поддерживается.")
    filename = f"uploads/{uuid.uuid4()}.{ext}"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Проверка содержимого файла
    try:
        img = Image.open(filename)
        img.verify()
    except Exception:
        os.remove(filename)
        raise HTTPException(
            400, detail="Некорректный или повреждённый файл изображения."
        )
    output_path = f"outputs/{uuid.uuid4()}.{ext}"
    detector = PT_MODELS[model]
    try:
        results = detector.model.predict(
            source=filename,
            conf=detector.confidence,
            iou=detector.iou,
            device=detector.device,
        )
        shutil.copyfile(filename, output_path)
        dets = []
        boxes = results[0].boxes
        names = detector.model.names
        indices = filter_boxes_by_confidence(boxes, detector.confidence)
        for i in indices:
            xyxy = boxes.xyxy[i].tolist()
            conf = float(boxes.conf[i])
            cls_idx = int(boxes.cls[i])
            class_name = names[cls_idx] if cls_idx < len(names) else str(cls_idx)
            x, y, w, h = (
                int(xyxy[0]),
                int(xyxy[1]),
                int(xyxy[2] - xyxy[0]),
                int(xyxy[3] - xyxy[1]),
            )
            dets.append(
                {
                    "class": class_name,
                    "confidence": conf,
                    "bbox": [x, y, w, h],
                }
            )
        return {"filename": os.path.basename(output_path), "detections": dets}
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка инференса.")


# Новый эндпоинт для видео (только "авторизованным")
@app.post("/infer-video")
async def infer_video(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form("small"),
    confidence: float = Form(0.32), # Добавьте это
    iou: float = Form(0.5)          # Добавьте это
    # user=Depends(verify_jwt),
):
    check_rate_limit(request)
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in SUPPORTED_VIDEO_EXTS:
        raise HTTPException(status_code=400, detail="Только видео поддерживается.")
    if model not in PT_MODELS:
        raise HTTPException(status_code=400, detail="Модель не поддерживается.")
    filename = f"uploads/{uuid.uuid4()}.{ext}"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Проверка содержимого файла
    try:
        cap = cv2.VideoCapture(filename)
        if not cap.isOpened():
            os.remove(filename)
            raise Exception("Некорректный видеофайл")
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    except Exception:
        if os.path.exists(filename):
            os.remove(filename)
        raise HTTPException(400, detail="Некорректный или повреждённый видеофайл.")
    output_path = f"outputs/{uuid.uuid4()}.{ext}"
    shutil.copyfile(filename, output_path)
    detector = PT_MODELS[model]
    detections_by_frame = []
    try:
        cap = cv2.VideoCapture(filename)
        frame_idx = 0
        max_frames = (
            300  # Ограничение на количество кадров (например, 10 сек при 30 fps)
        )
        while True:
            ret, frame = cap.read()
            if not ret or frame_idx >= max_frames:
                break
            temp_img_path = f"uploads/temp_{uuid.uuid4()}.jpg"
            cv2.imwrite(temp_img_path, frame)
            results = detector.model.predict(
                source=temp_img_path,
                conf=detector.confidence,
                iou=detector.iou,
                device=detector.device,
            )
            frame_dets = []
            boxes = results[0].boxes
            names = detector.model.names
            indices = filter_boxes_by_confidence(boxes, detector.confidence)
            for i in indices:
                xyxy = boxes.xyxy[i].tolist()
                conf = float(boxes.conf[i])
                cls_idx = int(boxes.cls[i])
                class_name = names[cls_idx] if cls_idx < len(names) else str(cls_idx)
                x, y, w, h = (
                    int(xyxy[0]),
                    int(xyxy[1]),
                    int(xyxy[2] - xyxy[0]),
                    int(xyxy[3] - xyxy[1]),
                )
                frame_dets.append(
                    {
                        "class": class_name,
                        "confidence": conf,
                        "bbox": [x, y, w, h],
                    }
                )
            detections_by_frame.append({"frame": frame_idx, "detections": frame_dets})
            os.remove(temp_img_path)
            frame_idx += 1
        cap.release()
        if os.path.exists(filename):
            os.remove(filename)
        return {
            "filename": os.path.basename(output_path),
            "detections": detections_by_frame,
        }
    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        raise HTTPException(status_code=500, detail=f"Ошибка инференса: {str(e)}")
