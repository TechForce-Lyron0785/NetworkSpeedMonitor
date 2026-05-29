# Contributing to Network Speed Monitor

## Branch Strategy
- `main` – production ready
- `develop` – integration branch (optional, but we use `main` for solo)
- Feature branches: `feature/backend-poller`, `feature/api-endpoints`, etc.

## Setup Development Environment
```bash
# Clone
git clone https://github.com/TechForce-Lyron0785/NetworkSpeedMonitor.git
cd NetworkSpeedMonitor

# Python virtual env
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install