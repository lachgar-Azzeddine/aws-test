# Project: SRM-CS Automation

This project is designed to automate the installation, provisioning, and management of the SI SRM-CS modules, which include EService and GCO. The primary goal is to streamline the deployment process using an Infrastructure as Code (IaC) approach.

## Technologies Used

- **Python:** For the backend orchestration layer.
- **Ansible:** For configuration management and application deployment.
- **Packer:** For building virtual machine images.
- **Docker:** For containerizing the different components of the project.

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

- The backend is written in Python using the FastAPI framework. It uses a repository pattern for data access.

# Backend Analysis

## Summary of Findings

The backend is a FastAPI application with a three-layer architecture. It uses a SQLite database for its own data, but can connect to PostgreSQL and Informix databases. Ansible Runner is a core component, used to automate infrastructure provisioning and software installation. The application is designed to be run in a Docker container, and the Dockerfile includes a complex setup for the Informix Client SDK.

## Relevant Locations

| File                                                                 | Reasoning                                                                                                                                                                                                                  | Key Symbols                                                        |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `/home/mrabbah/Documents/srm-cs/runner-src/backend/api.py`           | This is the main entry point of the FastAPI application. It defines all the API endpoints and orchestrates the calls to the repository and other modules.                                                                  | `app`, `start_install`, `login_for_access_token`                   |
| `/home/mrabbah/Documents/srm-cs/runner-src/backend/models.py`        | This file defines the database schema using SQLAlchemy and Pydantic. It provides a clear picture of the data that the application manages.                                                                                 | `Base`, `User`, `Product`, `AnsibleRole`                           |
| `/home/mrabbah/Documents/srm-cs/runner-src/backend/repository.py`    | This file implements the data access layer. It encapsulates all the database logic, including session management, CRUD operations, and more complex queries. It also handles password encryption and authentication logic. | `get_session`, `create_user`, `authenticate_user`, `test_database` |
| `/home/mrabbah/Documents/srm-cs/runner-src/backend/install.py`       | This file is the heart of the Ansible integration. It uses the ansible_runner library to execute Ansible roles, with a flexible system for dynamically loading variables and handling post-install tasks.                  | `install_all_roles`, `call_role`, `load_and_call_get_inputs`       |
| `/home/mrabbah/Documents/srm-cs/runner-src/backend/requirements.txt` | This file lists all the Python dependencies of the project, which is crucial for understanding the technologies used.                                                                                                      | `fastapi`, `sqlalchemy`, `ansible-runner`, `psycopg2-binary`       |
| `/home/mrabbah/Documents/srm-cs/runner-src/backend/Dockerfile`       | This file shows how the application is containerized. It reveals important details about the runtime environment, including the installation of the Informix Client SDK.                                                   | `FROM`, `RUN`, `ENTRYPOINT`, `CMD`                                 |
