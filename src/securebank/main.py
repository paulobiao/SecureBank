
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .models import Transaction, ScoreResponse
from .rules import score_transaction, batch_score_dataframe
import pandas as pd
import io

app = FastAPI(title="SecureBank Threat Detection API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/score", response_model=ScoreResponse)
def score(txn: Transaction):
    score, reasons, flags = score_transaction(txn.model_dump())
    return ScoreResponse(score=score, reasons=reasons, flags=flags)

@app.post("/api/v1/score/batch")
async def score_batch(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    results = batch_score_dataframe(df)
    return results
