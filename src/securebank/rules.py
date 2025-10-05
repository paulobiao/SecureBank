
from typing import Dict, Tuple, List, Any
import pandas as pd
import os

BLOCKLIST_PATH = os.environ.get("BLOCKLIST_PATH", "/data/threat_intel_blocklist.txt")

# Simple in-memory config
HIGH_RISK_MCC = {4829, 6051, 7995, 5967}  # money transfer, quasi-cash, adult, subscriptions

def load_blocklist() -> set:
    items = set()
    try:
        with open(BLOCKLIST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    items.add(line.lower())
    except FileNotFoundError:
        pass
    return items

BLOCKLIST = load_blocklist()

def score_transaction(txn: Dict[str, Any]) -> Tuple[int, List[str], Dict[str, bool]]:
    score = 0
    reasons: List[str] = []
    flags: Dict[str, bool] = {}

    amount = float(txn.get("amount", 0.0))
    mcc = txn.get("mcc")
    ip = (txn.get("ip") or "").lower()
    user_id = (txn.get("user_id") or "").lower()
    device_id = (txn.get("device_id") or "").lower()
    country = (txn.get("country") or "").upper()

    # Rule 1: High amount
    if amount >= 5000:
        score += 25
        reasons.append("HIGH_AMOUNT")
        flags["high_amount"] = True

    # Rule 2: High-risk MCC
    if mcc in HIGH_RISK_MCC:
        score += 20
        reasons.append("HIGH_RISK_MCC")
        flags["high_risk_mcc"] = True

    # Rule 3: Blocklist hit (ip/user/device)
    if any(x in BLOCKLIST for x in [ip, user_id, device_id] if x):
        score += 30
        reasons.append("BLOCKLIST_HIT")
        flags["blocklist_hit"] = True

    # Rule 4: Foreign country (example heuristic)
    if country and country not in {"US", "USA"}:
        score += 10
        reasons.append("FOREIGN_COUNTRY")
        flags["foreign_country"] = True

    # Normalize score
    score = min(score, 100)
    if score == 0:
        reasons.append("LOW_RISK_BASELINE")

    return score, reasons, flags

def batch_score_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    results = []
    for _, row in df.iterrows():
        s, r, f = score_transaction(row.to_dict())
        results.append({"txn_id": row.get("txn_id"), "score": s, "reasons": r, "flags": f})
    out = {
        "count": len(results),
        "summary": {
            "avg_score": float(pd.Series([x["score"] for x in results]).mean()) if results else 0.0,
            "hi_risk": sum(1 for x in results if x["score"] >= 50),
        },
        "results": results,
    }
    return out
