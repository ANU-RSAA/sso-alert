FROM python:3.12
#LABEL maintainer="llindstrom@lco.global"

# the exposed port must match the deployment.yaml containerPort value
EXPOSE 8080
ENTRYPOINT [ "../sso_tom/start_within_container.sh"]
RUN apt-get update -y
RUN apt-get install vim -y
RUN apt-get install cron -y

WORKDIR /code

COPY requirements.txt /code
RUN pip install --upgrade pip && pip install --no-cache-dir -r /code/requirements.txt

# continue to setup the image with node and npm install (via nvm)
# see https://stackoverflow.com/questions/25899912/

# Use bash for subsequent RUN, CMD, ENTRYPOINT commands
SHELL ["/bin/bash", "--login", "-c"]

ENV NVM_DIR /usr/local/nvm
RUN mkdir -p $NVM_DIR
ENV NODE_VERSION 14.17.0

# Install nvm with node and npm
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.38.0/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

COPY . /code
RUN pip install --no-cache-dir tom_fink

RUN python manage.py collectstatic --noinput
