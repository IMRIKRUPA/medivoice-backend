# MediVoice Backend API

Flask-based backend for MediVoice application. Handles authentication, API requests, and data storage.

## Tech Stack
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- JWT
- Gunicorn

## Setup

```bash
pip install -r requirements.txt
python app.py

Runs on:

http://localhost:5000
Deployment (Render)
Build Command
pip install -r requirements.txt
Start Command
gunicorn app:app
Environment Variables
SECRET_KEY=your_secret_key
FLASK_DEBUG=false
TOKEN_EXPIRY_HOURS=24
AUTO_SEED=true
