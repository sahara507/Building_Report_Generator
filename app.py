#print("AI_Report_Generator")
from fastapi import FastAPI, UploadFile, File
from ingestion import load_file
from report_generator import generate_report
from web_search import search_web
import os


app = FastAPI(
    title="_BUILDING_REPORT_GENERATOR_",
    description="Generates the reports using Gen_AI",
)


# Create uploads folder if it doesn't exist
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "Automated Report Generator is running"
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    # Create file path
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Load uploaded CSV/Excel file
    data = load_file(file_path)

    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
        "data": data.to_dict(orient="records")
    }


@app.get("/web-search")
def web_search(query: str):

    # Call Tavily search function
    results = search_web(query)

    return {
        "query": query,
        "results": results
    }
