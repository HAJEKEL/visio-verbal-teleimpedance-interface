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

# Install Ngrok to expose the frontend server to the internet
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
    | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
    | tee /etc/apt/sources.list.d/ngrok.list \
    && apt-get update \
    && apt-get install -y ngrok

# Install sudo and configure the 'node' user for passwordless sudo
RUN apt-get update \
    && apt-get install -y sudo \
    && echo "node ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/node \
    && chmod 0440 /etc/sudoers.d/node \
    && rm -rf /var/lib/apt/lists/*

# Switch to the non-root 'node' user
USER node

# Copy the .env file into the container
COPY .env /app/.env
