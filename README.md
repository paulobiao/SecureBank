# SecureBank – Zero-Trust Threat Detection Study (Banking Simulation)

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-ready-success.svg)
![Docker](https://img.shields.io/badge/Docker-supported-2496ED.svg)
![Open Source](https://img.shields.io/badge/Open--Source-Yes-brightgreen.svg)

> **Note:** This is an educational open-source project — a technical study of
> zero-trust and threat-detection concepts applied to **simulated** banking
> environments (FastAPI, Python, Docker). It is not a commercial product and
> has not been deployed in any production environment.

SecureBank is an open-source study project exploring a financially-aware
zero-trust architecture for banking systems, using synthetic data and
simulation.

---

## 🚀 Gemini 3 Hackathon – SecureBank Copilot

This repository powers **SecureBank Copilot**, an AI-driven decision-support
prototype created for the **Gemini 3 Hackathon**.

The project explores how generative AI can translate simulated cyber incidents
into quantified financial-loss estimates, regulatory exposure, and executive
decision paths.

### 🎥 Demo
https://youtu.be/lFNKE2sfnkI

### 🌐 Project page
https://www.biaotech.dev/securebank-copilot

---

## 📄 Companion Preprint (self-archived)

**SecureBank: A Financially-Aware Zero-Trust Architecture for High-Assurance
Banking Systems** — self-archived preprint (Zenodo, not peer-reviewed).

- **DOI:** https://doi.org/10.5281/zenodo.18071268
- **Author:** Paulo Fernandes Biao

This repository contains the companion implementation and simulation artifacts
described in the preprint.

---

## 🎯 Objective

Explore detection of suspicious financial activity and identity abuse in
**simulated banking and fintech environments**:

- Real-time risk evaluation via APIs
- Explainable scoring with explicit reason codes
- Quantitative exploration through Monte Carlo simulation

---

## ✨ Key Features

- FastAPI-based transaction scoring API
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

## 🧪 Statistical Simulation

The project includes a Monte Carlo–based simulation module with hypothesis
testing, effect-size analysis, and visualizations, using synthetic data.

See: `sim/securebank-sim/README.md`
