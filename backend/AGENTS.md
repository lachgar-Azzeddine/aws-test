# Project: SRM-CS Automation Backend

This project is the backend for the SRM-CS Automation platform. It is a Python-based application that uses Ansible Runner to automate the installation, provisioning, and management of the SI SRM-CS modules.

## Architecture

- **Framework:** The backend is built using the **FastAPI** framework, providing a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Database:** The application uses **SQLAlchemy** as the Object Relational Mapper (ORM) to interact with a **SQLite** database for its own data. It also has the capability to connect to **PostgreSQL** and **Informix** databases.
- **Automation Engine:** The core of the automation is powered by **Ansible Runner**, which is used to execute Ansible playbooks for infrastructure provisioning and software installation.
- **Authentication:** The application uses **JWT (JSON Web Tokens)** for authentication, with password hashing handled by **passlib**.
- **Containerization:** The application is designed to be run in a **Docker** container. The `Dockerfile` includes a complex setup for the Informix Client SDK.

## Building and Running

The project is containerized and can be built and run using Docker Compose.

- **Building the project:**

  ```bash
  docker build -t backend-harmonisation:latest .
  ```

- **Backend development server:**

  ```bash
  pip install -r requirements.txt
  uvicorn api:app --host 0.0.0.0 --port 8008 --reload
  ```

## Development Conventions

- The backend follows a three-layer architecture:
  1. **API Layer (`api.py`):** Defines the API endpoints and handles incoming requests.
  2. **Repository Layer (`repository.py`):** Implements the data access logic, encapsulating all database interactions.
  3. **Automation Layer (`install.py`):** Contains the logic for executing Ansible roles and managing the automation workflows.
- The project uses a repository pattern for data access.
- The `install.py` script dynamically loads and executes `prepare_inputs.py` and `post_install.py` scripts from within the Ansible role directories to manage role-specific logic.
- The application uses a `Fernet` encryption key to encrypt and decrypt sensitive data, such as passwords.

# Deployment Architecture look at: @ARCHITECTURE.md
