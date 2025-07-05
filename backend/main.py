from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.post("/analyze")
def analyze_code():
    # Placeholder for future static analysis
    return {"status": "analyze endpoint hit"}
