#!/bin/bash
# the following volumes in this directory are persistent
# ./data for nginx-proxy-manager
# ./letsencrypt for nginx-proxy-manager letsencrypt
# ./postgresql/data for postgres database
# ./ for django appication building (See Dockerfile)
docker system prune -f
docker compose up --build --remove-orphans --force-recreate > staging.txt 2>&1 &

IMAGE_NAME=tom-demo-demo
CONTAINER_ID=$(docker ps --all --filter ancestor=${IMAGE_NAME} --format="{{.ID}}" | head -n 1)
echo CONTAINER_ID=${CONTAINER_ID}
until [ "${CONTAINER_ID}" != "" ]
do
    CONTAINER_ID=$(docker ps --all --filter ancestor=${IMAGE_NAME} --format="{{.ID}}" | head -n 1)
    echo "Waiting for container ID to appear..."
    sleep 5
done
CONTAINER_STATUS=$(docker inspect --format "{{json .State.Status }}" ${CONTAINER_ID})
until [ "${CONTAINER_STATUS}" == '"running"' ]
do
    echo "Waiting for container to start..."
    sleep 5
done
echo CONTAINER READY FOR INITIALIZATION
sleep 45
#only need to do this the very first time docker compose comes up since we are using volumes now
#docker exec -i a2 /bin/bash << !
#createdb -U postgres tom_demo
#exit
#!

docker exec -i a1 /bin/bash << !
python manage.py migrate
exit
!
echo READY

