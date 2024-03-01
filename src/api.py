from fastapi import FastAPI, File, UploadFile
import ddddocr
from datetime import datetime
import json

app = FastAPI()
ocr = ddddocr.DdddOcr(show_ad=False)
total_requests = 0
today_requests = 0

MAX_REQUESTS_PER_DAY = 100
REQUESTS_FILE_PATH = "data/total_requests.json"

# Function to save total number of requests to file
def save_requests():
    with open(REQUESTS_FILE_PATH, "w") as file:
        json.dump({"total_requests": total_requests, "last_updated": datetime.now().strftime('%Y-%m-%d')}, file)

# Load total number of requests and last updated date from file if exists
try:
    with open(REQUESTS_FILE_PATH, "r") as file:
        data = json.load(file)
        total_requests = data.get("total_requests", 0)
        last_updated = datetime.strptime(data.get("last_updated", datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
except FileNotFoundError:
    last_updated = datetime.now()

# Function to update total number of requests and save to file
def update_requests():
    global total_requests, last_updated, today_requests
    current_date = datetime.now()
    if current_date.date() != last_updated.date():  # Reset counter if new day
        today_requests = 0
        last_updated = current_date
    total_requests += 1
    today_requests += 1
    if total_requests % 50 == 0:
        save_requests()

# Endpoint to extract text from image
@app.post("/api/extract_code")
def extract_text(image: UploadFile = File(...)):
    global today_requests
    try:
        if today_requests >= MAX_REQUESTS_PER_DAY:
            raise ValueError("Maximum requests limit reached for today")
        image_stream = image.file.read()
        code = ocr.classification(image_stream)
        print("Code:", code)
        update_requests()
        return {"code": code}
    except ValueError as e:
        return {"error": str(e)}

# Endpoint to get total number of requests
@app.get("/api/extract_code/total_requests")
def get_total_requests():
    return {"total_requests": total_requests}

# Endpoint to reset total number of requests (for testing purpose)
@app.post("/api/extract_code/reset_requests")
def reset_requests():
    global total_requests
    total_requests = 0
    save_requests()
    return {"message": "Total requests reset to 0"}

# Default endpoint
@app.get("/")
def home():
    return {"message": "Visit the endpoint: /api/extract_code to perform decode the CAPTCHA."}
