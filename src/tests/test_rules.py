
from securebank.rules import score_transaction

def test_high_amount_scores_higher():
    score, reasons, flags = score_transaction({
        "txn_id":"1","user_id":"u","amount":10000,"mcc":4829,"ip":"8.8.8.8","country":"US"
    })
    assert score >= 25
    assert "HIGH_AMOUNT" in reasons

def test_low_risk_baseline():
    score, reasons, flags = score_transaction({
        "txn_id":"2","user_id":"u2","amount":10,"mcc":1234,"ip":"1.1.1.1","country":"US"
    })
    assert score >= 0
    assert "LOW_RISK_BASELINE" in reasons
