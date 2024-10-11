# Use an official Node.js 18.7.0 runtime as a parent image
FROM node:18.7.0

# Set the working directory in the container
WORKDIR /app

# Remove the pre-installed Yarn version
RUN npm uninstall -g yarn

# Install the specified version of Yarn (1.22.19)
RUN npm install -g yarn@1.22.19 --force

# Install the specified version of ts-node (10.9.1)
RUN npm install -g ts-node@10.9.1

# Expose the application port (optional, depending on your app)
EXPOSE 3000
EXPOSE 5173