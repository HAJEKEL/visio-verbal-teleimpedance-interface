# Use an official Python 3 runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application
CMD ["python3", "app.py"]
