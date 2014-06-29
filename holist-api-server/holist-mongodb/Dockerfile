# DOCKER-VERSION 1.0.1

##############################
### The mongoDB container. ###
##############################

FROM ubuntu:14.04
MAINTAINER Robert Weindl <robert.weindl@blackstack.net>

# Import MongoDB public GPG key AND create a MongoDB list file.
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
RUN echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/10gen.list

# Update apt-get sources AND install MongoDB.
RUN apt-get -qq -y update
RUN apt-get -qq -y upgrade
RUN apt-get install -y -q mongodb-org

# Create the default data directory.
RUN mkdir -p /data/db

# Create the default logs directory and create a log file.
RUN mkdir -p /data/log
RUN touch /data/log/db.dat

# Define mountable volumes.
VOLUME ["/data/db"]
VOLUME ["/data/log"]

# Expose ports if neccessary.
EXPOSE 27017

# Create the administrative user.
# CMD /usr/bin/mongod --eval "use admin; db.createUser({ user: "root", pwd: "toor", roles: ["root"]})"

# Default port to execute the entrypoint (MongoDB).
#CMD ["--port", "27017", "--dbpath, "/data/db", "--smallfiles"]
CMD /usr/bin/mongod --port 27017 --dbpath /data/db --smallfiles --logpath /data/log/db.dat --logappend

# Set default container command.
#ENTRYPOINT mongod
