# Contributing to SecureBank™

Contribuições são bem-vindas! Para manter o projeto organizado:

## Fluxo
1. Faça um **fork** do repositório  
2. Crie uma **branch**: `git checkout -b feat/nome-da-feature`  
3. Commit claro: `feat: add velocity rule`  
4. Abra um **Pull Request** com descrição do que mudou  

## Padrão de código
- Python 3.11+
- Formatação: PEP8  
- Testes: `pytest -q`  
- Escreva docstrings curtas nas funções públicas  

## Como rodar localmente
```bash
pip install -r requirements.txt
uvicorn src.securebank.main:app --reload --port 8000
# docs: http://localhost:8000/docs
