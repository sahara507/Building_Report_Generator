#print("AI_Report_Generator")
from fastapi import FastAPI, UploadFile, File


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
    return {
        "filename": file.filename,
        "message": "File uploaded succesfully..."
    }