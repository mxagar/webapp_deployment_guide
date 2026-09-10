# Web-App Deployment Guide

- [`00_Self_Hosting_VPS/`](./00_Self_Hosting_VPS/): [Self-Hosting with Docker & Linux: Run Your Own Services (Udemy Course)](https://www.udemy.com/course/self-hosting-docker-linux/)
- [`01_ServerDeployment/`](./01_ServerDeployment/): [Server Deployment and Containerization (Udacity Course)](https://www.udacity.com/course/server-deployment-and-containerization--cd0157)
- [`02_Example_Deployments/`](./02_Example_Deployments/): Example Deployments.
- [`notes_webapp/`](./notes_webapp/): Sample note-taking application used in the deployment examples (Git submodule).

## Dummy Web App Submodule

The [`notes_webapp/`](./notes_webapp/) submodule contains a dummy note-taking web application used to test deployments across different hosting services.

Clone this repository with submodules enabled:

```bash
git clone --recurse-submodules <repository-url>
```

If you already cloned the repository, initialize and download the submodule with:

```bash
git submodule update --init --recursive
```

## Authorship

Mikel Sagardia, 2026.  
No guarantees.  
