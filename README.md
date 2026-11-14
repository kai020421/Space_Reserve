# 🚀 SpaceReserve — Campus Resource & Room Reservation System

**SpaceReserve** is an enterprise-grade automated resource allocation and room reservation platform designed for university campuses. Built with a robust 3-tier architecture, it handles real-time space availability, priority preemption, automated no-show room releases, and concurrent booking request locks.

---

## 🏗️ Architecture & Technology Stack

The application strictly follows a decoupled **3-Tier Architecture**:

- **Frontend (Presentation Layer):** Flutter (Web, Android, iOS, Windows Desktop) with BLoC / Cubit state management.
- **Backend (Application Layer):** FastAPI (Python) asynchronous REST API with JWT-based Auth Middleware and Pydantic validation.
- **Database (Data Layer):** PostgreSQL managed via Docker containers and Alembic schema migrations.

---

## ✨ Key Features & Capabilities

- 🔐 **Secure Authentication & Access Control:** Bcrypt password hashing (work factor $\ge 12$), role-based access control (Student, Faculty, Admin, TA), and strict institutional email verification (`@khi.iba.edu.pk` / `@iba.edu.pk`).
- ⚡ **High-Performance Room Search:** Composite database indexing for slot search queries under 150ms latency.
- 🔒 **Concurrency Lock Control:** DB-level pessimistic locking (`SELECT FOR UPDATE`) to prevent double-booking of identical time slots.
- ⚖️ **Priority Preemption Engine:** Automated priority scoring to allow high-capacity campus events to displace lower-ranked reservations gracefully.
- ⏱️ **Tap-to-Check-In & Automated Release:** 15-minute check-in window validation paired with background tasks to release unallocated space back to public inventory.

---

## 📊 Agile Sprint Roadmap

The development process is structured across **5 sequential Sprints**, moving from core authentication foundations to advanced automation and benchmarking:

| Sprint | Phase Focus | Key Deliverables & Engineering Scope |
| :--- | :--- | :--- |
| **Sprint 1** | **Foundation & Auth** *(Completed)* | Database schema design, Alembic setup, PostgreSQL seeding, FastAPI base architecture, JWT security guard, Bcrypt password hashing, global exception handlers, HTTP interceptors, and core Flutter login presentation pages. |
| **Sprint 2** | **Discovery & Quotas** *(Current)* | Room search and filtering engine (by building, capacity, and equipment), composite database indexing for availability queries, daily slot quota enforcement (1 active slot/day), maintenance room filtering, token clearance on logout, and Flutter room search and landing interfaces. |


---

## 🛠️ Getting Started (Local Setup)

### Prerequisites
- [Flutter SDK](https://docs.flutter.dev/get-started/install) (v3.x or higher)
- [Python 3.11+](https://www.python.org/)
- [Docker Desktop](https://www.docker.com/) & PostgreSQL

### 1. Repository Setup
```bash
git clone [https://github.com/kai020421/Space_Reserve.git](https://github.com/kai020421/Space_Reserve.git)
cd Space_Reserve
