from fastapi import FastAPI, UploadFile
from typing import List
import csv, io

from .rules import score_transaction

app = FastAPI(title="SecureBank API")

@app.get("/")
def root():
    return {"status": "ok", "service": "SecureBank"}

@app.post("/api/v1/score")
async def score(tx: dict):
    score, reasons = score_transaction(tx)
    return {"score": score, "reasons": reasons}

@app.post("/api/v1/score/batch")
async def score_batch(file: UploadFile):
    content = await file.read()
    csv_data = csv.DictReader(io.StringIO(content.decode()))
    results = []
    for row in csv_data:
        s, r = score_transaction(row)
        results.append({"score": s, "reasons": r})
    avg = round(sum(r["score"] for r in results) / len(results), 2)
    return {"average_score": avg, "results": results}

