<div align="center">

# 📘 DEVBOOKS — TECHNICAL BOOKSTORE & LIBRARY STORE
### *The Ultimate Curated Reading Platform for Software Engineers & Architects*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

</div>

---

## 🛠️ Overview

**DevBooks** is a high-performance, full-stack technical bookstore application designed to provide developers, engineers, and tech enthusiasts with seamless access to top-tier literature. Built with modern asynchronous architecture and secure JWT authentication, DevBooks bridges the gap between fast backend execution and an architect-focused responsive user interface.

---

## 🚀 Core Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend Framework** | Python, FastAPI, Pydantic, PyMongo |
| **Database** | MongoDB (NoSQL Document Store) |
| **Security & Auth** | `bcrypt` (Secure Password Hashing), `PyJWT` (Token Authentication & Cookie Handling) |
| **Frontend UI/UX** | HTML5, Jinja2 Templates, Bootstrap 5, Custom CSS, Vanilla JavaScript |
| **Version Control** | Git & GitHub |

---

## ✨ Key Features & Capabilities

* **🔐 Secure Role-Based Access Control:** Strict system roles (`Admin` and `Guest`). Public registration is securely locked to the `Guest` role by default to prevent privilege escalation.
* **👤 Advanced Profile Management:** Users can update credentials, secure passwords, and upload custom profile avatars with a dynamic live-preview interface.
* **📚 Curated Book Catalog:** Searchable and filterable technical library categorized by specific engineering domains (Backend Development, Frontend & UI, DevOps & Cloud).
* **🤖 Interactive AI Support Chatbot:** Built-in floating customer support bot instantly handling order tracking, shipping inquiries, and cancellation policies.
* **⚡ Modern SaaS UI Styling:** Fully responsive design featuring marquee promotional bars, interactive password visibility toggles, smart navigation dropdowns, and real-time form validations.

---

## 📂 Project Directory Structure

```text
FastApi NEW PROJECT/
├── config/             # MongoDB database connection setup
├── models/             # Pydantic data validation models
├── schemas/            # Database serialization entities & mappers
├── routes/             # FastAPI endpoint routers (Users, Books, Auth)
├── static/             # Static assets (CSS, JS, uploaded user avatars)
├── templates/          # Jinja2 HTML layout components and views
│   ├── base.html       # Master layout with dynamic navbar & chatbot
│   └── users/          # Authentication & profile views (Login, Register, Update)
├── main.py             # FastAPI application entry point
└── requirements.txt    # Project Python dependencies
⚙️ Local Installation & Setup
Follow these steps to run DevBooks locally on your machine:

Clone the repository:

Bash
git clone [https://github.com/jatingulati1264/fastapi-book-library-store-DEVBOOKS--Python.git](https://github.com/jatingulati1264/fastapi-book-library-store-DEVBOOKS--Python.git)
cd "FastApi NEW PROJECT"
Create and activate a virtual environment:

Bash
python -m venv env
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
Install project dependencies:

Bash
pip install -r requirements.txt
Run the FastAPI development server:

Bash
uvicorn main:main --reload
Open in your browser:
Navigate to http://127.0.0.1:8000 to explore the platform.

🔐 Security Implementations
No Plaintext Passwords: All user passwords are computationally hashed and salted using bcrypt before database insertion.

Stateless Authentication: JWTs are utilized for session management, stored securely in HttpOnly cookies to mitigate XSS (Cross-Site Scripting) attacks.

Backend Role Enforcement: Registration forms drop the type parameter from the frontend entirely, hardcoding new users as Guest on the server-side to prevent malicious HTTP POST manipulations.

👤 Author
Developed with passion and precision by Jatin Gulati

Software Engineer & Creator
