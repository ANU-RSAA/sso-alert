# SSO Alert System UI Prototype

This is the User Interface of the Siding Spring Observatory's Alert System. This project uses Docker Compose to set up a
reverse proxy with Nginx Proxy Manager, a web application, and a PostgreSQL database. Each service is defined within the
`docker-compose.yml` file, ensuring a modular and scalable setup.

## Services

### 1. Nginx Proxy Manager
- Manages reverse proxy settings and SSL certificates.
- Exposes:
  - Port `81` for the admin interface.
  - Port `80` for HTTP traffic.
  - Port `443` for HTTPS traffic.
- Stores configuration and SSL data in mounted volumes.

### 2. Web Application
- Runs a web application built from the local directory.
- Connects to the PostgreSQL database.
- Exposes port `8080` for external access.
- Environment variables configure the database connection.

### 3. PostgreSQL Database
- Provides a database backend for the web application.
- Exposes port `5432` for database access.
- Stores persistent data in a local volume.

## Cron jobs

In addition to the services described above, the system employs two cron jobs to read streams and update submitted 
observation status. These jobs run management commands inside the Docker container at specified intervals and log the 
output for monitoring.

### 1. Read Streams via `run_readstreams.sh` Cron Job

This cron job runs every 5 minutes and executes the `readstreams` management command.

### 2. Update Status `run_updatestatus.sh` Cron Job

This cron job runs every 2 hours and executes the `updatestatus` management command.

## The Web Application service is Built with

![Django]
![tom]

## Installation

To run the prototype locally, please follow the below instructions.
```
cd <repo_location>
git clone --recursive git@gitlab.com:CAS-eResearch/external/sso-alert/ui.git
python3 -m venv <env_name>
source <env_name>/bin/activate
python3 -m pip install -r ui/requirements.txt 
```

## Run project
```

cd ui/sso_tom
python manage.py runserver
```
The project will now be available at http://localhost:8000/

<!-- Markdown links and images -->

[django]: https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white
[tom]: https://avatars.githubusercontent.com/u/39539400?s=48&v=4
