FROM python:3.11
#LABEL maintainer="llindstrom@lco.global"

# the exposed port must match the deployment.yaml containerPort value
EXPOSE 8080
#ENTRYPOINT [ "/usr/local/bin/gunicorn", "sso_tom.wsgi:application", "-b", "0.0.0.0:8080", "--access-logfile", "-", "--error-logfile", "-", "-k", "gevent", "--timeout", "300", "--workers", "2"]
ENTRYPOINT [ "python", "manage.py", "runserver", "0.0.0.0:8080"]
RUN apt-get update -y
RUN apt-get install vim -y

WORKDIR /code

COPY requirements.txt /code
RUN pip install --upgrade pip && pip install --no-cache-dir -r /code/requirements.txt
COPY patch-for-forms.py /usr/local/lib/python3.9/site-packages/tom_dataproducts/forms.py
COPY patch-for-fink.py /usr/local/lib/python3.9/site-packages/tom_alerts/brokers/fink.py

# continue to setup the image with node and npm install (via nvm)
# see https://stackoverflow.com/questions/25899912/

# Use bash for subsequent RUN, CMD, ENTRYPOINT commands
SHELL ["/bin/bash", "--login", "-c"]

ENV NVM_DIR /usr/local/nvm
RUN mkdir -p $NVM_DIR
ENV NODE_VERSION 14.17.0

# Install nvm with node and npm
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.38.0/install.sh | bash \
    && source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

COPY . /code

# write new webpack-stats.json for django-webpack-loader to use
# and install the Vue JS/CSS etc as static files
#WORKDIR /code/vue
#RUN npm install && npm run build

RUN python manage.py collectstatic --noinput
