# Server Deployment and Containerization

These are my notes after following the Udacity course [Server Deployment and Containerization (Udacity Course)](https://www.udacity.com/course/server-deployment-and-containerization--cd0157).

See also my previous notes on [Docker & Kubernetes](https://github.com/mxagar/tool_guides/blob/master/docker_swarm_kubernetes/docker_swarm_kubernetes_howto.md).

The [Udacity course repository](https://github.com/udacity/cd0157-Server-Deployment-and-Containerization) is included as a Git submodule in [`lab/udacity_server_deployment_exercises/`](./lab/udacity_server_deployment_exercises/). It contains additional course exercises and is pinned to a specific upstream commit.

The submodule was added from this repository's root with:

```bash
git submodule add https://github.com/udacity/cd0157-Server-Deployment-and-Containerization.git 01_ServerDeployment/lab/udacity_server_deployment_exercises
```

To download the exercises after cloning this guide, run from the repository root:

```bash
git submodule update --init --recursive 01_ServerDeployment/lab/udacity_server_deployment_exercises
```

Alternatively, use `git clone --recurse-submodules <guide-repository-url>` when cloning this guide to download all its submodules.

Table of Contents:
- [Server Deployment and Containerization](#server-deployment-and-containerization)
  - [Introduction](#introduction)
    - [Container and Deployment Overview](#container-and-deployment-overview)
    - [Environment Setup](#environment-setup)
      - [AWS CLI and Credentials](#aws-cli-and-credentials)
  - [Containers](#containers)
    - [Introduction](#introduction-1)
    - [Docker Concepts](#docker-concepts)
    - [DockerHub Example: Pull and Run PostgreSQL](#dockerhub-example-pull-and-run-postgresql)
    - [Dockerfiles](#dockerfiles)
    - [Dockerfile Exercises](#dockerfile-exercises)
      - [Simple Flask App](#simple-flask-app)
      - [Repository with More Exercises](#repository-with-more-exercises)
  - [AWS and Kubernetes](#aws-and-kubernetes)
    - [Introduction to Kubernetes and Project Overview](#introduction-to-kubernetes-and-project-overview)
    - [AWS Resources and Cost](#aws-resources-and-cost)
    - [AWS Setup](#aws-setup)
  - [Deployment Using CI/CD](#deployment-using-cicd)
  - [Project: Deploy Your Flask App to Kubernetes Using EKS](#project-deploy-your-flask-app-to-kubernetes-using-eks)

## Introduction

Pre-requisites (knowledge in):

- HTML and CSS
- HTTP Requests and Routes
- RESTful APIs
- Identity and Access Management
- Python or Javascript Programming: Writing functions, logic, control flow
- Using the Terminal
- Version control in Git and using GitHub
- Relational databases and SQL
- Postgres SQL
- Object-Relational Mappers with SQLAlchemy

### Container and Deployment Overview

> - A container is a running piece of software that bundles code along with all of its dependencies, including system tools, libraries, or configuration files. We use [Docker](https://www.docker.com/) to create containers.
> - [Kubernetes](https://kubernetes.io/) is a container orchestration system that automates container deployment, scaling, and management and will be used in this course.

![Container and Deployment Overview](./assets/docker_kubernetes_overview.png)

### Environment Setup

- Use [uv](https://docs.astral.sh/uv/) with Python 3.13 and the local [`pyproject.toml`](./pyproject.toml). It updates all packages from the course's `requirements.txt` and adds NumPy, pandas, Matplotlib, scikit-learn, python-dotenv (`import dotenv`), and Boto3.
- `pytest` is a development dependency, installed by default. Gunicorn is installed only on Unix systems; use Flask for local Windows exercises and Linux containers for Gunicorn.
- `uv.lock` records exact resolved versions. Keep it in version control; `.venv/` and `.env` are already ignored.

```powershell
# Run from this guide's repository root (PowerShell)
cd .../01_ServerDeployment

# Install Python 3.13 if needed, then create .venv and install locked dependencies
uv python install 3.13
uv sync --locked --python 3.13

# Run commands inside the environment without activating it
uv run python --version
uv run python lab/01_dockerfile_flask_app/app.py --port 8080
# Stop the app with Ctrl+C

# Optional: activate the environment to use python and pytest directly
.\.venv\Scripts\Activate.ps1
# In Bash on Linux/macOS/WSL: source .venv/bin/activate
# In Git Bash on Windows: source .venv/Scripts/activate
deactivate

# After intentionally editing dependencies, resolve and install the new versions
# uv lock
# uv sync --locked
# To refresh versions within the declared bounds: uv lock --upgrade
```

The upstream JWT exercise needs modernization with these dependencies: PyJWT 2.x returns a string from `jwt.encode()`, so remove `.decode('utf-8')` from the `/auth` response in `main.py` when adapting that exercise. The submodule and its old requirements are preserved. This environment does not change Docker builds; those use their own Dockerfile and dependency installation steps.

#### AWS CLI and Credentials

- Install [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) separately from the Python environment. Boto3 is the Python SDK (Software Development Kit); it does not install the CLI. Avoid adding the PyPI `awscli` package, which provides CLI v1.
- On this machine, CLI v2 is already installed at `C:\Program Files\Amazon\AWSCLIV2\aws.exe`. A broken Poetry-environment command currently shadows it on `PATH`; the commands below select the working installation for this terminal. If needed, fix the persistent Windows `PATH` order and reopen the terminal.
- Use a named profile such as `course`. For IAM (Identity and Access Management) Identity Center, use SSO (single sign-on); otherwise use the credentials supplied for the course or an IAM user. Boto3 uses the same profile and credential files. Keep credentials out of source files and Git.

```powershell
# Only if CLI v2 is missing: install using AWS's Windows installer, then reopen the terminal
# msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Check which aws commands Windows finds; prioritize CLI v2 in this terminal
Get-Command aws -All
$env:PATH = "C:\Program Files\Amazon\AWSCLIV2;" + $env:PATH
aws --version
# Expected prefix: aws-cli/2

# Choose ONE authentication method
# A: IAM Identity Center (requires your organization's SSO access details)
aws configure sso --profile course
aws sso login --profile course
# Repeat the login command when the SSO session expires

# B: access keys supplied for your account/course, entered interactively
# aws configure --profile course
# For temporary credentials, also set the supplied session token interactively:
# aws configure set aws_session_token (Read-Host "Session token") --profile course
# Refresh all temporary credentials when they expire

# Select the same profile for CLI commands and Boto3 in this terminal
$env:AWS_PROFILE = "course"
# Bash equivalent: export AWS_PROFILE=course

# Choose your deployment region (example: Frankfurt) and JSON output
aws configure set region eu-central-1 --profile course
aws configure set output json --profile course

# Verify authentication; these commands do not create cloud resources
aws sts get-caller-identity
uv run python -c "import boto3; print(boto3.client('sts').get_caller_identity()['Arn'])"
```

AWS stores profiles under `~/.aws/config` and access-key credentials under `~/.aws/credentials` (on Windows, `~` is your user directory). `python-dotenv` reads `.env` only when your application calls `load_dotenv()`; AWS tools do not automatically load that file. See the [AWS profile and SSO guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html).

## Containers

I will summarize most of this section, since I know already the topic.
Check my notes on [Docker & Kubernetes](https://github.com/mxagar/tool_guides/blob/master/docker_swarm_kubernetes/docker_swarm_kubernetes_howto.md) if you are insterested.

### Introduction

Key concepts:

- Containers
  - App dependencies bundled.
  - Lightweight.
  - Share/use OS resources (1 kernel, shared libraries).
- Containers vs Virtual Machines (VM)
  - VMs: higher overhead; fully running OS, no sharing.
  - They use a *hypervisor*, which handles the access to OS infrastructure.
  - AWS EC2 creates VMs.
- Docker: Open Source Container Solution + Company selling products around that.
  - Install Docker on Linux / Mac / Windows.

![Containers vs. VMs](./assets/containers_vs_vms.png)

![Container Deployments](./assets/container_deployments.png)

To check Docker installation:

```bash
# To check the version
docker version

# To verify that Docker can pull and run images
docker run hello-world 

# Run a container: open http://localhost:80
docker run -d -p 80:80 docker/getting-started
```

![Docker Getting Started: Tutorial](./assets/docker_getting_started.png)

### Docker Concepts

Key concepts:

- Image: immutable template of the container
  - Images are created with Dockerfiles
  - We can have *base images*, which gather common *layers* used by several children images
- Container: running image instance
- Registry (e.g., Docker Hub): where docker images are stored
- Volumes: attached to containers, so that data persists, since containers a re ephemeral
- Network: communication network between containers
- Docker Engine: application which consistes of
  - Daemon: server that manages images, containers, networks, volumes
  - Client: UI for Docker, used often via CLI
  - API


```bash
# This command will look for a Dockerfile in the `pwd`, and create myImage
docker build  --tag myImage  [OPTIONS] path_where_to_store_the_image 

# We pull the public image tomcat (tag: latest)
docker pull tomcat:latest

# We run an image -> container
docker run --name myContainer myImage
```

### DockerHub Example: Pull and Run PostgreSQL

[DockerHub](https://hub.docker.com/) is the largest, public docker image registry.

```bash
# -- Get PostgreSQL image
docker pull postgres:latest

# -- Create and run container
# --name: name for container
# --e: environment variables
# --p: publish port
# --d: detach, run in the background and return terminal
docker run --name psql -e POSTGRES_PASSWORD=password! -p 5433:5432 -d postgres:latest

# -- Connect to the PostgreSQL container with psql; pw: password! (the one passed via -e)
psql -h 127.0.0.1 -p 5433 -U postgres
# In psql
\l  # list all databases
\dti  # list all tables and relations
# More psql commands: https://www.postgresql.org/docs/current/app-psql.html
\q  @ quit

# -- Clean up
# List all containers
docker ps --all
# Stop
docker stop <container_ID>
# Remove
docker container rm <container_ID>

# -- Images
# List all images
docker image ls
# Remove
docker image rm <image_ID>
```

### Dockerfiles

A `Dockerfile` is a text document that contains all the commands to assemble an image. It allows you to automate the image creation process.

Typical `Dockerfile` instructions:

```Dockerfile
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
CMD ["--port", "8000"]
# Note: The CMD arguments can be overridden when running the container
# docker run myapp
# -> Runs: python app.py --port 8000
# docker run myapp --port 9000
# -> Runs: python app.py --port 9000
```

![Dockerfile: Build Image](./assets/docker_build_image.png)

To build and run the Docker image:

```bash
# Build the image
docker build -t myapp .

# Run the container
docker run --name myapp_container -p 8000:8000 myapp
```

For more details and commans, check the [`Dockerfile` reference](https://docs.docker.com/reference/dockerfile/).

### Dockerfile Exercises

#### Simple Flask App

Files in [`lab/01_dockerfile_flask_app/`](./lab/01_dockerfile_flask_app/):

- `app.py`: The Flask application script.
- `Dockerfile`: The Dockerfile to build the Flask app image.

```python
from flask import Flask
import argparse

# Flask app instance
app = Flask(__name__)

# Parse command-line arguments for the Flask app
args = argparse.ArgumentParser()
args.add_argument('--port', type=int, default=8080)

@app.route('/')
def hello_world():
    return "Hello, World -- from Flask!"

if __name__ == '__main__':
    # Parse command-line arguments
    parsed_args = args.parse_args()
    port = parsed_args.port

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=True)
```

```Dockerfile
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
# -> Runs: python app.py --port 8080
# docker run myapp --port 9000
# -> Runs: python app.py --port 9000
```

To build and run the Docker image:

```bash
cd .../lab/01_dockerfile_flask_app

# Build the image
docker build -t myapp .

# Run the container
docker run --name myapp_container --rm -p 8080:8080 myapp
# --rm: automatically remove the container when it exits

# List all containers (including stopped ones) + clean up
docker ps -a
docker container stop <container_ID>
docker container rm <container_ID>
```

#### Repository with More Exercises

The [Udacity course repository](https://github.com/udacity/cd0157-Server-Deployment-and-Containerization) provides more exercises in [`lab/udacity_server_deployment_exercises/`](./lab/udacity_server_deployment_exercises/), included as a Git submodule pinned to a specific commit.

This repository is included as a submodule in the `01_ServerDeployment/lab/udacity_server_deployment_exercises/` directory.

Here, basically the same example as before is demonstrated using the submodule's Flask application.

```bash
# Use the Flask example already included in this guide's submodule
cd .../lab/udacity_server_deployment_exercises/examples/flask

# Build an image named test; -t means --tag, and . is the build context
# Docker uses the Dockerfile in this directory by default
# The upstream example uses the old python:3.7.2-slim base image
# For a modernized exercise, change its FROM line to python:3.13-slim first
# Editing upstream files creates local changes inside the submodule
docker build -t test .
docker image ls

# Run the container; map host port 80 to Flask's container port 8080
# This runs in the foreground; use another terminal for the commands below
docker run --name myContainer -p 80:8080 test

# In another terminal: request the app, or open http://localhost:80/ in a browser
curl http://127.0.0.1:80/

# If port 80 is busy, use -p 9090:8080 instead, then visit http://localhost:9090/

# List running containers, then stop and remove this exercise's container
docker ps
docker stop myContainer
docker container rm myContainer

# Optional: remove the image after removing the container
docker image rm test

# Show help for container commands
docker container help
```

## AWS and Kubernetes

### Introduction to Kubernetes and Project Overview

- Docker packages an application with its environment and dependencies. Cloud deployment also requires managing how its container instances run and scale.
- **Container orchestration** manages containers across multiple hosts.
  - Creates and removes instances as needed; automatic scaling requires configuration.
  - Handles load balancing, health checks, configuration, networking, and container lifecycle management.
  - This course uses **Kubernetes** for orchestration.
- A **CI/CD (continuous integration and continuous delivery) pipeline** connects a shared code repository to the target infrastructure.
  - Typical steps: compile code when needed, run tests, build deployable artifacts, and deploy releases.
  - **Continuous integration (CI)** automatically builds and tests code changes outside production.
    - This course uses **AWS (Amazon Web Services) CodeBuild**; Jenkins is another option.
  - **Continuous delivery (CD)** keeps tested changes ready for release through an automated pipeline. Production deployment can require approval.
    - **Continuous deployment** also automates the production release without manual approval.
    - This course uses **AWS CodePipeline** to coordinate the release stages and support frequent, incremental releases.
- **Lesson objectives:**
  - Deploy a containerized application using **Amazon EKS (Elastic Kubernetes Service)**, AWS's managed Kubernetes service.
  - Set up continuous integration with AWS CodeBuild.
  - Create a continuous delivery pipeline with AWS CodePipeline.

The project uses these components:
- **Amazon EKS** for Kubernetes orchestration.
- **AWS CodeBuild** for continuous integration.
- **AWS CodePipeline** for continuous delivery.
- **Docker** for containerizing the application.
- **Flask** as the web application framework.

![AWS and Kubernetes Project Overview](./assets/aws_kubernetes_project.png)

### AWS Resources and Cost

Contents:

- **AWS access setup**: how to sign in for course cloud work
- **Cost awareness**: AWS can incur charges if resources stay running; check [https://aws.amazon.com/pricing/](https://aws.amazon.com/pricing/).
  - Track costs: ` Billing and Cost Management > AWS Cost Explorer`.
- **Use course-provided resources**: follow the classroom instructions for credentials and access; we have a dedicated set of resources for the course (25 USD credits), accessible via `Cloud Resources`. We need to log out from any AWS accounts first.
- **Avoid surprise billing**: shut down or clean up services when you're done: EC2, Sagemaker, Database, EMR, CloudFormation.

However, I used my own AWS account for the course & the project.

### AWS Setup




## Deployment Using CI/CD

:construction:

## Project: Deploy Your Flask App to Kubernetes Using EKS

:construction:
