# Use an official Python 3 runtime as a parent image
FROM python:3.9

# Install ping, iproute2, and vim
RUN apt-get update && apt-get install -y \
    iputils-ping \
    iproute2 \
    vim \
    curl \
    tmux

# Copy the .tmux.conf file to the home directory of the container
COPY .tmux.conf /root/.tmux.conf

# Append the specified lines to the end of the .bashrc file
RUN echo '_tmux_sessions() {' >> /root/.bashrc && \
    echo '    local cur=${COMP_WORDS[COMP_CWORD]}' >> /root/.bashrc && \
    echo '    local sessions=$(tmux list-sessions -F "#S")' >> /root/.bashrc && \
    echo '    COMPREPLY=( $(compgen -W "${sessions}" -- ${cur}) )' >> /root/.bashrc && \
    echo '}' >> /root/.bashrc && \
    echo '' >> /root/.bashrc && \
    echo 'complete -F _tmux_sessions tmux attach-session -t' >> /root/.bashrc && \
    echo 'complete -F _tmux_sessions tmux switch-client -t' >> /root/.bashrc && \
    echo 'complete -F _tmux_sessions tmux kill-session -t' >> /root/.bashrc

# Install Ngrok to expose the FastAPI server to the internet
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
    | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
    | tee /etc/apt/sources.list.d/ngrok.list \
    && apt-get update \
    && apt-get install -y ngrok

# Copy the .env file into the container
COPY functions/.env /app/

# Set up Ngrok authtoken using an environment variable from .env file
RUN export $(cat /app/.env | xargs) && ngrok config add-authtoken ${NGROK_AUTH_TOKEN}

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install the specific version of openai for older functionalities (speech-to-text and response generation)
RUN pip install openai==0.27.0 --target=/app/openai_v0.27.0

# Install the latest version of openai for the latest features (text-to-speech)
RUN pip install openai --target=/app/openai_latest

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application and save ngrok URL to a file
# CMD ["sh", "-c", "ngrok http 8000 > ngrok_url.txt & uvicorn main:app --reload"]