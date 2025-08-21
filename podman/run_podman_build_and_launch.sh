#!/bin/bash
set -x
#
# The location with the docker-compose.yml file
BASE_DIR=/opt/ssoalert/sso-alert/podman

if [ ! -d ${BASE_DIR} ]
then
        echo "Error: ${BASE_DIR} does not exist."
        exit 1
fi
cd ${BASE_DIR}

# the following volumes in this directory are persistent
# ./data for nginx-proxy-manager
# ./letsencrypt for nginx-proxy-manager letsencrypt
# ./postgresql/data for postgres database
# ./ for django appication building (See Dockerfile)
podman system prune -f
podman compose up --build --remove-orphans --force-recreate > staging.txt 2>&1 &

IMAGE_NAME=sso_tom_demo
CONTAINER_ID=""
i=0
while [ ${i} -le 60 -a "${CONTAINER_ID}" = "" ]
do
    echo "Waiting for container ID to appear..."
    sleep 5
    CONTAINER_ID=$(podman ps --all --filter ancestor=${IMAGE_NAME} --format="{{.ID}}" | head -n 1)
    i=$(expr 1 + ${i})
done
if [ "${CONTAINER_ID}" = "" ]
then
    echo "Error: Failed to locate container ID for ${IMAGE_NAME}"
    exit 1
else
    echo "${IMAGE_NAME} has container ID ${ONTAINER_ID}"
fi

CONTAINER_STATUS=""
i=0
while [ ${i} -le 60 -a "${CONTAINER_STATUS}" != '"running"' ]
do
    echo "Waiting for container to start..."
    sleep 5
    CONTAINER_STATUS=$(podman inspect --format "{{json .State.Status }}" ${CONTAINER_ID})
    i=$(expr 1 + ${i})
done
if [ "${CONTAINER_STATUS}" != '"running"' ]
then
    echo "Error: container status non running - ${CONTAINER_STATUS}"
    exit 1
fi
echo CONTAINER READY FOR INITIALIZATION
sleep 45
#only need to do this the very first time docker compose comes up since we are using volumes now
if [ ! -f ${BASE_DIR}/.tom_demo_postgres_created ]
then
    echo "First run: creating postgresql DB for tom_demo. (touch ${BASE_DIR}/.tom_demo_postgres_created)"

    podman exec -i postgres-pod /bin/bash << !
createdb -U postgres tom_demo
exit
!
    touch ${BASE_DIR}/.tom_demo_postgres_created
fi

podman exec -i sso-alert-pod /bin/bash << !
python manage.py migrate
exit
!
echo READY