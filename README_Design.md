# SSO Alert System Design

## Diagram Description

![Structural Design of the Project](Design_Diagram.png)

The diagram represents the main services and interactions in the application. This setup includes three core components:
**Nginx Proxy Manager**, **Django Application**, and **PostgreSQL Database**. Each component plays a critical role in
the application’s functionality.

### 1. **Nginx Proxy Manager**

- **Description**: This service acts as a reverse proxy, managing external HTTP and HTTPS requests to the application.
  It also handles SSL certificates through Let's Encrypt, ensuring secure connections.
  - Listens on ports 80 (HTTP), 443 (HTTPS), and 81 (for Nginx management interface).
  - Routes incoming traffic to the Django application based on defined proxy rules.
  - Manages reverse proxy settings and SSL certificates.
  - Exposes:
    - Port `81` for the admin interface.
    - Port `80` for HTTP traffic.
    - Port `443` for HTTPS traffic.
  - Stores configuration and SSL data in mounted volumes.

### 2. **Django Application**

- **Description**: This is the main application service. It connects to the other resources including the PostgreSQL
  database and provides the core functionality of the app.
  - Interacts with Nginx Proxy Manager to handle requests routed from the internet.
  - Communicates with the PostgreSQL database to read and write application data.
  - Leverages the functionalities provided by the tom toolkit apps (Can be viewed
      at [tom demo site](https://tom-demo.lco.global/)). On top of that, it has got its own (custom) apps to support
      additional features and customised functionality requests.
  - Hosts two custom facility classes (DREAMS, ANU230cm) to make queries to those facilities and submit observations.
      For details on how to add facility to TOM, please see
      [writing an observation module](https://tom-toolkit.readthedocs.io/en/latest/observing/observation_module.html).
  - Runs a web application built from the local directory.
  - Connects to the PostgreSQL database.
  - Exposes port `8080` for external access.
  - Environment variables configure the database connection.

### 3. **PostgreSQL Database**

- **Description**: This service provides a persistent database to store application data.
  - Accepts connections from the Django application to manage and retrieve data.
  - Stores data persistently in the `postgresql/data` directory. This includes all tables, records, and schema
      information necessary for application functionality.
- Provides a database backend for the web application.
- Exposes port `5432` for database access.
- Stores persistent data in a local volume.

### Summary

This component setup enables the application to serve users securely via Nginx, interact with a PostgreSQL database for
data management, and isolate each component for better scalability and maintainability.

## Cron jobs

In addition to the services described above, the system employs two cron jobs to read streams and update submitted
observation status. These jobs run management commands inside the Docker container at specified intervals and log the
output for monitoring.

### 1. Read Streams via `run_readstreams.sh` Cron Job

This cron job runs every 5 minutes and executes the `readstreams` management command.

### 2. Update Status `run_updatestatus.sh` Cron Job

This cron job runs every 2 hours and executes the `updatestatus` management command.

## Workflow for Future Modifications

The project is set up as an extension to the **TOM Toolkit** (a Django-based project), retaining all applicable
functionalities of TOM while introducing new features through custom applications. ADACS developers have added three new
Django apps to meet specific requirements outlined in the design document.

To accommodate future modification requests, the following steps were taken by ADACS developers and can serve as a
guideline for future updates:

1. **Feature/Extension Assessment**
   Each feature or extension request is evaluated to determine whether it can be fulfilled using existing TOM Toolkit
   capabilities.

2. **Implementation Paths**
    - **If TOM Features Are Sufficient**: Make necessary adjustments within the Django templates (HTML, CSS, JS) if
      needed.
        - **Example**: Updating the `observation_form.html` file for front-end
          customizations ([see example template](sso_tom/templates/tom_observations/observation_form.html)).

    - **If New Functionality Is Required**:
        - **Extending Existing Views**: When some TOM Toolkit functionalities are applicable, consider extending the
          Django views in the custom Django app.
            - **Example**: Customizing view logic
              in `views.py` ([see reference](sso_tom/sso_tom/views.py)).
        - **Implementing as a New Feature**: If no TOM Toolkit components can be leveraged, develop the feature
          independently within the custom app.
            - **Example**: Building new views from scratch for unique
              features ([see reference](sso_tom/sso_alerts/views.py)).

By following these steps, future modifications can be efficiently managed while preserving TOM’s core functionalities
and integrating custom extensions.

## Software Maintenance Documentation

There are some steps which could be followed by the IT people to make sure the application is running smoothly.

### 1. **Regular Monitoring and Logs**

- Ensure that cron jobs are running as expected by checking the logs generated by the scripts (`readstreams` and `updatestatus`). Logs are stored in date-based subdirectories to facilitate monitoring.
- Review logs periodically for any signs of errors, failures, or abnormal behaviors. Any issues in the cron jobs should be investigated immediately to avoid potential disruptions in application functionality.

#### 1.1 Do I need to back up cron job logs?

Not necessarily. The application will be able to run smoothly after restarting even if you don't do the backup.

### 2. **Backup Strategy**

- Regularly back up essential data, i.e., the PostgreSQL database to prevent data loss. Automated and secured backups
  should be scheduled if possible.
- Use volume mounts in Docker to ensure data persistence across container restarts. For example, the PostgreSQL data is
  stored in a mounted volume, which should be backed up as part of the disaster recovery plan.

#### 2.1 Where is the Data Stored

The PostgreSQL service stores its data in the following volume mount - `./postgresql/data:/var/lib/postgresql/data` -
This is where the actual PostgreSQL database files are stored. All database records, schemas, and configurations are
stored here.

#### 2.2 What to Back Up

PostgreSQL Data (`./postgresql/data`): This directory contains the full database for your application. It is essential
to back this up regularly, as it stores all the critical data required for the application's operation.

### 3. **Security Updates**

- Stay up-to-date with security patches for both the Docker containers (e.g., Nginx, PostgreSQL) and the application
  dependencies. Regularly update images used in the `docker-compose.yml` file to their latest stable versions to
  incorporate security fixes.
- If required, you can update the `tom-toolkit` that is used under the hood of the web application, however, it could
  potentially lead to various errors in the extended UI components which need to be fixed in the UI code.
- Ensure that SSL certificates managed by Nginx Proxy Manager are renewed automatically.

### 4. **Database Maintenance**

- Monitor the database size and storage utilization, especially in the mounted volumes.
