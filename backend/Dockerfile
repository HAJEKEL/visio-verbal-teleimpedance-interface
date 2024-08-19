# Use an official Python 3 runtime as a parent image
FROM python:3.9

# Install ping, iproute2, and vim
RUN apt-get update && apt-get install -y \
    iputils-ping \
    iproute2 \
    vim \
    curl

# Install Ngrok
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
    | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
    | tee /etc/apt/sources.list.d/ngrok.list \
    && apt-get update \
    && apt-get install -y ngrok

# Copy the .env file into the container
COPY .env /app/

# Set up Ngrok authtoken using an environment variable from .env file
RUN export $(cat /app/.env | xargs) && ngrok config add-authtoken ${NGROK_AUTH_TOKEN}

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "ngrok http 8000 & uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]