# SSO Alert System UI Prototype

This is a prototype for the User Interface of the Siding Spring Observatory's Alert System.

**NOTE: This prototype is being actively developed.**

## Built with

![Django]
![tom]

## Installation

To run the prototype locally, please follow the below instructions.
```
cd <repo_location>
git clone git@gitlab.com:CAS-eResearch/external/sso-alert/ui.git
python3 -m venv <env_name>
source <env_name>/bin/activate
python3 -m pip install -r ui/requirements.txt 
python ui/sso_tom/manage.py runserver
```

## Run project
```
python ui/sso_tom/manage.py runserver
```
The project will now be available at http://localhost:8000/

<!-- Markdown links and images -->

[django]: https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white
[tom]: https://avatars.githubusercontent.com/u/39539400?s=48&v=4
