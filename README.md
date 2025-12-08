# SSO Alert System
<!-- Completely ripped off and updated from https://github.com/othneildrew/Best-README-Template -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#database">Database</a></li>
        <li><a href="#sso-alert">SSO Alert</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledging-usage">Acknowledging Usage</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

The Siding Spring Observatory (SSO) Alert System is designed to connect the various observing facilities at SSO to schedule observations in an automated manner.

The system uses Docker Compose to set up a reverse proxy with Nginx Proxy Manager, a web application, and a PostgreSQL database. Each service is defined within the `docker-compose.yml` file, ensuring a modular and scalable setup. For full details on the architecture of the system see _[README_Design](README_Design.md)_.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Django][django]][django-url]
* [![Python][python]][python-url]
* [![Tom Toolkit][tom]][tom-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

The prerequisites are dependent on whether you wish to deploy a local installation or a server installation.
Depending on your usage requirements you can create a python environment and/or container and database using any of:

* Containers
  * [![Docker][docker]][docker-url]
  * [![Podman][podman]][podman-url]
* Python Virtual Environments
  * [![conda][conda]][conda-url]
  * [![uv][uv]][uv-url]
  * **[venv][venv-url]**
* Databases
  * [![Postgres][postgres]][postgres-url]
  * [![SQLite][sqlite]][sqlite-url]

For a server installation, we currently recommend the use of podman. For a local installation, the easiest method (although not recommended by us) is the use of venv, as that is part of the Python Standard Library.

Both the server and local installation required a database backend, we recommend the use of Postgres DB.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Installation

#### Database

The SSO Alert System requires a database to be used. Depending on your preference for a database follow the instructions below.

* SQLite

  1. Create the database

      ```sh
      sqlite3 <database_filename>.sqlite3
      ```

* Postgresql

  1. Activate psql

      ```sh
      sudo -u postgres psql
      ```

  1. Create the database and database user

      ```sql
      CREATE DATABASE <database_name>;
      CREATE USER <database_user> with encrypted password '<database_password>';
      GRANT ALL PRIVILEGES ON DATABASE <database_name> to <database_user>;
      ```

The information contained in the <> should match the variables within the .env file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

#### SSO Alert

The following instructions are for a local installation using venv, assuming that Python is installed. Fill in <> with your choices.

1. Choose where to put the code

    ```sh
    cd <repo_location>
    ```

1. Clone the repo

   ```sh
   git clone https://github.com/ANU-RSAA/sso-alert.git
   ```

1. Create a Python environment

   ```sh
   python -m venv <env_name>
   ```

1. Activate the Python environment

   ```sh
   source <env_name>/bin/activate
   ```

1. Install the required packages

   ```sh
   python -m pip install -r podman/requirements.txt
   ```

1. Copy the file with the environment variables and update the .env file.

   ```sh
   cp sso_tom/.env.example sso_tom/.env
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

To run the SSO Alert System locally run the following steps.

1. Change to the appropriate directory where manage.py is located.

   ```sh
   cd sso_tom
   ```

1. Create/update database structure as needed

   ```sh
   python manage.py migrate
   ```

1. Run the server.

   ```sh
   python manage.py runserver 8080
   ```

The project will now be available at **<https://127.0.0.1:8000/>**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

Our development workflow primarily uses the "dev" branch to manage changes. All updates need to go through this branch before being applied to main.

1. Fork the project
1. Change to the dev branch (`git switch dev`)
1. Create your feature branch (`git checkout -b feature/AmazingFeature`)
1. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
1. Rebase your feature branch using the latest updates from dev (`git rebase dev`)
1. Push to the branch (`git push origin feature/AmazingFeature`)
1. Open a pull request to the dev branch

### Top contributors

<a href="https://github.com/ANU-RSAA/sso-alert/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ANU-RSAA/sso-alert" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the GNU GPLv3 License. See _[LICENSE](LICENSE)_ for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Project Link: _[https://github.com/ANU-RSAA/sso-alert](https://github.com/ANU-RSAA/sso-alert)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGING USAGE -->
## Acknowledging Usage

Acknowledging the usage of the SSO Alert System is not required, however, if you do make use of the SSO Alert System this does assist in tracking usage and will contribute to determining future support of the system.

If you would like to acknowledge us, an example is:

* This research made use of the Siding Spring Observatory Alert System.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* The SSO Alert System was originally developed as part of an Australian Research Council (**[ARC][arc-url]**) Linkage Infrastructure, Equipment and Facilities (**[LIEF][lief-url]**) grant: **[LE230100063][grant-url]** (PI: C. Lidman) by the Swinburne node of **[ADACS][adacs-url]**.
* This repository is currently maintained by the Research School of Astronomy and Astrophysics (**[RSAA][rsaa-url]**) at the Australian National University (**[ANU][anu-url]**).
* An instance of the SSO Alert System is deployed using infrastructure provided by the RSAA.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ANU-RSAA/sso-alert.svg?style=for-the-badge
[contributors-url]: https://github.com/ANU-RSAA/sso-alert/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ANU-RSAA/sso-alert.svg?style=for-the-badge
[forks-url]: https://github.com/ANU-RSAA/sso-alert/network/members
[stars-shield]: https://img.shields.io/github/stars/ANU-RSAA/sso-alert.svg?style=for-the-badge
[stars-url]: https://github.com/ANU-RSAA/sso-alert/stargazers
[issues-shield]: https://img.shields.io/github/issues/ANU-RSAA/sso-alert.svg?style=for-the-badge
[issues-url]: https://github.com/ANU-RSAA/sso-alert/issues
[license-shield]: https://img.shields.io/github/license/ANU-RSAA/sso-alert.svg?style=for-the-badge
[license-url]: https://github.com/ANU-RSAA/sso-alert/blob/main/LICENSE

[django]: https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white
[django-url]: https://www.djangoproject.com/
[python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[python-url]: https://www.python.org/
[tom]: https://avatars.githubusercontent.com/u/39539400?s=48&v=4
[tom-url]: https://lco.global/tomtoolkit/

[docker]: https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white
[docker-url]: https://www.docker.com/
[podman]: https://img.shields.io/badge/podman-892CA0?style=for-the-badge&logo=podman&logoColor=white
[podman-url]: https://podman.io/

[conda]: https://img.shields.io/badge/conda-342B029.svg?&style=for-the-badge&logo=anaconda&logoColor=white
[conda-url]: https://docs.conda.io/en/latest/
[uv]: https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white
[uv-url]: https://docs.astral.sh/uv/
[venv-url]: https://docs.python.org/3/library/venv.html

[postgres]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white
[postgres-url]: https://www.postgresql.org/
[sqlite]: https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white
[sqlite-url]: https://sqlite.org/

[arc-url]: https://www.arc.gov.au/
[lief-url]: https://www.arc.gov.au/funding-research/funding-schemes/linkage-program/linkage-infrastructure-equipment-and-facilities
[grant-url]: https://dataportal.arc.gov.au/NCGP/Web/Grant/Grant/LE230100063
[adacs-url]: https://adacs.org.au/
[rsaa-url]: https://rsaa.anu.edu.au/
[anu-url]: https://www.anu.edu.au/
