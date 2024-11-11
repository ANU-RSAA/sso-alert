# DEPLOYMENT INSTRUCTIONS ROCKY LINUX 9

## Requirements

Rocky Linux 9 VM

## Setup the the DNS entry

Let's assume we are calling this VM ssoalert-test.adacs-dev.cloud.edu.au

On Nectar we go do DNS/Zones and "Create Record Set" for adacs-dev.cloud.edu.au.  add ssoalert-test.adacs-dev.cloud.edu.au. with its IP address.

You should have a different domain name setup which should replace the above for the rest of the instructions.


## After login in to the VM (via ssh)

```
$ dnf install git
```
```
$ git clone ... (clone repository)
```

## Preparing rocky linux
```
$ sudo dnf install langpacks-en glibc-all-langpacks -y
```
```
$ sudo localectl set-locale LANG=en_US.UTF-8
```

## Installing docker
```
$ sudo dnf check-update
$ sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
$ sudo dnf install docker-ce docker-ce-cli containerd.io
$ sudo systemctl start docker
$ sudo systemctl status docker
$ sudo systemctl enable docker
$ sudo usermod -aG docker $(whoami)
```

## Author .env and bring up the docker compose services
```
$ cd ui/sso_tom
```

create a file ".env" and add the appropriate values as we have done on https://ssoalert.adacs-dev.cloud.edu.au/
except ensure that the SITE_URL is updated to point to this site.

| variable                       | test depolyment                                          |
|--------------------------------|----------------------------------------------------------|
| SECRET_KEY                     | Y0ur$ecretKeyIncludingSymbols#$%$^%                      |
|                                |                                                          |
| ADACS_PROPOSALDB_TEST_PASSWORD | xxxx                                                     |
| ADACS_PROPOSALDB_TEST_USERNAME | alertproxy                                               |
|                                |                                                          |
| FINK_CREDENTIAL_USERNAME       | ssoas_test                                               |
| FINK_CREDENTIAL_GROUP_ID       | ssoas_1                                                  |
| FINK_CREDENTIAL_URL            | 134.158.74.95:24499                                      |
| FINK_TOPIC                     | fink_sso_fink_candidates_zt                              |
| FINK_MAX_POLL_NUMBER           | 2                                                        |
| FINK_TIMEOUT                   | 10                                                       |
|                                |                                                          |
| DEVELOPMENT_MODE               | False                                                    |
| SITE_URL                       | https://ssoalert-test.adacs-dev.cloud.edu.au (update it) |
| SITE_DOMAIN_NAME               | ssoalert-test.adacs-dev.cloud.edu.au (update it)         |
| SERVER_EMAIL                   | noreply@supercomputing.swin.edu.au (update it)           |
|                                |                                                          |
| EMAIL_HOST                     | mail.swin.edu.au (update it)                             |
| EMAIL_FROM                     | xxxx                                                     |
| EMAIL_PORT                     | 25                                                       |
|                                |                                                          |
| DATABASE_NAME                  | ssoalerts                                                |
| DATABASE_USER                  | sso                                                      |
| DATABASE_PASSWORD              | xxxx                                                     |

The following were used for local testing in the .env file

```
SITE_URL=http://192.168.122.77
SITE_DOMAIN_NAME=192.168.122.77
```

When ready bring up the docker service using the following command:

```
$ ./run_docker_build_and_launch.sh
```

Alternatively, while you are in the `ui/sso_tom/` directory, you can run:

```
$ docker system prune
$ docker compose build --no-cache
$ docker compose up -d
```

## Configure Nginx Proxy manager

Using a web browser navigate to port 81.
```
http://ssoalert-test.adacs-dev.cloud.edu.au:81/ # when you have a domain set up.
```

```
http://192.168.122.77:81/ # I could use to test if that works for my local testing.
```

For the first time login use "admin@example.com" as the username and "changeme" as the password.
Then enter the side administrator's email address as the new username and assign a new password for future logins.

1. Add domain name for this site to create a lets encrypt SSL certificate
2. Add a proxy server where that SSL certicate is set the proxy to forward Scheme(http) to Forward Hostname (demo) and Foward Port (8080)

See the [NGINX Guide](https://nginxproxymanager.com/guide/) for more details on now to operate the Nginx Proxy Manager web UI.

## Finalise the installation
Often the postresql database does not initialise fully until the second time the docker container is brought up.

```
$ docker compose down
$ ./run_docker_build_and_launch.sh
```

## Create a superuser

```
$ docker exec -it a1 /bin/bash
```

Inside the container, run the following command and follow the prompt to create a superuser.

```
python manage.py createsuperuser
```

I did this for testing:
```
Username (leave blank to use 'root'): superuser
Email address: non-existent@sso-alert.service
Password: 
Password (again): 
Superuser created successfully.
```
For password, I used the root user password that was supplied to me to login to the VM.

Test the depolyment by navigating to its home page at https://ssoalert-test.adacs-dev.cloud.edu.au/ or http://192.168.122.77:8080 for local deployment

## Set up the cronjobs

```
$ mkdir readstreams_output
$ vi run_readstreams.sh 
```

#### paste the following in the run_readstreams.sh
```
#!/bin/bash

# Define variables
BASE_DIR="$HOME/readstreams_output"
DATE_DIR=$(date '+%Y-%m-%d')
OUTPUT_DIR="$BASE_DIR/$DATE_DIR"
LOG_FILE="$OUTPUT_DIR/readstreams_$(date '+%H%M').log"

# Create the date-based subdirectory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Run the command and save the output
docker exec a1 python manage.py readstreams >> $LOG_FILE 2>&1
```

$ chmod +x $HOME/run_readstreams.sh 

$ mkdir updatestatus
$ vi run_updatestatus.sh 

#### paste the following in the run_updatestatus.sh
```
#!/bin/bash

OUTPUT_DIR="$HOME/updatestatus"
LOCK_FILE="/tmp/run_updatestatus.lock"

mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="$OUTPUT_DIR/updatestatus_output_$(date +\%Y\%m\%d_\%H\%M\%S).log"
EXIT_LOG_FILE="$OUTPUT_DIR/updatestatus_exit_$(date +\%Y\%m\%d_\%H\%M\%S).log"

if [ -e "$LOCK_FILE" ]; then
    echo "$(date +\%Y-\%m-\%d \%H:\%M:\%S) - Previous Script is already running. Exiting." >> "$EXIT_LOG_FILE"
    exit 1
fi

touch "$LOCK_FILE"

docker exec a1 python manage.py updatestatus > "$OUTPUT_FILE" 2>&1

rm -f "$LOCK_FILE"
```

$ chmod +x $HOME/run_updatestatus.sh 

$ crontab -e

#### put these two lines at the end of the file
```
*/5 * * * * $HOME/run_readstreams.sh
0 */2 * * * $HOME/run_updatestatus.sh
```

#### output should be:
crontab: installing new crontab
