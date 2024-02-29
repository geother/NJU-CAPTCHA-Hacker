from fastapi import FastAPI, File, UploadFile
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Visit the endpoint: /api/extract_code to perform decode the CAPTCHA."}

@app.post("/api/extract_code")
def extract_text(image: UploadFile = File(...)):
    print("Images Uploaded:", image.filename)
    print(image.filename)
    image_strem = image.file.read()
    code = ocr.classification(image_strem)
    print("Code:", code)
    return {"code": code}
 