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
    - [Introduction to Kubernetes](#introduction-to-kubernetes)
    - [Kubernetes Concepts](#kubernetes-concepts)
    - [Kubernetes Components](#kubernetes-components)
    - [EKS: Amazon Elastic Kubernetes Service](#eks-amazon-elastic-kubernetes-service)
    - [Creating an EKS Cluster via Web Console](#creating-an-eks-cluster-via-web-console)
    - [eksctl](#eksctl)
    - [kubectl](#kubectl)
    - [Creating Kubernetes Resources via CLI](#creating-kubernetes-resources-via-cli)
  - [Deployment Using CI/CD: CloudFormation + CodeBuild + CodePipeline](#deployment-using-cicd-cloudformation--codebuild--codepipeline)
  - [Extra: Deployment Using Terraform + Github Actions](#extra-deployment-using-terraform--github-actions)
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

- The Python environment includes the PyPI `awscli` package (AWS CLI v1). For the SSO workflow below, install [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) separately and ensure it takes precedence on `PATH`. Boto3 is the Python SDK (Software Development Kit); it does not install the CLI.
- On this machine, CLI v2 is already installed at `C:\Program Files\Amazon\AWSCLIV2\aws.exe`. A broken Poetry-environment command currently shadows it on `PATH`; the commands below select the working installation for this terminal. If needed, fix the persistent Windows `PATH` order and reopen the terminal.
- Use a named profile such as `course`. For IAM (Identity and Access Management) Identity Center, use SSO (single sign-on); otherwise use the credentials supplied for the course or an IAM user. Boto3 uses the same profile and credential files. Keep credentials out of source files and Git.
  - SSO means Single Sign-On: you sign in through a central login system to access multiple applications or AWS accounts. **We should use the SSO for our everyday access instead of the root account.**
  - Sign in as root and enable MFA (multi-factor authentication).
  - Set up your everyday access through IAM Identity Center (SSO) or an IAM user.
    - We get a dedicated access URL: `https://<your-portal>.awsapps.com/start`
  - Sign out of root, then use that identity to create and manage resources.

To enable SSO:

```text
AWS Console (initial setup as root): https://console.aws.amazon.com
  Open: IAM Identity Center
  Select the region where Identity Center is configured
  Enable it if needed
    Use an organization instance with multi-account permissions

Left panel -> Users
  If no user exists -> Add user
    Enter username, email, and name
    Select the option to send an invitation email
    Accept the invitation and set a password

Left panel -> AWS accounts
  Select your AWS account
  Assign users or groups -> Users
    Select your existing/new user
  Select permission sets -> Create permission set
    Predefined permission set -> AdministratorAccess
    Session duration: 1 hour
    Relay state: leave blank
    Create
  Return to the assignment workflow
    Select AdministratorAccess
    Complete the assignment and wait for success

Dashboard -> Copy the AWS access portal URL: https://<your-portal>.awsapps.com/start
  Open it in a private browser window
  Sign in using your SSO credentials
  Your account should appear as Mikel / account ID
    Expand it -> AdministratorAccess -> Open AWS Console
  If no accounts appear:
    Confirm the user/account/permission-set assignment completed
    Sign out of the portal and sign back in

After confirming SSO access works:
  Sign out of the root console session
  Use the access portal for subsequent console sign-ins
    https://<your-portal>.awsapps.com/start
    Account > AdministratorAccess > Open AWS Console
```

To configure the CLI with the SSO authentication, follow the steps below:

```powershell
# Only if CLI v2 is missing: install using AWS's Windows installer, then reopen the terminal
# msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
# Alternative: install it via pip:
# uv pip install awscli --upgrade

# Check which aws commands Windows finds; prioritize CLI v2 in this terminal
Get-Command aws -All
$env:PATH = "C:\Program Files\Amazon\AWSCLIV2;" + $env:PATH
aws --version
# Expected prefix: aws-cli/2

# Choose ONE authentication method
# Opetion A: IAM Identity Center (requires your organization's SSO access details)
# One-time setup: saves the SSO settings as a local profile named course
# During setup, the CLI opens your browser.
# Sign in there with your SSO credentials and approve access
# ~/.aws/config: profile saved, portal URL, SSO region, account ID, role, and default region
# ~/.aws/sso/cache/: Cached SSO tokens
# ~/.aws/cli/cache/: Cached temporary role credentials
aws configure sso --profile deployment-course
# SSO session name (Recommended): deployment-course-sso
# SSO start URL [None]: https://<your-portal>.awsapps.com/start
# SSO region [None]: <your-sso-region>, e.g. eu-central-1
# SSO registration scopes [sso:account:access]: <ENTER>
# Web is opened, we log in with our SSO credentials and approve access
# After that, we can always log is as follows:
aws sso login --profile deployment-course
# Repeat the login command when the SSO session expires
# To log out:
# aws sso logout

# Verify access
aws sts get-caller-identity --profile deployment-course

# Option B: access keys supplied for your account/course, entered interactively
# aws configure --profile deployment-course
# For temporary credentials, also set the supplied session token interactively:
# aws configure set aws_session_token (Read-Host "Session token") --profile deployment-course
# Refresh all temporary credentials when they expire

# Select the same profile for CLI commands and Boto3 in this terminal
# And/or add it to .env
$env:AWS_PROFILE = "deployment-course"
# Bash equivalent: export AWS_PROFILE=deployment-course

# Choose your deployment region (example: Frankfurt) and JSON output
aws configure set region eu-central-1 --profile deployment-course
aws configure set output json --profile deployment-course

# Verify authentication; these commands do not create cloud resources
aws sts get-caller-identity --profile deployment-course
uv run python -c "import boto3; s = boto3.Session(profile_name='deployment-course'); print(s.client('sts').get_caller_identity()['Arn'])"
```

AWS stores profiles under `~/.aws/config` and access-key credentials under `~/.aws/credentials`. `python-dotenv` reads `.env` only when your application calls `load_dotenv()`; AWS tools do not automatically load that file. See the [AWS profile and SSO guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html).

Here, we use the SSO authentication to configure the AWS CLI. Later, in section [AWS CLI Configuration](#aws-cli-configuration) we see how to create a dedicated user to configure the AWS CLI, which is the best practice.

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

### Introduction to Kubernetes

- Containers package applications, but running them individually on one machine makes scaling, updates, and capacity management difficult.
- **Vertical scaling** gives a machine or workload more CPU and memory. It can be difficult to adjust automatically, and large machines may cost more or sit underused.
- **Horizontal scaling** runs more application instances across machines. Container images make it practical to add or remove copies as demand changes.
- **Kubernetes** is an open-source container orchestration platform, originating at Google and open-sourced in 2014. It automates deploying, scaling, and managing containerized applications.
  - Manages multiple containers across machines and helps match running workloads to their desired state.
  - Supports horizontal scaling, load balancing, service discovery, networking, and health checks.
  - Provides high availability, automated updates, container health management, and configuration and secret management.
  - Cloud resources can provide additional capacity when local or on-premises servers are insufficient; Kubernetes itself does not make infrastructure unlimited.
  - Its broad feature set and ecosystem bring operational complexity and a learning curve.
- Further reading: [Scaling containerized apps at Google](https://queue.acm.org/detail.cfm?id=2898444) and the [Kubernetes overview](https://kubernetes.io/docs/concepts/overview/).

![Horizontal Scaling](./assets/horizontal_scaling.png)

### Kubernetes Concepts

- A **Kubernetes cluster** is a set of machines managed together. Its **control plane** coordinates the cluster; older material often calls this the *master*.
- **Nodes** are the virtual or physical worker machines where workloads run. The control plane schedules Pods on nodes based on available resources; a node can run multiple Pods and needs a supported container runtime.
- A **Pod** is Kubernetes’ smallest deployable unit and contains one or more closely related containers.
  - Containers in a Pod share its network namespace and can share mounted volumes.
  - Each Pod has its own cluster IP, but Pods are ephemeral: they can be replaced, moved, or removed during scaling and recovery.
- A **Service** selects a set of Pods and provides a stable way to reach them as individual Pod IPs change. It can distribute traffic across matching Pods.
- A **Volume** provides storage mounted into one or more containers in a Pod. Pod-local ephemeral storage does not survive Pod replacement; use persistent storage when data must outlive a Pod.
- Replicating application Pods across nodes can reduce dependence on a single node and improve availability, provided the cluster and application are configured for it.
- Common workflow: create a cluster, deploy an application, expose its ports through a Service, then scale or update the application.
- Cluster options:
  - Run a local cluster for development. Docker Desktop is one option when Kubernetes is enabled.
  - Use a cloud provider's managed service. This course uses **Amazon EKS (Elastic Kubernetes Service)**; other examples include Google Kubernetes Engine (GKE) and Azure Kubernetes Service (AKS).
- For hands-on learning, see:
  - the [Kubernetes cluster introduction](https://kubernetes.io/docs/tutorials/kubernetes-basics/create-cluster/cluster-intro/)
  - and the [interactive cluster tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/create-cluster/cluster-interactive/).

![Kubernetes Cluster](./assets/k8s_cluster.png)

![Kubernetes App Service](./assets/k8s_app_service.png)

![Kubernetes Basic Workflow](./assets/kubernetes_basic_workflow.png)

More information:

- [Kubernetes cluster components overview](https://kubernetes.io/docs/concepts/overview/components/)
- [Pods documentation](https://kubernetes.io/docs/concepts/workloads/pods/)

### Kubernetes Components

- A cluster contains the **control plane**, which manages the cluster, and **worker nodes**, which run application Pods. In managed services such as EKS, the provider manages the control plane.
- **Control plane components:**
  - `kube-apiserver` exposes the Kubernetes API. Users, cluster components, and tools communicate with the cluster through it; it serves requests to read or change objects such as Pods, Namespaces, ConfigMaps, and Events.
  - `etcd` stores the cluster's state and data as a consistent, highly available key-value store.
  - `kube-scheduler` watches for Pods that have no assigned node and selects a node for each.
  - `kube-controller-manager` runs controllers that observe cluster state and work to move it toward the desired state.
  - `cloud-controller-manager` integrates Kubernetes with a cloud provider's APIs; it is used when the cluster needs cloud-specific control logic.
- **Node components:**
  - `kubelet` runs on each node and ensures assigned Pods and their containers are running as specified.
  - A **container runtime** runs the containers. Kubernetes uses a compatible runtime such as containerd or CRI-O; Docker Engine is no longer directly integrated through Kubernetes' removed dockershim.
  - `kube-proxy`, when used by the cluster, maintains node network rules that support communication to Services and their Pods.

![Kubernetes components](./assets/k8s_components.png)

References: [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/) and the [Kubernetes API](https://kubernetes.io/docs/concepts/overview/kubernetes-api/).

### EKS: Amazon Elastic Kubernetes Service

- **Amazon EKS** is AWS's managed Kubernetes service. AWS operates the Kubernetes control plane, including its availability across multiple Availability Zones (AZs) and control plane maintenance.
- The cluster's **data plane** runs application Pods on compute nodes. You choose and manage the compute approach, such as managed node groups or Fargate; autoscaling requires configuring the appropriate cluster and workload scaling.
- EKS connects the Kubernetes cluster with AWS networking and services. You still configure worker capacity, application deployments, Services, permissions, and access to AWS resources.
- Managed control plane availability does not automatically make application workloads highly available. Run enough replicas across AZs and configure storage, networking, backups, and recovery for your needs.
- AWS manages control plane backups and recovery mechanisms, but you remain responsible for protecting application data and planning workload recovery.
- Further reading: [What is Amazon EKS?](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html).

### Creating an EKS Cluster via Web Console

### eksctl

### kubectl

### Creating Kubernetes Resources via CLI

## Deployment Using CI/CD: CloudFormation + CodeBuild + CodePipeline

:construction:

## Extra: Deployment Using Terraform + Github Actions

:construction:

## Project: Deploy Your Flask App to Kubernetes Using EKS

:construction:
