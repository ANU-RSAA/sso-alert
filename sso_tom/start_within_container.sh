#!/bin/bash
cron -f &
crontab << !
* * * * * touch /code/cron_check
!
python manage.py migrate
python manage.py runserver 0.0.0.0:8080
