# astrobot Dockerfile
#
# This file is used to create the docker container for the astrobot client.
# The resulting container is then intended to be used with a server-specific docker-compose file. (a template can be found in /templates/docker-compose.yml)
#
# we base our image on the debian bullseye-based python image
FROM python:slim-bullseye

# set working directory variable for use a couple lines later
ARG workdir=/astrobot
# move astrobot files to container
COPY . /astrobot/
# create workdir
WORKDIR $workdir
# create log directory
RUN ["mkdir", "logs"]
ENV LOG_DIR=$workdir/logs

#update apt package cache
RUN ["apt", "update"]
# install postgres and wget
RUN ["apt", "install", "-y", "postgresql", "wget"]
# download waiter script and make executable
RUN ["wget", "https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh"]
RUN ["chmod", "+x", "wait-for-it.sh"]
# install required python dependencies
RUN ["pip", "install", "-r", "requirements.txt"]