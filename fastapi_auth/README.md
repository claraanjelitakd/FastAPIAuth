# FastAPI Authentication Boilerplate

A production-ready authentication system built with FastAPI, SQLAlchemy, and Pydantic.

## Features
- **Secure Hashing**: Password storage using BCrypt.
- **JWT Auth**: Implementation of Access and Refresh tokens.
- **Email Verification**: Registration flow with email confirmation.
- **Password Reset**: Secure token-based password recovery.
- **Modern Structure**: Organized folders for core, models, schemas, and routes.
- **SQL Injection Protection**: Uses SQLAlchemy ORM.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install fastapi[all] sqlalchemy passlib[bcrypt] python-jose[cryptography] fastapi-mail pydantic-settings
   ```

2. **Configure Environment**:
   - Copy `.env.example` to `.env`.
   - Update `SECRET_KEY`, `DATABASE_URL`, and SMTP settings.
   - For Gmail, use an [App Password](https://myaccount.google.com/apppasswords).

3. **Run the Application**:
   ```bash
   cd fastapi_auth
   uvicorn app.main:app --reload
   ```

4. **API Documentation**:
   - Visit `http://localhost:8000/docs` for the interactive Swagger UI.

## Project Structure
- `app/core`: Configuration, security utilities, database setup, and mailer.
- `app/models`: SQLAlchemy database models.
- `app/schemas`: Pydantic models for data validation.
- `app/api`: API routes and dependencies.
- `app/main.py`: Application entry point.
