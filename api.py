from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()


# ── REQUEST MODEL ──
class DataIssues(BaseModel):
    issues: List[str]


# ── HOME ──
@app.get("/")
def home():
    return {"message": "Smart Cleaning API Running"}


# ── MAIN ANALYZE ENDPOINT ──
@app.post("/analyze")
def analyze_data(data: DataIssues):

    recommendations = []

    # ── PROCESS EACH ISSUE ──
    for issue in data.issues:

        issue_lower = issue.lower()

        # ── MISSING VALUES ──
        if "missing" in issue_lower:

            recommendations.append({
                "title": "Fill Missing Numeric Values",
                "description": "Fill missing numeric columns using mean/median.",
                "action": "fill_missing_mean",
                "severity": "medium",
                "auto_applicable": True
            })

            recommendations.append({
                "title": "Fill Missing Text Values",
                "description": "Fill missing categorical values using mode (most frequent value).",
                "action": "fill_missing_mode",
                "severity": "medium",
                "auto_applicable": True
            })

        # ── DUPLICATES ──
        if "duplicate" in issue_lower:

            recommendations.append({
                "title": "Remove Duplicate Rows",
                "description": "Duplicate rows reduce data quality and bias analysis.",
                "action": "remove_duplicates",
                "severity": "high",
                "auto_applicable": True
            })

        # ── DATATYPE ISSUES ──
        if "datatype" in issue_lower or "text" in issue_lower:

            recommendations.append({
                "title": "Fix Data Types",
                "description": "Convert numeric strings into proper numeric datatype.",
                "action": "fix_dtypes",
                "severity": "medium",
                "auto_applicable": True
            })

        # ── OUTLIERS ──
        if "outlier" in issue_lower:

            recommendations.append({
                "title": "Handle Outliers",
                "description": "Outliers can distort analysis results. Review carefully.",
                "action": "handle_outliers",
                "severity": "low",
                "auto_applicable": False
            })

    # ── REMOVE DUPLICATES IN ACTIONS ──
    unique_recommendations = {}
    for rec in recommendations:
        unique_recommendations[rec["action"]] = rec

    final_output = list(unique_recommendations.values())

    # ── RESPONSE ──
    return {
        "recommendations": final_output,
        "total_actions": len(final_output)
    }
