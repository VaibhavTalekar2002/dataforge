# ─────────────────────────────
# In-memory storage layer
# ─────────────────────────────

datasets = {}

jobs = {}

audit_logs = []


# ─────────────────────────────
# OPTIONAL: standard log format helper (VERY USEFUL)
# ─────────────────────────────
def create_audit_log(dataset_id, job_id, actions, before, after):
    return {
        "dataset_id": dataset_id,
        "job_id": job_id,
        "actions": actions,
        "before": {
            "rows": before.get("rows"),
            "missing": before.get("missing")
        },
        "after": {
            "rows": after.get("rows"),
            "missing": after.get("missing")
        },
        "timestamp": None  # can be filled in app.py
    }
