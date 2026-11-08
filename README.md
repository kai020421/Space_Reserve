# 🚀 SpaceReserve — Campus Resource & Room Reservation System

**SpaceReserve** is an enterprise-grade automated resource allocation and room reservation platform designed for university campuses. Built with a robust 3-tier architecture, it handles real-time space availability, priority preemption, automated no-show room releases, and concurrent booking request locks.

---

## 🏗️ Architecture & Technology Stack

The application strictly follows a decoupled **3-Tier Architecture**:

* **Frontend (Presentation Layer):** Flutter (Web, Android, iOS, Windows Desktop) with BLoC / Cubit state management.
* **Backend (Application Layer):** FastAPI (Python) asynchronous REST API with JWT-based Auth Middleware and Pydantic validation.
* **Database (Data Layer):** PostgreSQL managed via Docker containers and Alembic schema migrations.

---

## ✨ Key Features & Capabilities

* 🔐 **Secure Authentication & Access Control:** Bcrypt password hashing (work factor $\ge 12$), role-based access control (Student, Faculty, Admin, TA), and institutional email verification.
* ⚡ **High-Performance Room Search:** Composite database indexing for slot search queries under 150ms latency.
* 🔒 **Concurrency Lock Control:** DB-level pessimistic locking (`SELECT FOR UPDATE`) to prevent double-booking of identical time slots.
* ⚖️ **Priority Preemption Engine:** Automated priority scoring to allow high-capacity campus events to displace lower-ranked reservations gracefully.
* ⏱️ **Tap-to-Check-In & Automated Release:** 15-minute check-in window validation paired with background tasks to release unallocated space back to public inventory.

---

## 📊 Agile Sprint Roadmap

The development process is structured into 4 sequential 2-week Sprints (Total: 182 Story Points):

| Sprint | Phase Focus | Key Deliverables & Engineering Scope |
| :--- | :--- | :--- |
| **Sprint 1** | **Foundation & Auth** | DB schema design, Alembic setup, FastAPI base architecture, Bcrypt/JWT security guard, Flutter UI login pages, and HTTP interceptors. |
| **Sprint 2** | **Discovery & Quotas** | Search & filtering engine, daily room quota enforcement (1 active slot/day), composite indexes, and student reservation dashboards. |
| **Sprint 3** | **Booking Engine & Locks** | Pessimistic locking implementation, TA exception request routing, priority preemption manager, and check-in window validation. |
| **Sprint 4** | **Automation & Benchmarking** | Async background workers (no-show processing), multi-channel email alerts, immutable audit logging, and Locust load testing scripts. |

---

## 🛠️ Getting Started (Local Setup)

### Prerequisites
* [Flutter SDK](https://docs.flutter.dev/get-started/install) (v3.x or higher)
* [Python 3.11+](https://www.python.org/)
* [Docker Desktop](https://www.docker.com/) & PostgreSQL

### 1. Repository Setup
```bash
git clone [https://github.com/kai020421/Space_Reserve.git](https://github.com/kai020421/Space_Reserve.git)
cd Space_Reserve
