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


@app.get("/")
def home():
    return {
        "message": "Automated Report Generator is running"
    }
    


@app.post("/upload")
async def upload(file: UploadFile = File(...)):           # he function user kadun input ghenyasathi aahe. to upload the file..
                                                         
    os.makedirs("data", exist_ok=True)                     # Make sure data folder exists

                                                            
    file_path = f"data/{file.filename}"                     # Create file path

                                                             
    with open(file_path, "wb") as buffer:                  # Save uploaded file
        buffer.write(await file.read())

                                                            # Read the file using ingestion.py
    df = load_file(file_path)

                                                           # Generate report using report_generator.py
    report = generate_report(df)  
    return {
        "filename": file.filename,
        "message": "File uploaded succesfully...",
         "report": report
    }

@app.get("/web-search")                                     # for Web Search API
def web_search(query: str):

    # Call Tavily search function
    results = search_web(query)

    return {
        "query": query,
        "results": results
    }
