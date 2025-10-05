
# Roadmap & Hardening

## Short Term
- JWT auth and API keys
- Rate limiting with Redis
- Request/response audit logs
- Postgres storage (Timescale optional)
- Prometheus metrics + Grafana dashboard
- OTX/VirusTotal enrichment

## Medium Term
- Risk model calibration with historical distributions
- Device fingerprinting and session anomaly detection
- GeoIP provider and velocity limits by country
- CICD: docker scan, bandit, safety, secret scanning

## Long Term
- Streaming pipeline (Kafka) + Flink jobs
- Real-time rule management (UI) and AB testing
- Hybrid detection: rules + ML (XGBoost/LightGBM)
