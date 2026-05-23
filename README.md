# Interview Prep Tracker

A comprehensive web application designed to help students and professionals prepare for job interviews through structured mock interviews, coding practice tracking, resume analysis, and personalized recommendations.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Models](#database-models)
- [API Routes](#api-routes)
- [Core Services](#core-services)
- [User Roles & Permissions](#user-roles--permissions)
- [Features in Detail](#features-in-detail)
---

## Overview

**Interview Prep Tracker** is a full-stack Flask web application built to bridge the gap between interview preparation resources and practical execution. Whether you're preparing for FAANG interviews or role-specific technical assessments, this platform provides:

- Mock interview scheduling and execution
- Real-time interview feedback and analytics
- Coding problem tracking across multiple platforms
- Resume analysis and skill extraction
- Personalized role recommendations
- Comprehensive dashboard with performance metrics
- Admin panel for question management
# Smart Job Portal

A lightweight Flask application for managing job postings, candidate resumes, mock interviews, feedback, and role recommendations. This README is generated from the codebase and documents exact setup, routes, models and operational steps present in the repository.

## Table of contents

- [Quickstart](#quickstart)
- [Prerequisites](#prerequisites)
- [Environment & Configuration](#environment--configuration)
- [Run the app](#run-the-app)
- [Seeding data & default admin](#seeding-data--default-admin)
- [Database Collections](#database-collections)
- [Models (brief)](#models-brief)
- [Blueprints & Routes](#blueprints--routes)
- [Core Services](#core-services)
- [File uploads](#file-uploads)
- [Development notes](#development-notes)

---

## Quickstart

1. Clone the repository and change into it:

```bash
git clone <repo-url>
cd SmartJobPortal
```

2. Create and activate a Python virtual environment:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables (see below) and run:

```bash
python run.py
```

The development server listens on port 5000 by default.

---

## Prerequisites

- Python 3.7+
- MongoDB (local or Atlas)
- pip

---

## Environment & Configuration

Create a `.env` file in the project root (optional). The code reads environment variables via `python-dotenv` and uses sensible defaults.

Recommended variables (examples):

```env
# Optional: `FLASK_APP` is not required to run, `run.py` starts the app directly
SECRET_KEY=change-this-in-production
MONGO_URI=mongodb://localhost:27017/smart_job_portal
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216
```

Key configuration values live in [app/config.py](app/config.py) and default values are set there. Important constants include `INTERVIEW_TYPES`, `SKILL_CATEGORIES`, and `JOB_ROLE_MAPPINGS`.

---

## Run the app

To start the development server (debug mode enabled in code):

```bash
python run.py
```

Open http://localhost:5000 in your browser.

Notes:
- The app factory is in [app/__init__.py](app/__init__.py). It creates the upload folder and seeds an admin account if none exists.
- The default upload folder is `app/static/uploads` (created automatically).

---

## Seeding data & default admin

- The app ensures a default admin account exists on startup: email `admin@jobportal.in` with password `Admin@123` (created only if no admin exists).
- To seed the sample question bank run the seeder script:

```bash
python seed_data.py
```

This inserts many example MCQ questions into the `questions` collection.

---

## Database Collections

The code uses the following MongoDB collections:

- `users` — user accounts (candidates, employers, admin)
- `questions` — question bank for interviews
- `mock_interviews` — scheduled / completed mock interviews
- `resumes` — parsed resume records
- `feedback` — generated interview feedback
- `recommendations` — role / course / skill recommendations
- `job_postings` — employer job postings
- `applications` — candidate applications to jobs

You can inspect collection usage by reading the model files in [app/models/](app/models).

---

## Models (brief)

The repository implements several thin model wrappers around MongoDB documents. See files under [app/models/](app/models/).

- `User` ([app/models/user.py](app/models/user.py)) — fields: name, email, password_hash, role, preferred_roles, profile_summary, avatar_color, is_active, is_approved, company_* fields for employers.
- `Question` ([app/models/question.py](app/models/question.py)) — MCQ fields, options, correct_answer, difficulty, category, tags, points.
- `MockInterview` ([app/models/interview.py](app/models/interview.py)) — user_id, job_id, interview_type, questions list, answers map, score, status.
- `Resume` ([app/models/resume.py](app/models/resume.py)) — parsed resume info (skills, experience_years, education, certifications, resume_score, raw_text).
- `Feedback` ([app/models/feedback.py](app/models/feedback.py)) — feedback summary, weak/strong topics, topic_scores.
- `Recommendation` ([app/models/recommendation.py](app/models/recommendation.py)) — recommended roles / courses / skills and confidence_scores.
- `JobPosting` ([app/models/job_posting.py](app/models/job_posting.py)) — employer_id, title, required_skills, min_resume_score, num_questions, difficulty, is_active.
- `Application` ([app/models/application.py](app/models/application.py)) — candidate/job/employer links, resume_score, interview_id, status.

---

## Blueprints & Routes

Blueprints are registered in [app/__init__.py](app/__init__.py). Major route groups:

- `auth` (Authentication):
   - `GET/POST /login` — login form
   - `GET/POST /register` — candidate registration
   - `GET/POST /register/employer` — employer registration (pending admin approval)
   - `GET /logout` — logout

- `main` (Public pages): `/`, `/about`, `/features` — templates in `templates/`

- `dashboard` — redirects users to role-appropriate dashboards (`/dashboard`)

- `candidate` (prefix `/candidate`) — candidate features including resume upload, jobs listing, applying, starting interviews, interview session and results.

- `employer` (prefix `/employer`) — employer features: post jobs, view applicants, schedule interviews for applicants.

- `admin` (prefix `/admin`) — admin dashboard, approve employers, manage users and jobs.

- `resume` (prefix `/resume`) — upload and analyze resumes (PDF/DOCX).

- `interview` (prefix `/interview`) — schedule, start and view interview sessions.

- `api` (prefix `/api`) — JSON endpoints used by frontend:
   - `GET /api/analytics` — returns user analytics
   - `GET /api/chart-data` — data for charts
   - `GET /api/interviews` — list of interviews (filter by status)
   - `GET /api/question/<id>` — question payload (omits correct answer)

Refer to the route implementations in [app/routes/](app/routes) for exact behavior and required parameters.

---

## Core Services

Services implement business logic and are located in [app/services/](app/services).

- `ResumeParserService` ([app/services/resume_parser.py](app/services/resume_parser.py))
   - Extracts text from PDF/DOCX, finds skills/education/certifications, estimates experience, computes resume score and recommends skills.

- `QuestionService` ([app/services/question_service.py](app/services/question_service.py))
   - Selects questions for interviews by category / tags / difficulty and evaluates MCQ answers to produce a percentage score.

- `FeedbackService` ([app/services/feedback_service.py](app/services/feedback_service.py))
   - Produces readable feedback summaries, identifies weak/strong topics and creates improvement suggestions.

- `RecommendationService` ([app/services/recommendation_service.py](app/services/recommendation_service.py))
   - Matches resume skills and interview performance to job roles and suggests courses / skills.

- `AnalyticsService` ([app/services/analytics_service.py](app/services/analytics_service.py))
   - Aggregates interview history and feedback into dashboards and chart-ready payloads.

---

## File uploads

- Resume uploads: only `pdf` and `docx` (checked by routes). Max size from environment `MAX_CONTENT_LENGTH` (default 16MB).
- Employer logos / images: allowed types in routes include `png, jpg, jpeg, gif, webp`.
- Uploads are stored in `app/static/uploads` by default; the folder is created by the application on startup.

---

## Development notes

- The project uses `Flask-Login` for session management and `werkzeug` for password hashing.
- The default admin account (`admin@jobportal.in` / `Admin@123`) is created automatically if missing. You can change defaults in [app/__init__.py](app/__init__.py) or create your own user via the UI.
- Seed the question bank with `python seed_data.py` (this clears and repopulates the `questions` collection).
- `requirements.txt` lists dependencies; `spacy` is present but resume parsing currently relies on `PyPDF2` and `python-docx` in code.

---

## Where to look in the code

- App factory and blueprint registration: [app/__init__.py](app/__init__.py)
- Routes: [app/routes/](app/routes)
- Models: [app/models/](app/models)
- Services: [app/services/](app/services)

---

If you'd like, I can:

- Run the seed script and start the server for you locally
- Add example environment `.env.example`
- Extend the README with deployment steps (Docker, Gunicorn, nginx)

Tell me which of those you'd like next.
