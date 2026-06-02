from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from recommendation_engine import analyze_issues

app = FastAPI()

class DataIssues(BaseModel):
    issues: List[str]

@app.get("/")
def home():
    return {"message": "Smart Cleaning API Running"}

@app.post("/analyze")
def analyze_data(data: DataIssues):

    recommendations = analyze_issues(data.issues)

    return {
        "recommendations": recommendations,
        "total_actions": len(recommendations)
    }