# Healthcare Backend System

This repository contains the implementation of a **Healthcare Backend** using **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **JWT authentication**. The API supports user registration/login, patient management, doctor management, and patient–doctor assignments.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Getting Started](#getting-started)
   - [Clone the repo](#clone-the-repo)
   - [Create a virtual environment](#create-a-virtual-environment)
   - [Install dependencies](#install-dependencies)
   - [Configure environment variables](#configure-environment-variables)
   - [Database setup & migrations](#database-setup--migrations)
   - [Run the development server](#run-the-development-server)
5. [Project Structure](#project-structure)
6. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication)
   - [Patients](#patients)
   - [Doctors](#doctors)
   - [Mappings](#mappings)


---

## Features

- ✅ **User Registration & Login** with **JWT** (via `djangorestframework-simplejwt`).
- ✅ **Patient CRUD**: create, read, update, delete operations secured per-user.
- ✅ **Doctor CRUD**: create, read, update, delete operations (authenticated users).
- ✅ **Patient–Doctor Mapping**: assign doctors to patients, list, and remove assignments.
- ✅ **Validation & Error Handling**: unique email/license checks, owner permissions, friendly error messages.
- ✅ **Environment-driven Configuration**: secrets and DB credentials via `.env`.

## Tech Stack

- **Python 3.12**
- **Django 4.x**
- **Django REST Framework**
- **PostgreSQL**
- **djangorestframework-simplejwt** for JWT auth
- **python-dotenv** for environment variables

## Prerequisites

- Python 3.12 or later
- PostgreSQL (and `psycopg2` installed)
- Git

## Getting Started

Follow these steps to spin up the backend locally:

### Clone the repo

```bash
git clone https://github.com/Dhiraj274/healthcare_backend.git
cd healthcare_backend
```

### Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate     # Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root (next to `manage.py`) with:

```dotenv
DJANGO_SECRET_KEY=<your-secret-key>
DEBUG=True
DB_NAME=<postgres_db_name>
DB_USER=<postgres_user>
DB_PASSWORD=<postgres_password>
DB_HOST=localhost
DB_PORT=5432
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database setup & migrations

1. Create the Postgres database:
   ```bash
   psql -U <postgres_user>
   CREATE DATABASE <postgres_db_name>;
   \q
   ```
2. Run Django migrations:
   ```bash
   python manage.py migrate
   ```

### Run the development server

```bash
python manage.py runserver
```

The API will now be available at `http://127.0.0.1:8000/`.

---

## Project Structure

```
healthcare_backend/
├── project/           # Django project settings & URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py, asgi.py
├── api/               # Core DRF app
│   ├── models.py      # Patient, Doctor, Mapping
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py       # (Add your tests here)
├── manage.py
├── requirements.txt
└── .env.example       # Sample env template
```

---

## API Endpoints

All endpoints (unless noted) require an **Authorization** header with a Bearer JWT token:

```
Authorization: Bearer <access_token>
```

### Authentication

| Method | Endpoint                  | Description             |
| ------ | ------------------------- | ----------------------- |
| POST   | `/api/auth/register/`     | User sign-up            |
| POST   | `/api/auth/login/`        | Obtain JWT tokens       |
| POST   | `/api/auth/token/refresh/`| Refresh access token    |

#### Register Example

```json
POST /api/auth/register/
{
  "email": "alice@example.com",
  "password": "StrongPass123",
  "password2": "StrongPass123",
  "first_name": "Alice",
  "last_name": "Smith"
}
```

#### Login Example

```json
POST /api/auth/login/
{
  "username": "alice@example.com", # username is same as email
  "password": "StrongPass123"
}
```

---

### Patients

| Method | Endpoint                  | Description                        |
| ------ | ------------------------- | ---------------------------------- |
| GET    | `/api/patients/`          | List your patients                 |
| POST   | `/api/patients/`          | Create a new patient               |
| GET    | `/api/patients/{id}/`     | Retrieve a single patient detail   |
| PUT    | `/api/patients/{id}/`     | Update patient info                |
| DELETE | `/api/patients/{id}/`     | Delete a patient                   |

### Doctors

| Method | Endpoint                  | Description                        |
| ------ | ------------------------- | ---------------------------------- |
| GET    | `/api/doctors/`           | List all doctors                   |
| POST   | `/api/doctors/`           | Add a new doctor                   |
| GET    | `/api/doctors/{id}/`      | Retrieve a single doctor           |
| PUT    | `/api/doctors/{id}/`      | Update doctor info                 |
| DELETE | `/api/doctors/{id}/`      | Delete a doctor                    |

### Patient–Doctor Mappings

| Method | Endpoint                            | Description                     |
| ------ | ----------------------------------- | ------------------------------- |
| GET    | `/api/mappings/`                    | List all your mappings          |
| POST   | `/api/mappings/`                    | Assign a doctor to a patient    |
| GET    | `/api/mappings/{mapping_id}/`       | Retrieve a single mapping       |
| DELETE | `/api/mappings/{mapping_id}/`       | Remove an assignment            |
| GET    | `/api/mappings/by-patient/{id}/`    | List doctors for a patient      |

