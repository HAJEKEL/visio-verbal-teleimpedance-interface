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

# Copy the .env file into the container
COPY .env /app/.env

# Expose the application port (optional, depending on your app)
EXPOSE 3000
EXPOSE 5173
