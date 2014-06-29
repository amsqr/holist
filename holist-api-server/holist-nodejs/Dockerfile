# DOCKER-VERSION 1.0.1

##############################
### The Node.js container. ###
##############################

FROM ubuntu:14.04

MAINTAINER Robert Weindl <robert.weindl@cdtm.de>

# Update aptitude
RUN apt-get -qq update
RUN apt-get -qq upgrade

# Install Node.js and npm
RUN apt-get install -y nodejs npm

# Create symbolic link to use Node.js with node command.
RUN ln -s /usr/bin/nodejs /usr/bin/node

# Bundle application source
ADD /src /src

# Clear the npm cache if needed. This command is commented out to provide faster deployment.
# RUN npm cache clean

# Install application dependencies.
RUN cd /src; npm install

# Expose all necessary ports.
EXPOSE 8080

# Run the node server.
CMD ["node", "/src/server.js"]
