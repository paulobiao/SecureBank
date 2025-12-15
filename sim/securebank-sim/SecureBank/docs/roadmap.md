# 🧭 Roadmap — SecureBank™

## v0.1.0 (atual)
- [x] API FastAPI base e health-check
- [x] Score inicial (mock) + reason codes
- [x] Estrutura de pastas (src/data/docs/tests) e Dockerfile
- [x] CI básico (pytest) no GitHub Actions

## v0.2.0
- [ ] Endpoints `/api/v1/score` e `/api/v1/score/batch` (CSV)
- [ ] Regras: velocity (freq), geo-IP change, device mismatch, MCCs de alto risco
- [ ] Threat intel: leitura de `data/threat_intel_blocklist.txt`
- [ ] Testes de unidade para regras

## v0.3.0
- [ ] Métricas Prometheus + dashboard Grafana (docker-compose)
- [ ] Persistência opcional em PostgreSQL
- [ ] Notebook de análise (docs/) com exemplo de investigação

## v1.0.0
- [ ] Publicar imagem no Docker Hub
- [ ] Documentação hospedada (Read the Docs)
- [ ] Demo pública (Render/Fly.io) com endpoint somente leitura

