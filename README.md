# ⚖️ Smart Court Case Management System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)
![GraphQL](https://img.shields.io/badge/GraphQL-API-pink.svg)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-orange.svg)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![Project](https://img.shields.io/badge/Project-Educational-yellow.svg)

A **Smart Court Case Management System** built using **Python, FastAPI, Strawberry GraphQL, and SQLAlchemy** to manage **court cases, judges, lawyers, hearings, and verdicts** efficiently.

This project demonstrates a **modern backend architecture with GraphQL APIs** allowing flexible queries and mutations for legal case management.

---

# 📌 Project Overview

The **Smart Court Case Management System** helps organize and manage court processes digitally.  
It allows administrators to:

- Register **cases**
- Add **judges and lawyers**
- Schedule **hearings**
- Track **case progress**
- Record **verdicts**

The system ensures **data validation, unique constraints, and proper case status transitions**.

---

# 🚀 Features

### 📂 Case Management
- Create and manage court cases
- Track case status
- Retrieve case details

### 👨‍⚖️ Judge Management
- Register judges
- Assign court rooms
- Retrieve judge information

### 👨‍💼 Lawyer Management
- Register lawyers
- Maintain unique bar IDs

### 📅 Hearing Scheduling
- Schedule hearings for cases
- Prevent hearing overlaps
- Track hearing status

### 📜 Verdict Recording
- Store final decisions
- Maintain verdict history

### ⚡ GraphQL API
- Flexible queries
- Efficient data fetching
- Clean API design

---

# 🛠 Tech Stack

| Technology | Usage |
|------------|------|
| **Python 3.8+** | Core programming language |
| **FastAPI** | Web framework |
| **Strawberry GraphQL** | GraphQL schema and resolvers |
| **SQLAlchemy** | ORM for database |
| **SQLite** | Data storage |
| **Uvicorn** | ASGI server |
| **Python-dotenv** | Environment variable management |

---

# 📦 Installation

Install required dependencies:

```bash
pip install strawberry-graphql fastapi sqlalchemy python-dotenv uvicorn
```

---

# ▶️ Running the Project

Start the server using:

```bash
uvicorn main:app --reload
```

Server will run on:

```
http://localhost:8000
```

---

# 🌐 API Endpoints

| Endpoint | Description |
|--------|--------|
| `/graphql` | GraphQL Playground |
| `/info` | API information |
| `/health` | Health check |

Open GraphQL Playground:

```
http://localhost:8000/graphql
```

---

# 🗂 Project Structure

```
project-root
│
├── app
│   ├── types.py
│   ├── utils.py
│   │
│   └── resolvers
│       ├── case_resolver.py
│       ├── judge_resolver.py
│       ├── lawyer_resolver.py
│       ├── hearing_resolver.py
│       └── verdict_resolver.py
│
├── db.py
├── schema.py
├── main.py
├── elearning.db
├── .env
├── .gitignore
└── README.md
```

---

# 📊 Database Schema

## Case

| Field | Type |
|------|------|
| id | Integer |
| caseNumber | String |
| type | String |
| status | Enum |
| filedDate | Date |

## Judge

| Field | Type |
|------|------|
| id | Integer |
| name | String |
| courtRoom | String |

## Lawyer

| Field | Type |
|------|------|
| id | Integer |
| name | String |
| barId | String |

## Hearing

| Field | Type |
|------|------|
| id | Integer |
| caseId | Integer |
| judgeId | Integer |
| hearingDate | Date |
| status | Enum |

## Verdict

| Field | Type |
|------|------|
| id | Integer |
| caseId | Integer |
| decision | String |
| decisionDate | Date |

---

# 🔎 GraphQL Queries

### Fetch All Cases

```graphql
query GetAllCases {
  getCases {
    id
    caseNumber
    type
    status
    filedDate
  }
}
```

---

### Get Case by ID

```graphql
query GetCaseById {
  getCaseById(caseId: 1) {
    id
    caseNumber
    status
    filedDate
  }
}
```

---

### Get All Judges

```graphql
query GetAllJudges {
  getJudges {
    id
    name
    courtRoom
  }
}
```

---

### Get All Lawyers

```graphql
query GetAllLawyers {
  getLawyers {
    id
    name
    barId
  }
}
```

---

### Get Hearings by Case

```graphql
query GetHearingsByCase {
  getHearingsByCase(caseId: 1) {
    id
    hearingDate
    status
    judgeId
  }
}
```

---

### Get Verdicts by Case

```graphql
query GetVerdictsByCase {
  getVerdictsByCase(caseId: 3) {
    id
    decision
    decisionDate
  }
}
```

---

# ✏️ GraphQL Mutations

### Create Case

```graphql
mutation CreateCase {
  createCase(input: {
    caseNumber: "CASE-2023-004"
    type: "Family"
    status: FILED
  }) {
    success
    message
    case {
      id
      caseNumber
      status
    }
  }
}
```

---

### Update Case Status

```graphql
mutation UpdateCaseStatus {
  updateCaseStatus(caseId: 1, newStatus: ONGOING) {
    success
    message
    case {
      id
      status
    }
  }
}
```

---

### Create Judge

```graphql
mutation CreateJudge {
  createJudge(
    input: {
      name: "Justice Sharma"
      courtRoom: "A101"
    }
  ) {
    success
    message
    judge {
      id
      name
      courtRoom
    }
  }
}
```

---

### Create Lawyer

```graphql
mutation CreateLawyer {
  createLawyer(
    input: {
      name: "Advocate Mehta"
      barId: "BAR12345"
    }
  ) {
    success
    message
    lawyer {
      id
      name
      barId
    }
  }
}
```

---

### Get Scheduled Hearings

```graphql
query GetScheduledHearings {
  getScheduledHearings {
    id
    caseId
    judgeId
    hearingDate
    status
  }
}
```

---

### Delete Hearing

```graphql
mutation DeleteHearing {
  deleteHearing(hearingId: 2) {
    success
    message
  }
}
```

---

# 🔐 Validation Rules

### Case Status Flow

```
FILED → ONGOING → CLOSED
```

Cases must follow this order and cannot revert to previous states.

---

### Hearing Overlap Prevention

A **judge cannot have two hearings on the same date**.

---

### Unique Constraints

- Case numbers must be unique
- Lawyer bar IDs must be unique
- Judge + courtroom combination must be unique

---

# 🧪 Testing

Testing can be done using **GraphQL Playground**.

```
http://localhost:8000/graphql
```

---

# 🎓 Educational Purpose

This project was developed for **academic learning and backend development practice**, demonstrating:

- GraphQL API design
- FastAPI backend architecture
- Database management
- API validation and business logic

---

# 👨‍💻 Author

**Antriksh Sandesh Manwadkar**

Computer Science Engineering Student  
Passionate about building innovative technology solutions.

---

# ⭐ Support

If you found this project helpful, please **give it a star ⭐ on GitHub**.
