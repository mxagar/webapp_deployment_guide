# Simple Web App Deployment Guide

A guide on how to deploy simple web apps on several cloud services.

## Goal

Create a small but realistic web application project for learning deployment concepts.

The focus is **not** machine learning infrastructure. The focus is deploying a conventional app that includes the resources many real applications need:

* a Python backend with Flask
* a simple frontend with HTML, CSS, and JavaScript
* a PostgreSQL database
* blob/object storage
* an API built with Flask
* containerization with Docker
* local orchestration with Docker Compose
* CI/CD for linting, tests, and deployment
* separate staging and production environments

ML functionality, if present, is treated as just another internal application feature.



## Project Scope

This project is meant to teach the deployment and operations fundamentals behind a typical small-to-medium web application.

It should help answer questions like:

* How do I package an app in Docker?
* How do I run it locally with its dependencies?
* How do I deploy it to a managed platform or VPS?
* How do I separate staging from production?
* How do I handle database access, file storage, authentication, and background work?
* How do I set up a basic CI/CD pipeline?

This architecture is representative of a large class of internal tools, SaaS products, dashboards, CRUD systems, admin portals, and API-backed web apps.



## Functional Components

### 1. Backend

The backend is a Flask application written in Python.

Responsibilities:

* serve server-side pages or API endpoints
* implement business logic
* connect to PostgreSQL
* manage authentication
* interact with blob storage
* expose HTTP endpoints for the frontend and other clients

### 2. Frontend

The frontend is intentionally simple:

* HTML
* CSS
* JavaScript

It can either:

* be served by Flask templates, or
* be built as static assets and served through the same app or reverse proxy

The goal is not frontend complexity, but deployment clarity.

### 3. SQL Database

Use PostgreSQL as the relational database.

Responsibilities:

* store users
* store business entities
* store application state
* store metadata for uploaded files
* store job state if needed

### 4. Blob/Object Storage

Use blob/object storage for large files and binary assets.

Examples:

* uploaded documents
* images
* exports
* media files
* optional model artifacts

Important principle:

* structured relational data goes into PostgreSQL
* large binary files go into object storage

### 5. API

The Flask backend also exposes an API.

Examples:

* authentication endpoints
* CRUD endpoints
* file upload/download endpoints
* status endpoints

This keeps the architecture simple: one backend, one app, multiple interfaces.



## Recommended Minimal Architecture

### Version 1: Minimal but realistic

This is the recommended first version.

Components:

* **Flask** application
* **Gunicorn** as the WSGI server
* **Caddy** as reverse proxy
* **PostgreSQL**
* **Object storage**
* **Flask-Login** for authentication
* **Dockerfile** for packaging
* **docker-compose.yaml** for local development
* **GitHub Actions** for CI/CD

Conceptual flow:

```text
Browser
  -> Caddy
  -> Gunicorn
  -> Flask app
  -> PostgreSQL
  -> Object storage
```

### Why these choices?

#### Caddy as reverse proxy

Caddy is a good learning choice because it is simpler than Nginx and handles HTTPS very smoothly.

Responsibilities:

* terminates HTTPS
* forwards requests to Gunicorn/Flask
* can serve static files
* can manage headers and routing

#### Gunicorn as app server

Gunicorn runs the Flask app in a production-ready way.

Responsibilities:

* runs Flask workers
* handles incoming requests from the reverse proxy

#### Flask-Login for auth

Flask-Login is a good fit for a classic web app with sessions, login/logout, and protected pages.



## Extended Architecture

### Version 2: Add realism gradually

Once the minimal version works, add:

* **Redis**
* **RQ** for background jobs
* optional caching through Redis
* basic monitoring and error tracking

Conceptual flow:

```text
Browser
  -> Caddy
  -> Gunicorn
  -> Flask app
      -> PostgreSQL
      -> Object storage
      -> Redis
  -> RQ worker
      -> Redis
      -> PostgreSQL
      -> Object storage
```

### Why Redis?

Redis is useful once the application needs:

* caching
* background jobs
* temporary shared state
* rate limiting
* session-related extensions

### Why RQ?

RQ is a simple Python background job system backed by Redis.

It is a good learning option because it is easier to understand than heavier alternatives.

Typical uses:

* processing uploaded files
* sending emails
* generating reports or PDFs
* slow external API calls
* long-running tasks that should not block web requests



## Environments: Local, Staging, Production

A key part of deployment learning is understanding that the same app usually runs in multiple environments.

### 1. Local development

Purpose:

* code locally
* run the full stack on your machine
* iterate quickly

Typical setup:

* Docker Compose
* Flask app
* PostgreSQL container
* optional Redis container
* local object storage emulator or mocked/external storage

Characteristics:

* fastest feedback loop
* debug-friendly
* not publicly exposed
* developer-oriented configuration

### 2. Staging

Purpose:

* environment for pre-production validation
* test deployment workflows
* verify migrations
* test integrations and secrets handling
* review features before production

Characteristics:

* should resemble production closely
* uses separate database and storage
* may use smaller resources than production
* can be deployed automatically from a develop or staging branch

Typical uses:

* manual QA
* integration testing
* smoke tests after deployment
* validating infrastructure changes

### 3. Production

Purpose:

* serve real users
* run the stable version of the system

Characteristics:

* real traffic
* real credentials and secrets
* separate database and storage from staging
* stronger monitoring and backup requirements
* stricter access control



## Why staging matters

Without staging, every deployment is effectively a production experiment.

Staging helps you validate:

* infrastructure configuration
* environment variables
* reverse proxy setup
* database migrations
* authentication flows
* file upload/download behavior
* CI/CD deployment logic

It also teaches an important operational principle:

* **same app, different environment configuration**



## Configuration Strategy

Each environment should have its own configuration values.

Examples:

* `APP_ENV=local|staging|production`
* database URL
* object storage bucket/container name
* secret keys
* OAuth credentials if added later
* Redis URL
* debug mode
* allowed hosts / domains

Important rules:

* never hardcode secrets in source code
* keep staging and production data isolated
* use environment variables or a secrets manager
* use different buckets/containers and databases per environment



## Suggested Deployment Targets

The project should focus on these targets:

* **AWS**
* **Azure**
* **Render**
* **Railway**
* **Hetzner VPS**

### How to think about them

#### Render / Railway

Best for learning deployment quickly with less operational burden.

Good for:

* container deployment
* managed PostgreSQL
* simpler developer experience
* CI/CD from Git

#### AWS / Azure

Best for learning mainstream cloud architecture.

Good for:

* managed app hosting
* managed Postgres
* managed blob storage
* infrastructure-as-code
* more production-like cloud patterns

#### Hetzner VPS

Best for learning infrastructure more directly.

Good for:

* running Docker Compose yourself
* configuring reverse proxy yourself
* managing Linux, certificates, and backups
* understanding what managed platforms abstract away



## Infrastructure as Code

### Dockerfile

The Dockerfile packages the Flask application into a deployable container image.

Responsibilities:

* define Python runtime
* install dependencies
* copy source code
* define startup command

### docker-compose.yaml

Docker Compose is mainly for **local development** and sometimes for VPS deployment.

Responsibilities:

* start the app and its dependencies together
* define service relationships
* provide local reproducibility

Typical services:

* app
* postgres
* caddy
* optional redis
* optional worker

### Terraform

Terraform is appropriate mainly when targeting AWS or Azure, and sometimes other platforms where infrastructure provisioning is useful.

Use it for:

* provisioning app infrastructure
* provisioning databases
* provisioning storage resources
* provisioning networking and DNS-related resources where relevant

For Render or Railway, Terraform is less central to the learning path, because those platforms abstract away much of the infrastructure.



## CI/CD

A simple CI/CD pipeline should include:

### Continuous Integration

On every push or pull request:

* install dependencies
* run linting
* run tests
* optionally build Docker image

Suggested checks:

* formatting
* linting
* unit tests
* import checks
* maybe type checks later

### Continuous Deployment

On merge to selected branches:

* deploy to **staging** from a staging/develop branch
* deploy to **production** from the main branch

Basic pipeline idea:

```text
Push / Pull Request
  -> lint
  -> test
  -> build image
  -> deploy to staging or production depending on branch
```



## Recommended Libraries and Tools

### Core app

* **Flask**
* **Gunicorn**
* **psycopg** or **psycopg2** for PostgreSQL access
* **SQLAlchemy** or Flask-SQLAlchemy if ORM support is desired

### Reverse proxy

* **Caddy**

### Authentication

* **Flask-Login**

### Optional later additions

* **Redis**
* **RQ**

### CI/CD

* **GitHub Actions**



## What this project teaches well

This project is good for learning:

* app packaging with Docker
* local orchestration with Docker Compose
* production serving with Gunicorn
* reverse proxy concepts
* environment separation
* managed vs self-managed deployment options
* PostgreSQL integration
* object storage integration
* authentication basics
* CI/CD basics
* gradual extension with caching and background jobs



## What is intentionally not the focus

This project is not primarily about:

* microservices
* Kubernetes
* high-scale distributed systems
* advanced frontend frameworks
* full ML platform design
* event-driven architecture

Those can be learned later.

The purpose here is to build a strong, realistic foundation.



## Recommended Learning Progression

### Phase 1

Build and run locally:

* Flask app
* PostgreSQL
* Caddy
* Docker Compose
* simple login
* file upload to blob storage or a mocked local equivalent

### Phase 2

Add CI/CD:

* linting
* tests
* Docker image build
* deploy to staging

### Phase 3

Add production deployment:

* production environment
* separate secrets
* separate database and storage
* monitoring basics

### Phase 4

Add optional realism:

* Redis
* RQ worker
* background jobs
* cache
* more robust observability



## Final Recommendation

For this project, the most sensible architecture is:

* **Flask** backend
* simple **HTML/CSS/JS** frontend
* **PostgreSQL** database
* **object/blob storage**
* **Gunicorn** as app server
* **Caddy** as reverse proxy
* **Flask-Login** for authentication
* **Dockerfile** for packaging
* **docker-compose.yaml** for local development
* **GitHub Actions** for CI/CD
* distinct **local**, **staging**, and **production** environments
* optional later addition of **Redis** and **RQ**

This gives you a deployment-oriented project that is simple enough to learn from, but realistic enough to reflect how many real applications are structured.

