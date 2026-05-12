# Next.js 15 + FastAPI + shadcn/ui Full-stack SaaS Template (2026)

This template provides a robust starting point for a modern SaaS application, integrating a high-performance FastAPI backend with a beautiful Next.js 15 App Router frontend.

## 🚀 Quick Start

Ensure you have [Docker](https://www.docker.com/) installed.

1. Clone the repository.
2. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` variables if necessary (e.g., add your `RESEND_API_KEY`).
4. Build and start the services:
   ```bash
   docker compose up --build
   ```

## 🌐 Endpoints

- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database (Postgres)**: Exposed on port `5432`

## 📦 Stack Overview

**Frontend:**
- Next.js 15 (App Router)
- React 19
- Tailwind CSS v4
- shadcn/ui components (Radix UI)
- Recharts
- TanStack Table

**Backend:**
- FastAPI
- Python 3.11+
- SQLModel (SQLAlchemy)
- Pydantic v2
- PostgreSQL

## 💡 Key Features Implemented
- Registration and Login interfaces
- Dashboard with dynamic Recharts and TanStack DataTable
- Modular shadcn UI components configured correctly for Next 15
- Robust FastAPI backend with Dependency Injection for authentication
- Postgres Database initialized automatically
