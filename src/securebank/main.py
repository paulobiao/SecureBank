from fastapi import UploadFile, File
import pandas as pd
from io import StringIO

@app.post("/api/v1/score/batch")
async def score_batch(file: UploadFile = File(...)):
    """
    Recebe um CSV com colunas: user_id,amount,merchant,ip,device_id
    Retorna scores por linha e estatísticas agregadas.
    """
    content = (await file.read()).decode("utf-8")
    df = pd.read_csv(StringIO(content))
    results = []
    total = 0
    high_risk = 0

    for _, row in df.iterrows():
        s = {
            "user_id": str(row.get("user_id")),
            "amount": float(row.get("amount", 0)),
            "merchant": str(row.get("merchant", "")),
            "ip": str(row.get("ip", "")),
            "device_id": str(row.get("device_id", "")),
        }
        score, reasons = 10, []
        if s["amount"] > 500:
            score += 50; reasons.append("High amount")
        if s["merchant"].upper() == "ELC":
            score += 20; reasons.append("Electronics purchase")
        if "198.51" in s["ip"]:
            score += 10; reasons.append("Known suspicious IP range")

        score = min(score, 100)
        results.append({"user_id": s["user_id"], "score": score, "reasons": reasons})
        total += 1
        if score > 60: high_risk += 1

    return {
        "count": total,
        "high_risk_ratio": (high_risk / total) if total else 0,
        "items": results
    }
