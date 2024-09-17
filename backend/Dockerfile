# Use an official Python 3 runtime as a parent image
FROM python:3.9

# In dockerfiles we use apt-get to install packages instead of 
# apt because apt-get is more low-level and suitable for scripting



# Always run apt-get update because docker will otherwise use a cached version of the package list which may be outdated                    
# The -y flag is used to automatically answer yes to all prompts
# The \ character is used to split the command into multiple lines for version control purposes
# The rm -rf command is used to remove the package lists to reduce the image size and to force the Dockerfile author to use the apt-get update command to fetch the latest package lists at the start of the installation process

# General packages for debugging and development:
RUN apt-get update && apt-get install -y \ 
    vim \
    curl \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Packages for networking and debugging:
RUN apt-get update && apt-get install -y \ 
    iputils-ping \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Packages for video streaming from container to host
RUN apt-get update && apt-get install -y \ 
    x11-apps \ 
    && rm -rf /var/lib/apt/lists/*

# Packages for debugging and development:
RUN apt-get update && apt-get install -y \
    ffmpeg \ 
    && rm -rf /var/lib/apt/lists/*

# Packages for audio device host
RUN apt-get update && apt-get install -y \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Copy the .tmux.conf file to the home directory of the container
COPY .tmux.conf /root/.tmux.conf

# Create a non-root user
ARG USERNAME=henk
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
  && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
  # Create a home directory and a config directory for the user as some programs expect these to exist
  && mkdir /home/$USERNAME/.config && chown $USER_UID:$USER_GID /home/$USERNAME/.config 


# Add the user to the sudo group and allow it to run sudo commands without a password 
RUN apt-get update \
&& apt-get install -y sudo \
&& echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME\
&& chmod 0440 /etc/sudoers.d/$USERNAME \
&& rm -rf /var/lib/apt/lists/*

# Create the PulseAudio configuration directory for the user
RUN mkdir -p /home/$USERNAME/.config/pulse \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME/.config/pulse

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

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application and save ngrok URL to a file
# CMD ["sh", "-c", "ngrok http 8000 > ngrok_url.txt & uvicorn main:app --reload"]


# Copy the entrypoint and bashrc scripts so we have 
# our container's environment set up correctly
COPY entrypoint.sh /entrypoint.sh



# Set up entrypoint and default command
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["bash"]


# Make the container run as the non-root user
USER $USERNAME
