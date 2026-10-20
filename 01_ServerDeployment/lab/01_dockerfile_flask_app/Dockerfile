# Base image
FROM python:3.13-slim

# Copy files from current directory to /app in the container
COPY . /app
# Set the working directory inside the container
WORKDIR /app

# RUN: run any shell command
RUN pip install --upgrade pip
RUN pip install flask

# ENTRYPOINT: set executable
# Assuming there is a Python script named app.py in the working directory
# and it accepts command-line arguments for configuration
ENTRYPOINT ["python", "app.py"]
# CMD: provide default arguments for the ENTRYPOINT
CMD ["--port", "8080"]
# Note: The CMD arguments can be overridden when running the container
# docker run myapp
# -> Runs: python app.py --port 8000
# docker run myapp --port 9000
# -> Runs: python app.py --port 9000
