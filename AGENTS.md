# Project: SRM-CS Automation

This project is designed to automate the installation, provisioning, and management of the SI SRM-CS modules, which include EService and GCO. The primary goal is to streamline the deployment process using an Infrastructure as Code (IaC) approach.

## Core Components

The project is composed of several key components that work together to provide a comprehensive automation solution:

### 1. **Backend (`/backend`)**

The backend is the central orchestration engine of the project. It is a Python-based application that uses **Ansible Runner** to execute Ansible playbooks for provisioning and configuration management. The backend exposes an API that allows for programmatic control of the automation workflows.

Key responsibilities of the backend include:

- Managing the execution of Ansible playbooks.
- Handling environment and inventory management for Ansible.
- Providing a stable and consistent interface for interacting with Ansible.

### 2. **Frontend (`/frontend`)**

The frontend is an Angular-based web application that provides a user-friendly interface for interacting with the automation platform. Users can trigger and monitor the deployment of the SI SRM-CS modules through this interface.

### 3. **Packer (`/packer`)**

The project uses **Packer** to build standardized virtual machine templates for VMware vSphere. This ensures that the underlying operating system and base configuration are consistent across all deployments. The Packer templates are used to create the initial images that are then provisioned by Ansible.

### 4. **Corteza (`/corteza`)**

The project includes **Corteza**, a 100% open-source, low-code platform for building and deploying web applications. While the exact role of Corteza in this project is not fully detailed in the documentation, it is likely used as a component of the overall solution, potentially for building administrative interfaces or for managing business processes related to the SI SRM-CS modules.

## Architecture

- **Frontend:** An Angular application that provides the user interface for managing the automation platform.
- **Backend:** A Python FastAPI application that exposes a REST API to control the automation workflows. It uses Ansible Runner to execute Ansible playbooks for provisioning and configuration management. It uses a SQLite database for storing its state.
- **Packer:** Used to build standardized virtual machine templates for VMware vSphere.
- **Corteza:** A low-code platform integrated into the project.
- **nginx:** Used as a reverse proxy to route traffic to the different services.
- **Docker:** All the components are containerized using Docker and orchestrated with `docker-compose`.

## Workflow

The overall workflow of the project can be summarized as follows:

1. **Image Creation:** Packer is used to create a base virtual machine image with a pre-configured operating system.
2. **Provisioning:** The backend, using Ansible Runner, executes a series of Ansible playbooks to provision the virtual machine. This includes installing the necessary software, configuring the network, and deploying the SI SRM-CS modules (EService, GCO).
3. **Management:** The Angular frontend provides a user interface to initiate and monitor the deployment process.

## Technologies Used

- **Python:** For the backend orchestration layer.
- **Ansible:** For configuration management and application deployment.
- **Packer:** For building virtual machine images.
- **Angular:** For the frontend web application.
- **Docker:** For containerizing the different components of the project.
- **Corteza:** As a low-code platform for building related applications.

This project represents a modern approach to infrastructure management, leveraging automation and IaC principles to ensure consistency, reliability, and efficiency in the deployment of the SI SRM-CS modules.

## Building and Running

The project is containerized and can be built and run using Docker Compose.

- **Building the project:**

  ```bash
  docker compose build
  ```

- **Running the project:**

  ```bash
  docker compose up -d
  ```

- **Frontend development server:**

  ```bash
  cd frontend
  npm install
  ng serve
  ```

- **Backend development server:**

  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn api:app --host 0.0.0.0 --port 8008 --reload
  ```

## Development Conventions

- The backend is written in Python using the FastAPI framework. It uses a repository pattern for data access.
- The frontend is an Angular application.
- The project uses Ansible for configuration management. The playbooks are organized into roles.
- The `setup.sh` script suggests a specific setup for a test environment.

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

# CORTEZA ADMIN ACCOUNT

The Super ADMIN User for Corteza has the Login : <admin-os@srm-cs.ma> with the same password
The Super ADMIN SRM-CS User for Corteza has the Login : <admin-srm@srm-cs.ma> with the same password
The Super VIEWER SRM-CS User for Corteza has the Login : <viewer-srm@srm-cs.ma> with the same password

# SOME UTILITIES COMMAND

Exporting database :

```bash
docker compose exec postgres pg_dump -U harmonisation -d harmonisation > /home/mrabbah/Documents/srm-cs/runner-src/data/db/02-init-db-data.sql
```
