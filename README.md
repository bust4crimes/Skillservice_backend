# 💡 SkillService

**A Master Social & Skills Development Ecosystem**

SkillService is a cross-platform platform that connects users to offer and request skills. Built with a modern, decoupled architecture, it features a highly responsive mobile/web frontend and a blazing-fast Python backend.

---

## 🚀 Tech Stack

### **Frontend (Mobile & Web)**
* **Framework:** [Flutter](https://flutter.dev/) (Dart)
* **Platforms Supported:** Android, iOS, and Web browsers
* **State Management:** Provider
* **Authentication Client:** Firebase Auth (Email/Password, Google Sign-In)

### **Backend (API)**
* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3)
* **Server:** Uvicorn
* **Authentication Verification:** Firebase Admin SDK 
* **Cloud Hosting:** Render

### **Database**
* **Engine:** MongoDB (NoSQL)
* **ODM:** Motor (Async Python driver for MongoDB)

---

## ✨ Core Features

* **Secure Authentication:** Seamless login and registration backed by Google's Firebase Authentication, featuring email verification and secure session handling.
* **Discovery Feed:** A real-time, filterable feed where users can browse active skill offers and requests.
* **Dynamic Skill Posting:** Users can easily create and publish new skills to the community.
* **Cross-Platform Compatibility:** Runs flawlessly natively on Android devices or perfectly in a web browser.
* **Cloud-Ready:** Backend API is fully configured for deployment on modern cloud providers using environment variables for secure secret management.

---

## 🛠️ Local Development Setup

If you want to run this project on your local machine, follow these steps:

### 1. Backend Setup (FastAPI)
1. Navigate to the backend directory: `cd Skillservice_backend`
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
