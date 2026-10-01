# AI-Powered University Support System

An AI-powered university support system for **ABES Engineering College** that uses **Retrieval-Augmented Generation (RAG)** to provide students with grounded, institution-specific answers from an approved university knowledge base.

The system is designed around a simple principle:

> **University-specific answers should be grounded in institutional evidence rather than generated from unsupported model knowledge.**

---

## 1. Project Overview

University students frequently need information related to:

- Academic calendars
- Academic programs and departments
- Examination rules
- Faculty information
- Teacher cabin and seating locations
- Fee information
- Current notices
- Student services
- University policies

This project provides a centralized AI-based interface where students can ask such questions using natural language.

Instead of allowing an LLM to answer university-specific questions directly from its pretrained knowledge, the system retrieves relevant information from the ABES knowledge base and provides that evidence to the LLM before generating a response.

### Core Flow

```text
Student
   |
   v
Next.js Frontend
   |
   v
FastAPI Backend
   |
   v
Authentication
   |
   v
Query Processing
   |
   v
Vector Retrieval
   |
   v
ABES Knowledge Base
   |
   v
Relevant Evidence
   |
   v
Context Construction
   |
   v
Groq / GPT-OSS 20B
   |
   v
Grounding Validation
   |
   +-------------------+
   |                   |
   v                   v
Grounded Answer     Controlled Fallback
```

---

# 2. System Architecture

```text
                         +-------------------------+
                         |    ABES Documents       |
                         | PDF / DOCX / MD / CSV   |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |    Document Loader      |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         | Normalization & Chunking|
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |       BGE-M3            |
                         |      Embeddings         |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |         FAISS           |
                         |      Vector Index       |
                         +------------+------------+
                                      |
                               Student Query
                                      |
                                      v
                         +-------------------------+
                         |    Retrieval Engine     |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |     Context Builder     |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |    Groq / GPT-OSS 20B   |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |   Grounding Validation  |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |     FastAPI Backend     |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |     Next.js Frontend    |
                         +-------------------------+
```

---

# 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js |
| UI | React + Tailwind CSS |
| Frontend Language | JavaScript |
| Backend | Python |
| API Framework | FastAPI |
| LLM Provider | Groq |
| LLM | `openai/gpt-oss-20b` |
| Embedding Model | BGE-M3 |
| Vector Database / Search | FAISS |
| Application Database | MySQL |
| Database ORM / Driver | SQLAlchemy + PyMySQL |
| Authentication | JWT |
| Password Hashing | Passlib + bcrypt |
| API Documentation | FastAPI Swagger / OpenAPI |
| Package Management | npm + Python virtual environment |

---

# 4. Repository Structure

```text
university-support-system/
|
├── backend/
│   |
│   ├── app/
│   │   |
│   │   ├── api/
│   │   │   |
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── security.py
│   │   │   │   └── service.py
│   │   │   │
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── health.py
│   │   │   │   └── retrieve.py
│   │   │   │
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   └── rag_service.py
│   │   │   │
│   │   │   ├── context_builder.py
│   │   │   ├── db.py
│   │   │   ├── grounding.py
│   │   │   ├── main.py
│   │   │   └── schemas.py
│   │   │
│   │   └── rag/
│   │       ├── document_loader.py
│   │       ├── embeddings.py
│   │       ├── generator.py
│   │       ├── ingest.py
│   │       ├── retriever.py
│   │       └── vector_store.py
│   │
│   ├── sql/
│   │   └── auth_users.sql
│   │
│   ├── venv/
│   ├── .env
│   └── ...
│
├── data/
│   ├── knowledge_base/
│   └── vector_store/
│
├── frontend/
│   ├── app/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── screenshots/
│   ├── login.png
│   ├── dashboard.png
│   ├── chat.png
│   ├── rag-answer.png
│   ├── sources.png
│   ├── fallback.png
│   ├── fastapi-docs.png
│   └── health.png
│
├── README.md
└── .gitignore
```

---

# 5. Retrieval-Augmented Generation

The project uses **Retrieval-Augmented Generation (RAG)** rather than relying directly on the LLM's pretrained knowledge.

## Why RAG?

University information is:

- Institution-specific
- Frequently updated
- Often unavailable in general LLM training data
- Sensitive to incorrect answers
- Better represented through official documents

The RAG pipeline allows the system to retrieve relevant university information before asking the LLM to generate an answer.

### RAG Pipeline

```text
User Question
      |
      v
Query Embedding
      |
      v
FAISS Similarity Search
      |
      v
Relevant ABES Documents
      |
      v
Context Construction
      |
      v
LLM Generation
      |
      v
Grounding Validation
      |
      v
Final Answer
```

---

# 6. Knowledge Base

The current knowledge base contains institutional information covering:

- Academic calendar
- Academic programs and departments
- Examination rules
- Faculty directory
- Teacher seating plan
- Fee information
- Current notices
- General student policies
- Student services
- University overview

The current ingestion result is:

```text
Files discovered:              11
Documents loaded:             169
Documents after normalization: 169
Chunks created:               169
Unique chunk IDs:             169
Missing IDs:                    0
```

The final ingestion validation passed successfully.

---

# 7. Document Ingestion

The ingestion pipeline performs:

```text
Source Documents
      |
      v
File Loading
      |
      v
Normalization
      |
      v
Metadata Standardization
      |
      v
Chunking
      |
      v
Chunk ID Generation
      |
      v
Validation
```

Supported source formats include:

```text
PDF
DOCX
TXT
Markdown
CSV
JSON
XLSX
PPTX
HTML
```

The ingestion process validates:

- Required metadata
- Empty chunks
- Chunk ID uniqueness
- Metadata consistency
- Document distribution
- Chunk statistics

### Current Chunk Statistics

```text
Minimum chunk length : 177
Maximum chunk length : 859
Average chunk length : 271.13

Chunks <= 200 chars  : 80
Chunks 201-500 chars : 84
Chunks 501-1000 chars: 5
Chunks > 1000 chars  : 0
```

### Document Distribution

```text
ACADEMICS_ACADEMIC_CALENDAR_MD
ACADEMICS_PROGRAMS_AND_DEPARTMENTS_MD
EXAMINATIONS_EXAMINATION_RULES_MD
FACULTY_NAVIGATION_FACULTY_DIRECTORY_CSV
FACULTY_NAVIGATION_TEACHER_SEATING_PLAN_CSV
FACULTY_NAVIGATION_TEACHER_SEATING_PLAN_MD
FEES_FEE_INFORMATION_MD
POLICIES_NOTICES_CURRENT_NOTICES_MD
POLICIES_NOTICES_GENERAL_STUDENT_POLICIES_MD
STUDENT_SERVICES_STUDENT_SERVICES_DIRECTORY_MD
UNIVERSITY_UNIVERSITY_OVERVIEW_MD
```

---

# 8. Embedding Generation

The system uses the **BGE-M3** embedding model for semantic representation of documents and queries.

The generated embeddings are normalized before being inserted into the vector index.

Current embedding statistics:

```text
Number of vectors : 169
Vector dimension  : 1024
```

The embedding generation stage has been validated successfully.

---

# 9. FAISS Vector Store

FAISS is used for vector similarity search.

The generated vector store contains:

```text
data/
└── vector_store/
    ├── abes_knowledge.index
    └── chunk_metadata.json
```

The FAISS index uses inner-product similarity over normalized embeddings.

The metadata file maintains the relationship between vectors and their original knowledge-base chunks.

Stored information includes:

- Vector position
- Chunk ID
- Chunk text
- Document metadata

---

# 10. Retrieval Engine

The retrieval engine is responsible for finding the most relevant knowledge-base chunks for a user query.

### Retrieval Flow

```text
User Query
     |
     v
Query Embedding
     |
     v
FAISS Similarity Search
     |
     v
Similarity Filtering
     |
     v
Duplicate Removal
     |
     v
Relevant Retrieval Results
```

Each retrieval result maintains information such as:

- Chunk ID
- Document ID
- Document name
- Category
- Source
- Retrieved text
- Similarity information

The retrieval engine was independently validated before being integrated with the generation pipeline.

---

# 11. Context Construction

Retrieved chunks are converted into structured context before being passed to the LLM.

The context contains:

```text
Source Information
        +
Retrieved Evidence
        +
Document Metadata
```

This ensures that the generation layer receives the evidence required to answer the student's question.

---

# 12. LLM Generation

The current generation model is:

```text
Provider : Groq
Model    : openai/gpt-oss-20b
```

The generation layer is instructed to:

- Use the supplied ABES evidence
- Avoid inventing university-specific information
- Avoid unsupported institutional claims
- Respond only from available evidence
- Use a controlled fallback when sufficient evidence is unavailable

The generation configuration uses a low temperature to reduce unnecessary variation in responses.

---

# 13. Grounding Validation

The generated answer is passed through a separate grounding layer.

The grounding layer validates whether the factual claims made in the answer are supported by the evidence retrieved for that specific query.

Possible grounding decisions are:

```text
GROUNDED
NOT_GROUNDED
REVIEW_REQUIRED
```

## GROUNDED

The factual claims in the response are supported by the retrieved evidence.

## NOT_GROUNDED

The generated response contains unsupported claims and should not be treated as a verified institutional answer.

## REVIEW_REQUIRED

The response requires additional review before being treated as reliable.

---

# 14. Controlled Fallback

A major requirement of the system is to avoid hallucinating university-specific information.

If the system cannot retrieve sufficient evidence, it should not fabricate an answer.

Example:

```text
Student:
"What is the attendance requirement for a course that is not
present in the current knowledge base?"

             |
             v

      Retrieval Engine
             |
             v
   Insufficient Evidence
             |
             v
        Fallback
             |
             v

"I couldn't find sufficient official ABES information to answer
this reliably. Please contact the relevant department or office."
```

The fallback mechanism is intended to prevent unsupported institutional claims from being presented as official information.

---

# 15. FastAPI Backend

The backend is implemented using **FastAPI**.

The backend exposes the RAG system and authentication functionality through REST APIs.

---

## 15.1 Health Endpoint

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "ABES AI University Support System",
  "version": "1.0.0"
}
```

---

## 15.2 Retrieval Endpoint

```http
POST /api/v1/retrieve
```

This endpoint retrieves relevant knowledge-base evidence for a user query.

Authentication is required.

---

## 15.3 Chat Endpoint

```http
POST /api/v1/chat
```

This endpoint executes the complete RAG flow:

```text
User Query
    |
    v
Retrieval
    |
    v
Context Construction
    |
    v
LLM Generation
    |
    v
Grounding Validation
    |
    v
Response
```

The API returns a grounded answer when the response passes the grounding stage.

---

# 16. Authentication

The system uses JWT-based authentication.

Authentication flow:

```text
Email + Password
       |
       v
MySQL users table
       |
       v
Password Verification
       |
       v
JWT Access Token
       |
       v
Authenticated Request
       |
       v
Protected API
```

The supported application roles are:

```text
STUDENT
STAFF
ADMIN
```

---

# 17. Authentication Endpoints

## Login

```http
POST /api/v1/auth/login
```

The login endpoint accepts OAuth2-compatible username/password form data.

The `username` field contains the user's email address.

Example:

```text
username = student@abes.ac.in
password = ********
```

---

## Current User

```http
GET /api/v1/auth/me
```

Returns the authenticated user's profile.

---

## Logout

```http
POST /api/v1/auth/logout
```

The current implementation uses token discard on the client side.

---

# 18. MySQL Database

The application database uses:

```text
Database: university_support
Host:     localhost
Port:     3306
```

The authentication system currently uses a `users` table.

### Users Table

| Field | Purpose |
|---|---|
| `id` | Unique user identifier |
| `email` | User email |
| `password_hash` | Hashed password |
| `full_name` | User's name |
| `role` | STUDENT / STAFF / ADMIN |
| `is_active` | Account status |
| `created_at` | Account creation time |
| `updated_at` | Last update time |

Passwords are never stored as plaintext.

---

# 19. Frontend

The frontend is built using:

- Next.js
- React
- Tailwind CSS
- JavaScript
- App Router

TypeScript is not used in this project.

The frontend is responsible for:

- Authentication
- Login interface
- Student dashboard
- Chat interface
- API communication
- Displaying RAG responses
- Displaying retrieved sources
- Displaying fallback responses
- Managing authenticated sessions

Frontend development server:

```bash
npm run dev
```

Application:

```text
http://localhost:3000
```

---

# 20. Screenshots

Screenshots should be stored in the repository's `screenshots/` directory.

Recommended structure:

```text
screenshots/
├── login.png
├── dashboard.png
├── chat.png
├── rag-answer.png
├── sources.png
├── fallback.png
├── fastapi-docs.png
└── health.png
```

## Login Interface

![Login Interface](screenshots/login.png)

---

## Student Dashboard

![Student Dashboard](screenshots/dashboard.png)

---

## Chat Interface

![Chat Interface](screenshots/chat.png)

---

## RAG Answer

![RAG Answer](screenshots/rag-answer.png)

---

## Retrieved Sources

![Retrieved Sources](screenshots/sources.png)

---

## Fallback Response

![Fallback Response](screenshots/fallback.png)

---

## FastAPI Swagger Documentation

![FastAPI Documentation](screenshots/fastapi-docs.png)

---

## Health Check

![Health Check](screenshots/health.png)

> These image paths should point to actual screenshots committed to the repository. Screenshots should be captured from the working application rather than being placeholders.

---

# 21. Local Development Setup

## Prerequisites

Install the following before running the project:

- Python
- Node.js
- npm
- MySQL
- Git

---

# 22. Backend Installation

Navigate to the backend directory:

```powershell
cd backend
```

Activate the existing Python virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Verify the Python interpreter:

```powershell
python -c "import sys; print(sys.executable)"
```

The output should point to:

```text
backend\venv\Scripts\python.exe
```

---

# 23. Environment Variables

Create the following file:

```text
backend/.env
```

Example structure:

```env
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/university_support

GROQ_API_KEY=your_groq_api_key

GROQ_MODEL=openai/gpt-oss-20b

JWT_SECRET=your_jwt_secret

ACCESS_TOKEN_EXPIRE_MINUTES=60

ALLOWED_ORIGINS=http://localhost:3000
```

Do not commit the actual `.env` file.

A safe `.gitignore` should contain:

```gitignore
.env
.env.*
!.env.example
```

Never publish:

- API keys
- JWT secrets
- Database passwords
- Authentication credentials
- Other private secrets

---

# 24. Database Setup

Make sure MySQL is running.

The application uses:

```text
university_support
```

The authentication table can be created using the provided SQL setup.

From the backend directory:

```powershell
python setup_auth_db.py
```

The script creates the required authentication table.

---

# 25. Start FastAPI

From the `backend` directory:

```powershell
python -m uvicorn app.api.main:app --reload
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

# 26. Frontend Installation

Open another terminal.

Navigate to the frontend:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

# 27. Running the Complete System

The backend and frontend should run simultaneously.

## Terminal 1 — Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.api.main:app --reload
```

## Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

Then open:

```text
http://localhost:3000
```

---

# 28. RAG Data Flow

A complete user interaction follows this flow:

```text
                     Student
                        |
                        v
                Next.js Frontend
                        |
                        v
                JWT Authentication
                        |
                        v
                  User Query
                        |
                        v
                FastAPI Backend
                        |
                        v
              Retrieval Service
                        |
                        v
               BGE-M3 Embedding
                        |
                        v
                FAISS Search
                        |
                        v
             Relevant ABES Chunks
                        |
                        v
                Context Builder
                        |
                        v
              Groq GPT-OSS 20B
                        |
                        v
              Generated Response
                        |
                        v
             Grounding Validator
                        |
                +-------+-------+
                |               |
                v               v
            GROUNDED      NOT/REVIEW
                |               |
                v               v
             Answer         Fallback
                |
                v
          Next.js Frontend
```

---

# 29. Validation Status

The project has been developed and validated progressively.

| Component | Status |
|---|---|
| Knowledge-base ingestion | Completed |
| Document normalization | Completed |
| Chunking | Completed |
| Chunk validation | Passed |
| BGE-M3 embeddings | Completed |
| FAISS vector store | Completed |
| Retrieval engine | Validated |
| Context construction | Completed |
| Groq generation | Validated |
| Grounding | Validated |
| FastAPI backend | Validated |
| MySQL connection | Validated |
| JWT authentication | Validated |
| Protected API routes | Validated |
| Next.js frontend | Running |
| Frontend authentication integration | In progress |
| Frontend ↔ FastAPI integration | In progress |
| End-to-end testing | Pending |
| Evaluation | Pending |
| Security review | Pending |
| Deployment | Pending |

---

# 30. Current RAG Statistics

```text
Knowledge-base files       : 11
Loaded documents           : 169
Generated chunks           : 169
Unique chunk IDs           : 169
Embedding vectors          : 169
Embedding dimensions       : 1024
```

---

# 31. Development Roadmap

```text
Project Foundation
        |
        v
Knowledge Base
        |
        v
Document Ingestion
        |
        v
Normalization & Chunking
        |
        v
Embedding Generation
        |
        v
FAISS Vector Store
        |
        v
Retrieval Engine
        |
        v
Context Construction
        |
        v
LLM Generation
        |
        v
Grounding & Fallback
        |
        v
FastAPI Backend
        |
        v
MySQL
        |
        v
Authentication & Authorization
        |
        v
Next.js Frontend
        |
        v
Frontend Integration
        |
        v
End-to-End Testing
        |
        v
Evaluation
        |
        v
Security Review
        |
        v
Deployment
```

---

# 32. Evaluation Plan

The system will be evaluated using multiple dimensions rather than relying only on LLM output quality.

## Retrieval Evaluation

Measure:

- Retrieval success
- Relevant document retrieval
- Similarity quality
- Retrieval failures
- Unanswerable queries

## Generation Evaluation

Measure:

- Answer correctness
- Answer relevance
- Completeness
- Response consistency
- Unsupported claims

## Grounding Evaluation

Measure:

- Grounded responses
- Ungrounded responses
- Review-required responses
- Fallback accuracy

## System Evaluation

Measure:

- API latency
- End-to-end latency
- Authentication behavior
- Error handling
- Regression behavior
- Multi-turn queries

---

# 33. Security Considerations

The system follows several security principles.

### Environment Secrets

Environment files should never be committed to Git.

### API Keys

Groq API keys must remain server-side.

### JWT Secrets

JWT secrets must remain server-side and should be sufficiently random.

### Passwords

Passwords are stored as bcrypt hashes rather than plaintext.

### Authentication

Protected API endpoints require a valid JWT access token.

### Authorization

User roles are included in the authentication system and can be used for role-specific access control.

### Student Data

Student-specific information should remain logically separated from the public institutional knowledge base.

### External Integrations

External student-system integrations should initially use read-only access where possible.

### HTTPS

Production deployment should use HTTPS.

### Credential Rotation

If a secret is ever exposed, it should be revoked and replaced immediately.

---

# 34. Git Security

The repository must not contain sensitive environment files.

The following should remain ignored:

```text
.env
.env.*
```

Before pushing changes:

```powershell
git status
```

Check that `.env` is not listed as a tracked file.

To inspect ignored environment files:

```powershell
git check-ignore -v backend/.env
```

---

# 35. Design Principles

The project follows several architectural principles.

## Grounded Answers

University-specific answers should come from the approved knowledge base.

## Controlled Generation

The LLM should generate answers from retrieved evidence rather than freely inventing institutional information.

## Explicit Fallback

If sufficient evidence is unavailable, the system should communicate that limitation instead of fabricating information.

## Separation of Responsibilities

Different components have different responsibilities:

```text
Ingestion
    -> Prepare knowledge

Embeddings
    -> Represent knowledge semantically

FAISS
    -> Search knowledge

Retriever
    -> Select relevant evidence

Context Builder
    -> Structure evidence

Generator
    -> Generate response

Grounding
    -> Validate response

FastAPI
    -> Expose system through APIs

MySQL
    -> Store application data

Next.js
    -> Provide user interface
```

---

# 36. Why RAG Instead of Fine-Tuning?

The system uses RAG because university information changes over time.

For example:

```text
Academic Calendar
       |
       v
New Academic Year
       |
       v
Updated Document
       |
       v
Re-index Knowledge Base
```

With a RAG architecture, updated institutional documents can be incorporated into the knowledge base without retraining the LLM itself.

This also allows the system to retain explicit connections between generated responses and the institutional evidence used to answer them.

---

# 37. Future Improvements

Potential future improvements include:

- Improved document versioning
- Automated knowledge-base updates
- Better retrieval evaluation
- Hybrid keyword + semantic retrieval
- Query rewriting
- Conversation memory
- More granular role-based authorization
- Student-specific integrations
- Administrative dashboard
- Analytics
- Feedback collection
- Automated regression testing
- Production deployment
- Monitoring and logging
- Better citation presentation
- Knowledge-source freshness tracking

---

# 38. Project Status

The core RAG pipeline has been implemented and validated.

Completed components include:

```text
Knowledge Base
       |
       v
Document Ingestion
       |
       v
Chunking
       |
       v
BGE-M3 Embeddings
       |
       v
FAISS
       |
       v
Retrieval
       |
       v
Context Construction
       |
       v
Groq Generation
       |
       v
Grounding
       |
       v
FastAPI
       |
       v
MySQL
       |
       v
JWT Authentication
       |
       v
Next.js Frontend
```

The project is currently moving through the **frontend integration and end-to-end testing phase**.

---

# 39. Next Development Steps

The immediate development sequence is:

1. Complete frontend authentication flow
2. Connect the frontend to FastAPI
3. Implement authenticated API requests
4. Build the student dashboard
5. Implement the RAG chat interface
6. Display generated answers
7. Display retrieved sources
8. Implement visible fallback handling
9. Test complete frontend-to-backend flow
10. Build evaluation test cases
11. Perform regression testing
12. Complete security review
13. Prepare deployment

---

# 40. Project Objective

The final objective is to provide ABES students with a centralized AI support system through which they can ask university-related questions naturally while maintaining a clear connection between the answer and the underlying institutional evidence.

The intended final architecture is:

```text
                        STUDENT
                           |
                           v
                   Next.js Frontend
                           |
                           v
                   FastAPI Backend
                           |
                           v
                    Authentication
                           |
                           v
                     User Query
                           |
                           v
                   Retrieval Engine
                           |
                           v
                  ABES Knowledge Base
                           |
                           v
                   Relevant Evidence
                           |
                           v
                   Context Builder
                           |
                           v
                   Groq GPT-OSS 20B
                           |
                           v
                  Grounding Validation
                      /          \
                     /            \
                    v              v
              GROUNDED        INSUFFICIENT
                    |              |
                    v              v
                 Answer         Fallback
```

The system therefore combines:

```text
Retrieval
+
Semantic Search
+
Large Language Models
+
Grounding
+
Authentication
+
MySQL
+
FastAPI
+
Next.js
```

to build an institution-specific AI support platform for university students.

---

## License

This project is developed for academic and educational purposes.
