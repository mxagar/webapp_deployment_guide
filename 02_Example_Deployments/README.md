# Example Deployments

This directory uses the dummy Django application
[`notes_webapp`](../notes_webapp/) to explore and compare web application
deployment workflows. Two deployment exercises have been carried out and
documented:

- [Railway](./Railway.md) explains a managed-platform deployment with separate
  development and production environments, PostgreSQL, GitHub integration, and
  Railway Infrastructure as Code.
- [Hostinger](./Hostinger.md) documents the live-validated VPS deployment of
  the complete Docker Compose stack with Nginx, Gunicorn/Django, and
  PostgreSQL.

Separate guides cover temporary GPU infrastructure and running Qwen with
Ollama:

- [Vast.ai](./VastAi.md) explains marketplace GPU selection, instance
  deployment, private SSH access, and cleanup.
- [RunPod](./RunPod.md) explains GPU Pod selection, deployment, private SSH
  access, and cleanup.
