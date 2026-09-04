# Railway Web Application Deployment Guide

This guide explains Railway by deploying the repository's
[`notes_webapp`](../notes_webapp/) Django application with isolated `dev` and
`prod` environments, a PostgreSQL database in each environment, GitHub-based
deployments, and source-controlled Railway Infrastructure as Code (IaC).

The guide was reviewed against the current Railway documentation and Railway
CLI 5.49.1 on 2026-09-04.

## Official references

- [Railway quick start](https://docs.railway.com/quick-start)
- [Projects](https://docs.railway.com/projects)
- [Services](https://docs.railway.com/services)
- [Environments](https://docs.railway.com/environments)
- [Variables and reference variables](https://docs.railway.com/variables)
- [Infrastructure as Code](https://docs.railway.com/infrastructure-as-code)
- [IaC TypeScript reference](https://docs.railway.com/infrastructure-as-code/reference)
- [`railway config` CLI reference](https://docs.railway.com/cli/config)
- [Deploying with the CLI](https://docs.railway.com/cli/deploying)
- [GitHub autodeploys](https://docs.railway.com/deployments/github-autodeploys)
- [Deploying Django](https://docs.railway.com/guides/django)
- [PostgreSQL](https://docs.railway.com/databases/postgresql)
- [Public networking](https://docs.railway.com/networking/public-networking)
- [Health checks](https://docs.railway.com/deployments/healthchecks)
- [Logs](https://docs.railway.com/observability/logs)
- [Metrics](https://docs.railway.com/observability/metrics)
- [Production readiness checklist](https://docs.railway.com/overview/production-readiness-checklist)

## Table of contents

- [1. Railway's resource model](#1-railways-resource-model)
- [2. Target architecture](#2-target-architecture)
- [3. Prerequisites and account setup](#3-prerequisites-and-account-setup)
- [4. Prepare the application](#4-prepare-the-application)
- [5. Define the project with Railway IaC](#5-define-the-project-with-railway-iac)
- [6. Create isolated dev and prod environments](#6-create-isolated-dev-and-prod-environments)
- [7. Configure secrets and connect GitHub](#7-configure-secrets-and-connect-github)
- [8. Deploy and expose the application](#8-deploy-and-expose-the-application)
- [9. Development and delivery workflow](#9-development-and-delivery-workflow)
- [10. Operate the deployment](#10-operate-the-deployment)
- [11. Security, persistence, and cost](#11-security-persistence-and-cost)
- [12. Troubleshooting](#12-troubleshooting)
- [13. Exemplary notes_webapp deployment](#13-exemplary-notes_webapp-deployment)

## 1. Railway's resource model

Railway organizes a deployment into several scopes:

| Resource | Purpose in this example |
| --- | --- |
| Workspace | Billing and access boundary: `Mikel's Projects` |
| Project | The complete application: `notes-app` |
| Environment | An isolated instance of the project: `dev` or `prod` |
| Service | A deployable container: `web` or managed `Postgres` |
| Deployment | One immutable attempt to build and run a service revision |

Configuration, variables, database instances, private networking, and
deployments are environment-scoped. The `dev` application therefore cannot
accidentally use the `prod` database reference: `${{Postgres.DATABASE_URL}}`
resolves to the PostgreSQL service in the currently selected environment.

Railway creates a `production` environment for a new project by default. This
example renames it to `prod` and duplicates it as `dev`, matching the short
environment names used in the rest of this repository.

## 2. Target architecture

Each environment contains the same topology but different running resources
and data:

```text
Browser
  -> HTTPS Railway domain
  -> Railway edge proxy
  -> web service
       -> Docker image built from github.com/mxagar/notes_webapp
       -> Gunicorn
       -> Django + WhiteNoise
       -> /health/ readiness check
       -> private DATABASE_URL
  -> Postgres service
       -> environment-specific persistent volume
```

The resulting isolation is:

```text
notes-app
├── dev
│   ├── web      -> dev public URL
│   └── Postgres -> dev database and data
└── prod
    ├── web      -> production public URL
    └── Postgres -> production database and data
```

Railway does not run the repository's `docker-compose.yaml` directly. It builds
the `web` service from the root `Dockerfile`, while Railway's managed Postgres
resource replaces the local Compose database service.

## 3. Prerequisites and account setup

Requirements:

- a Railway account with access to the `Mikel's Projects` workspace;
- Railway CLI 5.49.1 or newer;
- a GitHub account connected to Railway;
- the Railway GitHub App authorized for `mxagar/notes_webapp`;
- Git, Node.js, npm, Python 3.12, and uv for local work.

Check the CLI and authenticated identity:

```bash
railway --version
railway whoami --json
```

If authentication is missing, run `railway login`. Railway normally opens the
browser on the same computer; use browserless authentication only on a truly
headless machine.

In Railway, open **Account Settings -> Integrations -> GitHub** and confirm that
the GitHub App can access `mxagar/notes_webapp`. Connecting an account is not
enough when the GitHub App installation is limited to selected repositories.

## 4. Prepare the application

The example app already provides Railway's essential runtime contract:

- a root [`Dockerfile`](../notes_webapp/Dockerfile);
- Gunicorn bound to `0.0.0.0:$PORT`;
- PostgreSQL configured from `DATABASE_URL`;
- WhiteNoise for static assets;
- a database-aware `GET /health/` endpoint;
- proxy-aware HTTPS settings;
- database migrations and `collectstatic` commands.

Railway injects `PORT`; the application must listen on that value rather than a
fixed local port. Railway also injects `RAILWAY_PUBLIC_DOMAIN` after a public
domain exists. The Django settings add that generated hostname to
`ALLOWED_HOSTS` and its HTTPS origin to `CSRF_TRUSTED_ORIGINS`. Deployment
health checks use the hostname `healthcheck.railway.app`, which the app also
allows whenever `RAILWAY_ENVIRONMENT_NAME` is present. Because the internal
probe is HTTP and requires a 2xx response, only `/health/` is exempt from
Django's HTTPS redirect in Railway.

Run the local quality checks before deployment:

```bash
cd notes_webapp
uv sync --locked --group dev
uv run nox
```

The container entrypoint normally migrates the local Compose database. On
Railway, `RUN_MIGRATIONS_ON_STARTUP=false` disables that behavior because IaC
defines a pre-deploy migration command. This runs migrations once before the
new application instance starts and prevents every replica from racing to run
the same migration.

## 5. Define the project with Railway IaC

Railway's current project-level configuration format is
`.railway/railway.ts`. The older per-service `railway.json` and `railway.toml`
Config as Code formats are deprecated, so do not introduce them in a new
project.

The app keeps the Railway TypeScript dependency in `.railway/package.json`.
Install the exact locked version with:

```bash
npm --prefix .railway ci
```

The project definition in
[`notes_webapp/.railway/railway.ts`](../notes_webapp/.railway/railway.ts)
declares:

- a managed PostgreSQL service named `Postgres`;
- a `web` service sourced from `mxagar/notes_webapp` on `main`;
- a private `DATABASE_URL` reference;
- `/health/` as the deployment health check;
- a pre-deploy Django migration;
- HTTPS redirects in both environments;
- HSTS in `prod`, after HTTPS is known to work;
- preservation of `DJANGO_SECRET_KEY` without committing its value.

IaC commands act on the linked environment. Always inspect the link and plan:

```bash
railway status --json
railway config plan
```

Apply only after the plan contains the expected additions and changes:

```bash
railway config apply
```

GitHub pushes deploy application revisions, but they do not implicitly apply
new project-IaC changes. When `.railway/railway.ts` changes, plan and apply it
to each intended persistent environment.

## 6. Create isolated dev and prod environments

Create and link the project explicitly in the desired workspace:

```bash
railway init \
  --name notes-app \
  --workspace "Mikel's Projects" \
  --json
```

Rename the default `production` environment to `prod` in **Project Settings ->
Environments**, then link it:

```bash
railway environment link prod
railway status --json
```

For a brand-new project, use a two-phase bootstrap so Railway does not start a
public build before the Django secret exists. In a temporary, uncommitted copy
of `railway.ts`, omit the `web` service's `source` line and
`DJANGO_SECRET_KEY: preserve()` entry. Plan and apply that version to create the
empty `web` service and `Postgres` safely:

```bash
railway config plan
railway config apply
```

Do not push that intermediate file. Duplicate the resulting secret-free
topology to create an isolated `dev` environment:

```bash
railway environment new dev --duplicate prod --json
railway environment list --json
```

Environment duplication copies the service structure and configuration but
creates separate service instances, private networking, PostgreSQL storage,
variables, and deployments. Database contents are not shared.

## 7. Configure secrets and connect GitHub

Generate a different `DJANGO_SECRET_KEY` for each environment. Piping the value
through stdin avoids placing it in the command line:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(64), end="")' \
  | railway variable set DJANGO_SECRET_KEY --stdin \
      --service web --environment dev

python -c 'import secrets; print(secrets.token_urlsafe(64), end="")' \
  | railway variable set DJANGO_SECRET_KEY --stdin \
      --service web --environment prod
```

Never commit either value. Once the variables exist, `preserve()` in the IaC
definition tells Railway to retain them without revealing or replacing them.
Restore the final committed `railway.ts` after both secrets have been set.

The final IaC source declaration is equivalent to:

```ts
source: github("mxagar/notes_webapp", { branch: "main" })
```

Plan and apply it in both environments:

```bash
railway environment link dev
railway config plan
railway config apply

railway environment link prod
railway config plan
railway config apply
```

The source can also be inspected or connected explicitly with the CLI:

```bash
railway service source connect \
  --repo mxagar/notes_webapp \
  --branch main \
  --service web \
  --environment dev
```

Do not run both methods as competing sources of configuration. In this example,
IaC owns the source declaration; the service command is included for learning
and diagnosis.

## 8. Deploy and expose the application

Applying the GitHub source triggers Railway to build the repository's
Dockerfile. A push to the connected branch triggers later deployments
automatically.

Watch deployment state rather than treating a successful upload as a
successful release:

```bash
railway deployment list \
  --service web \
  --environment dev \
  --limit 5 \
  --json
```

The deployment is complete only when its status is `SUCCESS`. A detached
`railway up` means only that the source was uploaded or queued.

Generate one Railway-provided public domain per environment:

```bash
railway domain --service web --environment dev --json
railway domain --service web --environment prod --json
```

Verify both health endpoints and browser routes:

```bash
curl --fail --show-error https://<dev-domain>/health/
curl --fail --show-error https://<prod-domain>/health/
```

The expected health response is:

```json
{"status":"ok"}
```

Then open each URL, register separate test users, and create different notes.
Seeing different users and notes demonstrates that the environment databases
are isolated.

## 9. Development and delivery workflow

### Branch mapping used by this example

This learning deployment explicitly connects the same GitHub branch to both
Railway environments:

| GitHub branch | Railway environment | Purpose |
| --- | --- | --- |
| `main` | `dev` | Test the current application in the development infrastructure |
| `main` | `prod` | Run the same revision in the production infrastructure |

Configure both environment-scoped source connections explicitly:

```bash
railway service source connect \
  --project 62048fed-99b6-490c-b5c0-849a6cb08725 \
  --environment dev \
  --service web \
  --repo mxagar/notes_webapp \
  --branch main \
  --json

railway service source connect \
  --project 62048fed-99b6-490c-b5c0-849a6cb08725 \
  --environment prod \
  --service web \
  --repo mxagar/notes_webapp \
  --branch main \
  --json
```

Each result should report `repo: mxagar/notes_webapp`, `branch: main`, and
`disconnected: false`. If Railway shows **GitHub Repo not found**, first confirm
that its GitHub App is authorized for this repository, then reconnect the
source as shown above. The branch setting and repository authorization are
separate: selecting `main` cannot compensate for missing GitHub App access.

The checked-in IaC represents this learning setup with:

```typescript
source: github("mxagar/notes_webapp", { branch: "main" })
```

Because Railway evaluates the configuration for each target environment, this
sets `main` for both `dev` and `prod`.

### Conventional two-branch workflow

In a regular deployment, use `dev -> dev` and `main -> prod` so that a push to
the development branch cannot deploy directly to production:

| GitHub branch | Railway environment |
| --- | --- |
| `dev` | `dev` |
| `main` | `prod` |

That workflow is:

1. Create a long-lived `dev` branch.
2. Configure the `dev` service trigger for `dev`.
3. Keep the `prod` service trigger on `main`.
4. Push and validate changes in `dev`.
5. Merge the reviewed change into `main` to deploy production.

The corresponding environment-aware IaC source expression would be:

```typescript
source: github("mxagar/notes_webapp", {
  branch: ctx.environment === "dev" ? "dev" : "main",
})
```

Railway supports this branch mapping per environment in the service's source
settings. It can also wait for GitHub check suites, preventing an automatic
deployment until the repository's CI checks succeed.

For short-lived feature work, Railway PR environments can create an isolated
preview when a pull request opens and remove it when the pull request closes.
They complement rather than replace the persistent `dev` and `prod`
environments.

## 10. Operate the deployment

Always scope operational commands to the environment and service when more
than one instance exists.

### Inspect context and deployments

```bash
railway status --json
railway service list --environment prod --json
railway deployment list --service web --environment prod --limit 10 --json
```

### Read bounded logs

```bash
railway logs --service web --environment prod --lines 200 --json
railway logs --service web --environment prod --build --lines 200 --json
railway logs --service web --environment prod --http --status ">=400" \
  --lines 100 --json
```

Always give `railway logs` a line or time bound in scripts; otherwise it may
continue streaming.

### Inspect metrics

```bash
railway metrics --service web --environment prod --since 1h --json
railway metrics --service web --environment prod --since 6h \
  --cpu --memory --http --json
```

### Redeploy or restart

```bash
# Build the latest commit from the connected GitHub source.
railway redeploy --service web --environment prod --from-source --yes

# Restart the current image without rebuilding it.
railway restart --service web --environment prod --yes
```

After either command, check the specific deployment until it reaches a terminal
state. A restart is not a substitute for rebuilding changed code.

## 11. Security, persistence, and cost

- Keep `DJANGO_DEBUG=false` on every public environment.
- Store each environment's Django secret only in Railway variables.
- Use the private `${{Postgres.DATABASE_URL}}` reference; do not expose
  PostgreSQL through a public TCP proxy for this app.
- Railway terminates HTTPS. Django trusts the forwarded-protocol header and
  redirects plain HTTP requests.
- HSTS is enabled only for `prod` in this example. Test HTTPS thoroughly before
  enabling HSTS, include-subdomains, or preload settings on a custom domain.
- PostgreSQL data persists in Railway-managed storage, but persistence is not a
  backup strategy. Configure and test backups before storing important data.
- `dev` and `prod` each run a web service and database. Both consume resources;
  inspect usage and configure workspace cost controls.
- Do not place real personal or confidential notes in this learning deployment.

The app is intentionally deployed with one web replica. Before increasing the
replica count, confirm migrations run only as a pre-deploy command and review
database connection limits, session behavior, and expected traffic.

## 12. Troubleshooting

### GitHub repository is unavailable

Confirm that the Railway account is connected to GitHub and that the Railway
GitHub App installation has access to `mxagar/notes_webapp`. Reauthorizing the
account without granting repository access does not solve an installation
scope problem.

### IaC cannot import `railway/iac`

Install the pinned config dependency:

```bash
npm --prefix .railway ci
```

Run config commands from the repository root so Railway finds the nearest
`.railway/railway.ts`.

### IaC plan targets the wrong environment

```bash
railway environment link dev
railway status --json
railway config plan
```

Never apply until the status and plan name the intended project and
environment.

### Build fails

```bash
railway logs --service web --environment dev --build --lines 400 --json
```

Check that Railway found the root `Dockerfile`, the lockfile is committed, and
the GitHub source points at the expected branch and commit.

### Application crashes with a missing secret

When `DJANGO_DEBUG=false`, the app deliberately refuses to start without
`DJANGO_SECRET_KEY`. Check whether the key exists without copying its value into
documentation:

```bash
railway variable list --service web --environment dev --json
```

Set a newly generated value through stdin, then verify the resulting deployment.

### Database connection or migration fails

Confirm that `DATABASE_URL` is a reference to the environment's `Postgres`
service, then inspect pre-deploy and runtime logs. Do not replace it with the
public database URL.

### Deployment never becomes healthy

Railway expects `/health/` to return HTTP 200 before it activates the new
deployment. That endpoint checks the database, so a failing check can indicate
either an application startup problem or a database/configuration problem:

```bash
railway logs --service web --environment prod --lines 400 --json
railway logs --service web --environment prod --network --lines 100 --json
```

An HTTP 400 response specifically can mean Django rejected Railway's health
check hostname. Add `healthcheck.railway.app` to `ALLOWED_HOSTS` when running in
a Railway environment. An HTTP 301 response means Django redirected the
internal probe to HTTPS; exempt only the health path with
`SECURE_REDIRECT_EXEMPT = [r"^health/$"]` in the Railway environment.

### DisallowedHost or CSRF failure

Confirm that the service has a Railway domain and that
`RAILWAY_PUBLIC_DOMAIN` appears in the runtime environment. For a custom domain,
set `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` explicitly with the
custom hostname and HTTPS origin.

## 13. Exemplary notes_webapp deployment

This section records the concrete deployment performed while validating the
guide. It is intentionally separate from the reusable instructions above so
that transient deployment IDs and URLs do not become mistaken for universal
configuration.

### Deployment record

The deployment was completed on 2026-09-04 with these resources:

| Item | Value |
| --- | --- |
| Workspace | `Mikel's Projects` |
| Project | `notes-app` (`62048fed-99b6-490c-b5c0-849a6cb08725`) |
| Source | `mxagar/notes_webapp` |
| Branch mapping | `main -> dev`; `main -> prod` |
| Deployed commit | `3ccb7a62d50ae779776b2fb487d2b76f343739bf` |
| Builder | Root `Dockerfile` |
| Runtime region | `ams` |
| Database | Railway-managed PostgreSQL 18, one isolated instance per environment |
| Health check | `/health/`, 120-second deployment timeout |
| Pre-deploy command | `/app/.venv/bin/python src/manage.py migrate --noinput` |

Both web services and both PostgreSQL services reached `SUCCESS`. The final web
deployments were:

| Environment | Deployment ID | Public URL |
| --- | --- | --- |
| `dev` | `4f515270-f2d8-45c2-9162-548d2231667c` | <https://web-dev-c25d.up.railway.app> |
| `prod` | `f2b76756-2a8d-4150-8e63-2f2733ee2cda` | <https://web-prod-23f1.up.railway.app> |

Live checks returned `{"status": "ok"}` with HTTP 200 from both `/health/`
endpoints. Each root URL returned HTTP 302 to `/accounts/login/`, which is the
expected anonymous-user flow. A final `railway config plan` reported no drift
in either environment. The login page returned HTTP 200 in both environments;
the production response included `Strict-Transport-Security: max-age=31536000`,
while the development response intentionally omitted HSTS.

On 2026-09-04, the GitHub source was also reconnected explicitly for both
environment-scoped `web` service instances. Both Railway CLI responses reported
the repository as `mxagar/notes_webapp`, the branch as `main`, and
`disconnected: false`. This is the deliberate single-branch learning setup;
the conventional ongoing mapping is `dev -> dev` and `main -> prod`.

### Changes made to notes_webapp

The app repository was updated and pushed to support the deployment:

- `.railway/railway.ts` defines the project topology and environment-specific
  HSTS setting.
- `.railway/package.json` and its lockfile pin Railway's TypeScript IaC SDK.
- `src/entrypoint.sh` can skip startup migrations when Railway runs them as a
  pre-deploy command.
- Django accepts the generated Railway domain and Railway's health-check host.
- `/health/` is exempt from Django's internal HTTP-to-HTTPS redirect only when
  the app is running in a Railway environment.
- `README.md` documents the Railway-specific behavior and maintenance commands.

The relevant app commits are:

- `fed2e0e` — add Railway deployment configuration;
- `f829124` — allow Railway's health-check hostname;
- `3ccb7a6` — exempt the internal health probe from the HTTPS redirect.

### What the first deployment taught us

The first build and migrations succeeded, but the deployment health check
returned HTTP 400 because Django did not allow the probe hostname. Railway's
official health-check documentation specifies `healthcheck.railway.app`, so the
app now allows it in Railway environments.

The next attempt returned HTTP 301: Django's HTTPS redirect applied to the
internal HTTP readiness probe. Railway requires a 2xx health response and does
not follow that redirect for readiness. Exempting only `^health/$` resolved the
probe without weakening HTTPS enforcement for the rest of the application.

Finally, generating a public Railway domain after a deployment does not update
the already running container's environment. Redeploying the successful image
made `RAILWAY_PUBLIC_DOMAIN` available, after which both public domains passed
the live checks. The final releases were explicitly refreshed from the
GitHub-connected source with `railway redeploy --from-source`, then redeployed
once more after domain generation to refresh Railway-provided variables.
