# SecureBank™ — Financially-Aware Zero-Trust Threat Detection Framework

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-ready-success.svg)
![Docker](https://img.shields.io/badge/Docker-supported-2496ED.svg)
![Open Source](https://img.shields.io/badge/Open--Source-Yes-brightgreen.svg)

SecureBank™ is an open-source cybersecurity research and engineering framework demonstrating **financially-aware Zero Trust threat detection** through secure API design, explainable risk scoring, and reproducible simulation-based validation.

This repository serves as **public research evidence**, **open-source contribution**, and **portfolio-grade implementation** aligned with academic dissemination and U.S. immigration evidentiary standards (EB2-NIW / EB1).

---

## 📄 Academic Publication (Preprint)

**SecureBank™: A Financially-Aware Zero-Trust Architecture for High-Assurance Banking Systems**

- **DOI:** https://doi.org/10.5281/zenodo.18071268  
- **Version:** v1.0  
- **Author:** Paulo Fernandes Biao  
- **Indexed in:** OpenAIRE (Zenodo)

This repository contains the **companion implementation and simulation artifacts** supporting the paper’s methodology, metrics, and experimental validation.

---

## 🎯 Objective

Detect suspicious financial activity and identity abuse in **simulated banking and fintech environments**, providing:

- Real-time risk evaluation via secure APIs  
- Explainable scoring with explicit reason codes  
- Quantitative validation through Monte Carlo simulation  
- Architecture suitable for academic review and expert evaluation  

---

## ✨ Key Features

- FastAPI-based secure transaction scoring API  
- Rule-based threat detection:
  - Velocity anomalies  
  - Geo-IP changes  
  - Device mismatches  
  - High-risk transaction patterns  
  - Threat intelligence blocklists  
- Explainable output (score + reasons + flags)  
- Batch CSV evaluation for offline analysis  
- Reproducible Monte Carlo simulation module  
- Dockerized execution environment  
- MIT open-source license  

---

## 🏗️ System Architecture

```mermaid
flowchart LR
  A["Client / Ingest"] -->|/api/v1/score| B["FastAPI Application"]
  B --> C["Rule Engine (rules.py)"]
  B --> D["Threat Intelligence (Blocklists)"]
  B --> E["Data Storage (CSV / SQLite)"]
  B --> F["Monitoring (Prometheus / Grafana - optional)"]
```
```
docker compose up --build
```

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn securebank.main:app --reload --port 8000
```
```
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{
        "user_id": "u001",
        "amount": 999.99,
        "merchant": "ELC",
        "ip": "198.51.100.20",
        "device_id": "dev001"
      }'
```

```
{
  "score": 80,
  "reasons": ["High amount", "Suspicious IP range"],
  "flags": { "high_risk": true }
}
```

```
pytest -q
```

```
src/
  securebank/
    main.py
    rules.py
    models.py
    utils.py
tests/
  test_rules.py
data/
  sample_transactions.csv
  threat_intel_blocklist.txt
sim/
  securebank-sim/
docs/
  roadmap.md
.github/workflows/
Dockerfile
docker-compose.yml
requirements.txt
LICENSE
README.md
```

```
cd sim/securebank-sim
python runner.py
```
