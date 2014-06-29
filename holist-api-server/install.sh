#! /bin/sh

# Constants
readonly SCRIPT=$(cd "$(dirname "$0")"; pwd)
readonly USERNAME=holist

# Stop and remove the holist-nodejs container.
docker stop holistNodejs holistMongodb
docker rm holistNodejs holistMongodb

# Create a new directory to save and persist the data outside the MongoDB container.
sudo mkdir -p /var/db/holist-mongodb

# Create a new directory to save and persist the
sudo mkdir -p /var/log/holist-mongodb

# Remove the mongod.lock file if existing.
sudo rm -f /var/db/holist-nodejs/mongod.lock

# Build the holist-nodejs container.
docker build -t $USERNAME/holist-nodejs $SCRIPT/holist-nodejs

# Build the holist-mongodb container.
docker build -t $USERNAME/holist-mongodb $SCRIPT/holist-mongodb

# Run the MongoDB container.
# For exposing the port add '-p 27017'.
docker run -itd -p 49101:27017 -v /var/db/holist-mongodb:/data/db -v /var/log/holist-mongodb:/data/log --name holistMongodb $USERNAME/holist-mongodb

# Run the node.js container.
docker run -itd -p 49100:8080 --name holistNodejs --link holistMongodb:holistMongodb $USERNAME/holist-nodejs
