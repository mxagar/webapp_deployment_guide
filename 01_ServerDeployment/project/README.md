# Deploy Your Flask App to Kubernetes Using EKS

This README is the project's requirements checklist, execution guide, and activity log. The detailed [course instructions](../README.md#project-deploy-your-flask-app-to-kubernetes-using-eks) remain the source for the assignment and rubric.

I forked the starter/original repo to [https://github.com/mxagar/webapp_deployment_guide](https://github.com/mxagar/webapp_deployment_guide).

## Implementation update — 2026-11-09

The fork's project submodule is now populated at recorded commit `52ce056932fdb1f899505eee8454216a20f48871`, with local implementation changes in three files. Its origin is `https://github.com/mxagar/udacity_server_deployment_exercises_cd0157.git`. No commits or pushes were made, and no AWS resources were created. The checkout is currently detached at the recorded commit; select `master` before committing as described below. The earlier lab checkout was not changed.

### Changes made in the forked submodule

1. **`buildspec.yml`: run the existing regression suite in `pre_build`**, immediately after dependency synchronization:

   ```yaml
   - uv sync --locked
   - uv run --locked python -m pytest test_main.py
   ```

2. **`buildspec.yml`: guard image publication/deployment and wait for rollout.** The first `post_build` command now rejects a failed earlier phase. The existing push, kubeconfig update, apply, and artifact commands remain in place; rollout verification follows apply:

   ```yaml
   post_build:
     commands:
       - test "$CODEBUILD_BUILD_SUCCEEDING" = "1"
       - docker push $REPOSITORY_URI:$TAG
       # Existing diagnostics and kubeconfig update remain here.
       - kubectl apply -f simple_jwt_api.yml
       - kubectl rollout status deployment/simple-jwt-api --namespace default --timeout=180s
       # Existing build.json artifact command remains here.
   ```

3. **`simple_jwt_api.yml`: supply the signing secret and check readiness.** Under the application container:

   ```yaml
   env:
     - name: JWT_SECRET
       valueFrom:
         secretKeyRef:
           name: jwt-secret
           key: JWT_SECRET
   readinessProbe:
     httpGet:
       path: /
       port: 8080
     initialDelaySeconds: 3
     periodSeconds: 5
   ```

   Kubernetes must find `jwt-secret` in the application namespace before Pods can start. The readiness probe checks HTTP health before Pods receive Service traffic and allows rollout verification to reflect HTTP readiness.

4. **`ci-cd-codepipeline.cfn.yml`: set the fork defaults.** `GitSourceRepo` now defaults to `udacity_server_deployment_exercises_cd0157`; `GitHubUser` defaults to `mxagar`. Existing defaults already match `simple-jwt-api`, `master`, `UdacityFlaskDeployCBKubectlRole`, and `aws/codebuild/standard:8.0`.

The Flask app, Dockerfile, dependency lockfile, and 11 existing regression cases already supported the required local workflow and did not need changes. Account-specific placeholders in `trust.json` and `aws-auth-patch.yml` remain deliberate: use your verified account and live cluster mappings, never invent or blindly replace them.

### Verification completed locally

| Check | Result |
| --- | --- |
| `uv run --locked pytest` before and after configuration edits | 11 passed, Python 3.13.5 |
| Buildspec YAML parsing and command-type checks | Passed; each command parsed as a string |
| Kubernetes multi-document YAML parsing | Passed; Service and Deployment |
| CloudFormation YAML parsing with intrinsic tags supported | Passed; fork defaults verified. This is syntax checking, not AWS service validation. |
| `docker build -t eks-flask-project:local .` | Passed; image `sha256:88bc6bfb71c872efecf66a36478c5b22cbbb8d0596ff37628ec3d65de54f4506` |
| Running Gunicorn container over HTTP | Health, auth, contents passed; missing and invalid tokens returned 401 |
| `git diff --check` inside the submodule | Passed |

The image uses Python 3.13.18 and uv 0.13.7; local Python is the same minor version. Installed local uv is 0.11.16 and completed the checks, but the course recommends upgrading local uv to at least 0.13.7. The current Windows `aws` command resolves to a Python virtual-environment installation; verify/install **AWS CLI v2** before SSO or EKS work.

AWS template validation, IAM authorization, EKS rollout, external load-balancer checks, and the real failing-pipeline gate demonstration remain pending. Local YAML parsing and API tests do not establish those cloud results.

### Your next steps, in order

Use Bash in Git Bash/WSL for the following commands; the detailed numbered execution guide below explains the AWS actions and expected results. After each step, report its result so it can be recorded in the activity log before proceeding.

1. **Review and publish the fork changes.** From the guide root:

   ```bash
   cd 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157
   git status --short
   git diff
   git switch master
   git add buildspec.yml simple_jwt_api.yml ci-cd-codepipeline.cfn.yml
   git commit -m "Configure tested Flask deployment to EKS"
   git push origin master
   ```

   Confirm the push succeeds and record its commit ID. If branch selection or push is rejected, stop and inspect the message rather than force-pushing. A running pipeline on this fork/branch would be triggered by this push; none was created in this session.

2. **Verify tools and sign in** using execution-guide step 2. Ensure `aws --version` begins with `aws-cli/2`; verify `eksctl`, `kubectl`, and `jq`. Confirm `deployment-course`, your account ID, `eu-central-1`, and available EKS versions.
3. **Create or reuse the EKS cluster** using step 3. Creating the cluster begins AWS charges. Confirm two Ready nodes and a ConfigMap-compatible authentication mode.
4. **Configure the deployment IAM role** using step 4. Fill in the actual account ID in `trust.json` and create/reuse the named role with its permissions. Record the actual policy edits and commands.
5. **Authorize the role in the live cluster** using step 5. Preserve all existing `aws-auth` mappings and verify nodes remain Ready.
6. **Create Parameter Store and Kubernetes secrets** using step 6, before pipeline creation. The manifest reference is already implemented; create the actual `JWT_SECRET` parameter and `default/jwt-secret` privately.
7. **Publish any account-specific file changes deliberately.** Inspect `git diff`, stage only intended non-secret policy changes, commit, and push to `master`. Do not commit live ConfigMap exports, secret files, or credentials. Record the exact commands and commit ID.
8. **Validate the template with AWS CLI v2**, from the submodule directory with the profile and region exported:

   ```bash
   aws cloudformation validate-template --template-body file://ci-cd-codepipeline.cfn.yml
   ```

   Then create the stack in the console following step 7, entering the GitHub token privately. Verify the stack reaches `CREATE_COMPLETE` and the pipeline succeeds. Capture execution IDs and source commit.
9. **Verify the live deployment** using step 8. Save the external URL and sanitized endpoint results for the reviewer.
10. **Demonstrate the test gate** using step 9: push a temporary failing test, verify no image/deployment update, then remove it and push a passing correction. Record both execution IDs and running image evidence.
11. **Save the final submodule pointer and project documentation.** After the fork's final corrected commit is pushed, return to the guide root, review changes, and commit the README plus updated submodule pointer:

    ```bash
    cd ../../..
    git diff --submodule
    git add 01_ServerDeployment/project/README.md 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157
    git commit -m "Document EKS project implementation and deployment evidence"
    ```

    Push the guide's current branch through your normal workflow. Its recorded pointer must refer to a commit already available in the fork. Keep logging later review and cleanup actions too.
12. **Keep the URL available for review, then clean up** using step 10. Record and verify deletion of chargeable resources and retained data.

### Local signing secret in `.env`

A fresh 32-byte cryptographically random `JWT_SECRET` is saved in `udacity_server_deployment_exercises_cd0157/.env`. The file is ignored by Git and excluded from Docker's build context through the existing `.env*` patterns. Its value is intentionally absent from this README. This is a newly generated local secret, not recovery of the temporary secret used during the earlier container smoke test.

From the submodule directory, pass it to Docker at runtime:

```bash
docker run --rm --name flask-project --publish 127.0.0.1:8080:8080 --env-file .env eks-flask-project:local
```

For direct local Python execution in Bash, export it first; the application does not automatically read `.env`:

```bash
set -a
source .env
set +a
uv run --locked python main.py
```

For AWS deployment, step 6 still creates the managed secret separately. To deliberately reuse this local value instead, load `.env` as above and skip step 6's random-generation command before calling `aws ssm put-parameter`. Do not overwrite an existing AWS parameter without first checking that it belongs to this project. Never commit `.env` or print its contents in shared logs.

## Documentation rule

Every project action performed by the user or assistant must be recorded here: local edits, tests, Git operations, AWS console changes, AWS CLI commands, `eksctl` commands, Kubernetes commands, failures, retries, verification, and cleanup.

- The commands below are **planned instructions**, not evidence that they ran.
- After each action, append a dated activity-log entry with actor, command or console action, result, verification, and remaining work. Record failures too.
- Record actual non-secret resource names and configuration as they become known. Keep credentials, JWTs, signing secrets, and decrypted parameter values out of this file, screenshots, logs, and Git. Use placeholders in recorded commands containing secrets.
- The assistant records its own actions and user-reported actions. User actions cannot be marked complete until the user reports their result or the assistant verifies them.
- Before starting each new step, update this README with the preceding step's result.

## Requirements and acceptance checklist

| Area | Required result | Status |
| --- | --- | --- |
| API | `GET /` returns the JSON string `"Healthy"`. `POST /auth` accepts nonempty email/password and returns a JWT. `GET /contents` returns verified `email`, `exp`, and `nbf`; missing/invalid tokens return 401. | Pending verification |
| Runtime | Python 3.13 locally, in Docker, and in CodeBuild; dependencies declared in `pyproject.toml`, fixed in `uv.lock`, and installed with uv. | Local and Docker verified; CodeBuild pending |
| Docker | Successful local build using `python:3.13-slim`; locked runtime dependencies; entry point `["gunicorn", "-b", ":8080", "main:APP"]`; all endpoints tested. | Local build and HTTP checks passed |
| Local secret | Supply `JWT_SECRET` at runtime through an ignored environment file; do not embed it in the image. | `.env` created and exclusion verified; runtime commands documented |
| Cluster | EKS `simple-jwt-api` in `eu-central-1`, two `t3.medium` worker nodes; both Ready. Guide target: Kubernetes 1.37, kubectl 1.37.2. | Pending |
| Access | Deployment IAM role, trust relationship, AWS permissions, and Kubernetes authorization configured. Preserve existing node mappings. | Pending |
| Infrastructure | Supplied CloudFormation template provisions CodePipeline, CodeBuild, ECR, S3 artifacts, service roles, and trust-policy helper Lambda. | Pending |
| Source | Correct repository owner/name/branch and automatic GitHub change detection; GitHub token supplied privately as a template parameter. | Pending |
| Secret delivery | Parameter Store `SecureString` retrieved by CodeBuild; Kubernetes Secret supplies the same value to Pods. | Pending |
| Build gate | pytest runs before image build; failed builds cannot publish or deploy. | Pending |
| Deployment | Image pushed to ECR; manifest applied; rollout completes; external Service URL serves all three endpoints. | Pending |
| Evidence | Reviewer URL, successful pipeline execution, failed-test gate demonstration, and corrected successful execution recorded. Final tests pass. | Pending |
| Cleanup | After review, delete pipeline, load balancer, cluster/nodes, and unwanted retained storage/logs; verify removal. | Deferred until after review |

The original rubric mentions `python:stretch`; this guide explicitly updates it to Python 3.13 slim and uv. Additional endpoints and custom failure alerts are optional. The starter issues tokens from supplied fields; user-database authentication is outside this assignment.

## Understanding JWT: a temporary access pass

**JWT (JSON Web Token)** is a compact, signed token carrying information called **claims** between a client and a server. A useful mental model is a **temporary access pass issued by the backend**: after obtaining it, the client presents it with each request to a protected endpoint. Public endpoints do not need it.

In a complete login system, the backend checks the user's credentials before issuing this pass. This project's starter only checks that email and password are supplied; it does **not** verify them against a user database, so it is not a complete login system.

The project's request flow is:

1. The client sends an email and password to `POST /auth`.
2. The backend returns a JWT containing the email and validity timestamps.
3. The client sends the token to the protected `GET /contents` endpoint in the HTTP header:

   ```http
   Authorization: Bearer <token>
   ```

4. The backend verifies the signature and timestamps before returning the claims. Missing, expired, or invalid tokens are rejected with status 401.

The claims used here are `email` (the supplied email), `exp` (expiration time), and `nbf` ("not before": when the token becomes valid). The app uses `JWT_SECRET` with HS256 to sign and verify tokens. Modifying a token's contents makes its signature invalid. The signing secret stays on the backend; the client receives only the token.

JWTs commonly support authentication and API authorization. Like a temporary password, a bearer token can be used by whoever holds it until it expires, so keep it private and transmit it over HTTPS. Unlike a password, this token carries signed claims and an expiration time. **Signed does not mean encrypted**: anyone holding this JWT can read its contents, so never include passwords or other secrets in its payload.

### Where the JWT is stored

The **client stores the JWT** after receiving it from `/auth`. In this project's command-line examples, the token is held temporarily in the shell variable `TOKEN`:

```bash
TOKEN=$(curl ... | jq -er '.token')  # Illustrative: use the full request in the execution guide.
```

Subsequent protected requests send its value in the `Authorization: Bearer <token>` header. Run `unset TOKEN` when finished to remove the shell variable. In a browser application, storage depends on the application's design, such as application memory or a cookie.

This Flask backend does **not** store each issued JWT. It verifies the token supplied with each request using `JWT_SECRET`. These are different values:

| Value | Stored where in this project | Purpose |
| --- | --- | --- |
| JWT access token | Client's temporary `TOKEN` shell variable | Presented by the client to access a protected endpoint |
| `JWT_SECRET` signing secret | Backend configuration: AWS Parameter Store, then a Kubernetes Secret supplied to the Pods; also retrieved into CodeBuild's environment | Signs and verifies tokens; never sent to the client |

## Repository and configuration

The implementation belongs in the separate Git submodule:

```text
01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157/
```

Initial inspection found its directory unpopulated. It has now been initialized at the parent's recorded commit `52ce056932fdb1f899505eee8454216a20f48871`. The implementation update above describes the local changes applied to this project checkout; the earlier lab checkout remains untouched.

| Setting | Planned value; verify before use |
| --- | --- |
| AWS profile | `deployment-course` |
| AWS region | `eu-central-1` |
| Cluster | `simple-jwt-api` |
| Stack | `simple-jwt-api-pipeline` |
| Deployment role | `UdacityFlaskDeployCBKubectlRole` |
| GitHub owner | `mxagar`, or the actual fork owner |
| Repository | `udacity_server_deployment_exercises_cd0157` |
| Branch | `master`, subject to remote verification |
| CodeBuild image | `aws/codebuild/standard:8.0` |
| Parameter | `JWT_SECRET` (`SecureString`) |
| Kubernetes Secret | `default/jwt-secret`, key `JWT_SECRET` |
| Application | Deployment and Service `default/simple-jwt-api`; three application replicas in the reference manifest |

## Execution guide

Commands in this guide use **Bash** (Git Bash or WSL on Windows), unless stated otherwise. Gunicorn runs in Linux/WSL or Docker, rather than native Windows. Do not paste Bash syntax into PowerShell.

### 1. Populate and inspect the project locally

From the guide repository root:

```bash
git submodule update --init --recursive -- 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157
cd 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157
git status --short
git remote -v
git branch --show-current
git rev-parse HEAD
```

Inspect `main.py`, `test_main.py`, `Dockerfile`, `pyproject.toml`, `uv.lock`, `buildspec.yml`, `simple_jwt_api.yml`, `ci-cd-codepipeline.cfn.yml`, `trust.json`, `iam-role-policy.json`, and `aws-auth-patch.yml`. Record actual gaps before editing. Submodule initialization may leave a detached HEAD: select a working branch deliberately before committing. Changes inside this submodule must be committed/pushed to its own repository; the parent repository separately records its updated commit pointer.

Local API tests and Docker endpoint checks have passed, and the required buildspec gate and Pod secret reference are implemented locally. See the implementation update and activity log above/below. Publish these changes before pipeline creation; do not repeat the edits blindly.

### 2. Verify tools and AWS identity

```bash
export AWS_PROFILE=deployment-course
export AWS_DEFAULT_REGION=eu-central-1
export CLUSTER_NAME=simple-jwt-api
export STACK_NAME=simple-jwt-api-pipeline
aws --version
eksctl version
kubectl version --client
```

If the SSO profile is absent, run the wizard once:

```bash
aws configure sso --profile deployment-course
aws configure set region eu-central-1 --profile deployment-course
```

Then authenticate and verify the intended account:

```bash
aws sso login --profile "$AWS_PROFILE"
aws sts get-caller-identity
aws eks describe-cluster-versions --region "$AWS_DEFAULT_REGION" --output table
```

Record the selected account/profile/region and supported version. The identity needs permissions to create EKS, networking, EC2 nodes, IAM roles/policies, CloudFormation, CodePipeline, CodeBuild, ECR, S3, Lambda, and SSM resources. An SSO login does not itself grant these permissions. Resolve denied permissions before proceeding.

### 3. Create and verify EKS

This starts chargeable AWS resources. First check whether an existing course cluster can be reused:

```bash
aws eks list-clusters
```

For a new dedicated cluster, after verifying regional version availability:

```bash
export KUBERNETES_VERSION=1.37
eksctl create cluster --name "$CLUSTER_NAME" --nodes 2 --version "$KUBERNETES_VERSION" --instance-types t3.medium --region "$AWS_DEFAULT_REGION" --profile "$AWS_PROFILE"
aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$AWS_DEFAULT_REGION" --profile "$AWS_PROFILE"
kubectl config current-context
kubectl get nodes
aws eks describe-cluster --name "$CLUSTER_NAME" --query 'cluster.{version:version,authenticationMode:accessConfig.authenticationMode}' --output table
```

Record completion, authentication mode, and two Ready nodes. Use an identity already authorized for Kubernetes administration. The assignment's `aws-auth` method needs `CONFIG_MAP` or `API_AND_CONFIG_MAP`; confirm that before configuring access. An API-only cluster uses access entries instead. Keep local and CodeBuild kubectl within one minor version of the control plane.

### 4. Create or verify the deployment role

```bash
aws sts get-caller-identity --query Account --output text
aws iam get-role --role-name UdacityFlaskDeployCBKubectlRole
```

Replace `<ACCOUNT_ID>` in `trust.json` with the actual account ID. Inspect the existing role if found; create it only if absent:

```bash
aws iam create-role --role-name UdacityFlaskDeployCBKubectlRole --assume-role-policy-document file://trust.json
aws iam put-role-policy --role-name UdacityFlaskDeployCBKubectlRole --policy-name eks-describe --policy-document file://iam-role-policy.json
```

The supplied permissions cover EKS description and Parameter Store access; inspect the actual files before applying. CodeBuild's own service role separately needs permission to retrieve the buildspec parameter. The template's helper adds the generated service role to the deployment role's trust policy. Record the role ARN and policy changes.

### 5. Authorize the role in Kubernetes

Fetch the live mapping with the cluster administrator identity:

```bash
AUTH_PATCH=/tmp/aws-auth-patch.yml
kubectl get configmap/aws-auth --namespace kube-system -o yaml > "$AUTH_PATCH"
```

If and only if it is absent on an `API_AND_CONFIG_MAP` cluster with Ready managed nodes, create the ConfigMap and fetch it again:

```bash
kubectl create configmap aws-auth --namespace kube-system --from-literal=mapRoles='[]'
kubectl get configmap/aws-auth --namespace kube-system -o yaml > "$AUTH_PATCH"
```

Edit the fetched file, preserving all existing role mappings. Append this entry inside `data.mapRoles`, replacing the account placeholder:

```yaml
- groups:
    - system:masters
  rolearn: arn:aws:iam::<ACCOUNT_ID>:role/UdacityFlaskDeployCBKubectlRole
  username: build
```

This is the course's administrative access pattern. Do not replace the live ConfigMap with the illustrative repository sample.

```bash
kubectl patch configmap/aws-auth --namespace kube-system --type merge --patch-file "$AUTH_PATCH"
kubectl get nodes
```

If a conflict occurs, fetch fresh state and repeat the edit. Record the mapping and verification, without duplicating entries.

### 6. Create and deliver the signing secret

Create the secret before starting the pipeline so initial builds can retrieve it. Run from the project submodule with its uv environment ready:

```bash
JWT_SECRET=$(uv run --locked python -c 'import secrets; print(secrets.token_hex(32))')
aws ssm put-parameter --name JWT_SECRET --value "$JWT_SECRET" --type SecureString
aws ssm get-parameter --name JWT_SECRET --query 'Parameter.{Name:Name,Type:Type,Version:Version}' --output table
kubectl create secret generic jwt-secret --namespace default --from-literal=JWT_SECRET="$JWT_SECRET" --dry-run=client -o yaml | kubectl apply -f -
unset JWT_SECRET
```

If the parameter already exists, inspect its ownership and reuse it or rotate it deliberately; do not overwrite an unrelated secret. To copy an existing project parameter, retrieve it into the variable with `aws ssm get-parameter --name JWT_SECRET --with-decryption --query 'Parameter.Value' --output text`, without printing it, then run the Secret creation pipeline above.

Inside the manifest's application container, configure:

```yaml
env:
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: jwt-secret
        key: JWT_SECRET
```

Keep the buildspec's `env.parameter-store` mapping `JWT_SECRET: JWT_SECRET`. Parameter retrieval into CodeBuild does not automatically populate Pod environments. Rotation requires copying the new value to Kubernetes and restarting Pods. Record metadata and successful creation only, never values.

### 7. Prepare GitHub and create the pipeline stack

1. Complete and commit the local implementation in the fork. Verify the remote and monitored branch before pushing. Record exact Git commands and commit IDs.
2. Update template defaults: cluster `simple-jwt-api`, actual GitHub owner, repository `udacity_server_deployment_exercises_cd0157`, branch `master`, role `UdacityFlaskDeployCBKubectlRole`, and image `aws/codebuild/standard:8.0`.
3. Create a GitHub classic personal access token for the retained OAuth source action. The course specifies `repo`; webhook use also requires the documented hook permissions. Keep the token private and choose an expiration.
4. In AWS Console, select `eu-central-1` → CloudFormation → Create stack → With new resources → Upload the project's `ci-cd-codepipeline.cfn.yml`.
5. Set stack name `simple-jwt-api-pipeline`. Check all parameters, enter the token only in `GitHubToken` (`NoEcho`), acknowledge the required IAM capabilities, and create the stack.
6. Monitor Events until `CREATE_COMPLETE`. Record stack identity, parameter values excluding the token, resource names, and any errors.
7. Open CodePipeline in the same region and inspect the initial execution. For a retry use **Release change**, rather than starting CodeBuild alone: this project requires pipeline source artifacts.

Verify CodeBuild logs show Python 3.13, the intended kubectl/uv versions, dependency synchronization, passing pytest, Docker build/push, and Kubernetes deployment. Record pipeline/build execution IDs and source commit.

### 8. Verify rollout and external API

```bash
kubectl rollout status deployment/simple-jwt-api --namespace default --timeout=180s
kubectl get pods --namespace default -l app=simple-jwt-api
kubectl get service simple-jwt-api --namespace default -o wide
```

Wait for the external hostname and DNS. Substitute its actual value:

```bash
BASE_URL=http://<LOAD_BALANCER_HOSTNAME>
curl --fail-with-body --silent --show-error "$BASE_URL/"
TOKEN=$(curl --fail-with-body --silent --show-error --request POST "$BASE_URL/auth" --header 'Content-Type: application/json' --data '{"email":"test@example.com","password":"exercise-only"}' | jq -er '.token')
curl --fail-with-body --silent --show-error "$BASE_URL/contents" --header "Authorization: Bearer $TOKEN"
unset TOKEN
```

Record the URL, statuses, and sanitized responses. Also verify missing/invalid tokens return 401. A successful manifest apply alone is insufficient evidence of rollout or endpoint health.

### 9. Demonstrate the test gate and automatic delivery

1. Temporarily add `assert False, "Intentional check: this commit must not deploy"` inside a test.
2. Run `uv run --locked python -m pytest test_main.py`; record the expected failure.
3. Commit and push the intentional failure to the monitored branch. Record the commands and commit ID.
4. Confirm the triggered pipeline fails at tests, does not publish that execution's image or deploy it, and leaves the prior deployment serving requests. Record build logs and the running image before/after.
5. Remove the intentional failure, rerun pytest, commit and push the correction, and verify the next pipeline and rollout succeed. Record the corrected commit and execution IDs.
6. Finish with passing tests and reviewer notes containing the external URL and evidence references. Keep the deployment running until feedback is complete.

### 10. Clean up after review

Before deletion, record physical resource names, including retained ECR repository, S3 artifact bucket, and helper Lambda/log groups. Stop further source pushes and wait for builds to finish.

```bash
aws cloudformation delete-stack --stack-name "$STACK_NAME"
aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"
kubectl delete service simple-jwt-api --namespace default --wait=true
kubectl delete deployment simple-jwt-api --namespace default --wait=true
```

Verify the load balancer is removed before deleting the dedicated cluster:

```bash
eksctl delete cluster --name "$CLUSTER_NAME" --region "$AWS_DEFAULT_REGION" --profile "$AWS_PROFILE" --wait
```

Inspect remaining CloudFormation stacks, EC2 instances, EBS volumes, NAT gateways, and public IP allocations. Delete unwanted retained ECR images/repository, all S3 artifact versions/delete markers and bucket, and exercise CloudWatch log groups. Record each console action or actual CLI command and its result. Stack deletion alone does not prove cleanup is complete.

When unused, remove the manual IAM role/inline policy, Parameter Store parameter, exercise GitHub token, and local secret files. If keeping the cluster, remove only the obsolete role mapping and project Secret. Never delete shared resources merely because their names resemble the course examples.

## Activity log

| Date | Actor | Action / command | Result and evidence | Next step |
| --- | --- | --- | --- | --- |
| 2026-11-09 | Assistant | Read the project section in `../README.md`, rubric, `.gitmodules`, project directory, and earlier lab reference files; inspected registered project paths with `git ls-files --stage 01_ServerDeployment/project`. | Requirements analyzed; project submodule directory unpopulated; project README empty. No AWS resources inspected or changed. | Populate this guide, then initialize project checkout. |
| 2026-11-09 | Assistant | Checked AWS EKS version documentation and authentication documentation using web/Context7. | EKS 1.37 listed in standard support; ConfigMap authorization requires a compatible authentication mode. Regional availability still needs CLI verification. | Verify regional support before provisioning. |
| 2026-11-09 | Assistant | Read project README; searched for `AGENTS.md`; inspected reference CloudFormation parameters; populated this README with requirements, planned commands, verification, and logging rules. | Documentation only. No application code, Git commits/pushes, or AWS resources changed. | User/assistant executes step 1 and records results here. |

Verification of this documentation update: assistant ran `git diff --check`, `Get-Item 01_ServerDeployment/project/README.md | Select-Object Length`, and `git diff --stat`. The checks succeeded; Git reported only its configured LF-to-CRLF conversion warning. The diff contained the project README update only. This verification result was then appended here.

JWT explanation update (2026-11-09, assistant): read the opening section with `Get-Content 01_ServerDeployment/project/README.md | Select-Object -First 48`, then added the temporary-access-pass mental model, endpoint flow, claims, signing-secret distinction, and security considerations using `apply_patch`. Documentation only; no application or AWS changes. Verification command: `git diff --check`.

JWT storage explanation update (2026-11-09, assistant): used `apply_patch` to document client-side token storage, the temporary `TOKEN` shell variable and `unset TOKEN`, browser storage examples, and the distinction between issued JWTs and backend `JWT_SECRET` storage. Documentation only; no application or AWS changes. Verification: `git diff --check`.

Submodule audit (2026-11-09, assistant): ran `git submodule status --recursive`. The sandbox blocked Git's shell helper with Windows error 5; reran the same read-only command with elevated execution successfully. Also inspected `.gitmodules`, `git status --short`, and `git ls-files --stage`, and ran `git -C <path> status --short` for each initialized submodule. The project submodule is uninitialized (`-52ce056932fdb1f899505eee8454216a20f48871`). Both lab submodules and `notes_webapp` match the commits pinned by the parent. No remote fetch was performed, so this does not establish whether newer upstream commits exist. No submodule was updated during this audit.

### Implementation session command log — 2026-11-09, assistant

The implementation plan was to retain the existing API/runtime, complete the three deployment configuration files, run local verification, and provide the user's cloud checklist. Changes were applied with `apply_patch` in the fork's checkout and this README. No IAM account ID, secret value, or AWS resource was supplied or changed.

1. Initialized the project checkout successfully (approved execution outside the sandbox):

   ```bash
   git submodule update --init --recursive -- 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157
   ```

2. Inspected the checkout and existing files with PowerShell `Get-ChildItem -Force`, `Get-Content`, and Git. Read `buildspec.yml`, `simple_jwt_api.yml`, `test_main.py`, `pyproject.toml`, `Dockerfile`, `trust.json`, `ci-cd-codepipeline.cfn.yml`, and `.gitignore`. Also read the test-driven-development, verification-before-completion, and writing-plans skill instructions. Commands included:

   ```powershell
   Get-ChildItem -Force 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157
   git -C 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157 status --short
   git -C 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157 remote -v
   git -C 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157 branch --show-current
   Get-Command uv,docker,aws -ErrorAction SilentlyContinue | Select-Object Name,Source
   uv --version
   docker version
   ```

   Result: clean detached checkout of the intended fork; local uv 0.11.16; AWS command from a Python virtual environment. Docker initially failed with sandbox pipe permissions; approved retry returned a running Linux Docker Desktop engine.

3. Ran `uv run --locked pytest` in the submodule. Initial sandbox attempt failed accessing the shared uv cache; approved retry created the project `.venv`, installed locked dependencies, and passed all 11 tests. uv ignored an unrelated inherited `VIRTUAL_ENV` and fell back from hardlinks to copying. After configuration edits, repeated the full command: **11 passed** again.
4. Applied the three-file configuration changes summarized above. Ran:

   ```bash
   git -C 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157 diff --check
   git -C 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157 diff --stat
   ```

   Result: whitespace check passed; three files changed, 18 insertions and two deletions.
5. A preliminary `python -c "import yaml; print(yaml.__version__)"` failed because the default Python lacked PyYAML. Used an ephemeral dependency through uv instead; project dependency files were not edited:

   ```bash
   uv run --locked --with pyyaml python -c "from pathlib import Path; import yaml; b=yaml.safe_load(Path('buildspec.yml').read_text()); assert all(isinstance(c,str) for p in b['phases'].values() for c in p['commands']); docs=list(yaml.safe_load_all(Path('simple_jwt_api.yml').read_text())); print('buildspec command types and Kubernetes YAML valid'); print('Kubernetes resources:', [d['kind'] for d in docs])"
   uv run --locked --with pyyaml python -c "from pathlib import Path; import yaml; L=type('CfnLoader',(yaml.SafeLoader,),{}); L.add_multi_constructor('!',lambda loader,tag,node: loader.construct_scalar(node) if isinstance(node,yaml.ScalarNode) else loader.construct_sequence(node)); t=yaml.load(Path('ci-cd-codepipeline.cfn.yml').read_text(),Loader=L); assert t['Parameters']['GitHubUser']['Default']=='mxagar'; print('CloudFormation YAML parsed; fork defaults verified')"
   ```

   Both passed. Also consulted AWS CodeBuild documentation through Context7; no AWS account operations were performed.
6. Built the image from the submodule with approved Docker access:

   ```bash
   docker build -t eks-flask-project:local .
   ```

   Result: successful image build and locked runtime installation. Started a temporary container with a random in-memory secret, using PowerShell:

   ```powershell
   $env:JWT_SECRET = [Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
   docker run --detach --rm --name eks-flask-project-check --publish 127.0.0.1:18080:8080 --env JWT_SECRET eks-flask-project:local
   Remove-Item Env:JWT_SECRET
   ```

7. Exercised the container through HTTP using PowerShell. No tokens or signing secrets were printed:

   ```powershell
   $baseUrl = 'http://127.0.0.1:18080'
   $health = Invoke-RestMethod "$baseUrl/"
   if ($health -ne 'Healthy') { throw 'Health mismatch' }
   $auth = Invoke-RestMethod "$baseUrl/auth" -Method Post -ContentType 'application/json' -Body '{"email":"test@example.com","password":"exercise-only"}'
   $claims = Invoke-RestMethod "$baseUrl/contents" -Headers @{ Authorization = "Bearer $($auth.token)" }
   if ($claims.email -ne 'test@example.com' -or !$claims.exp -or !$claims.nbf) { throw 'Claims mismatch' }
   foreach ($requestHeaders in @(@{}, @{Authorization='Bearer invalid'})) {
       $response = Invoke-WebRequest "$baseUrl/contents" -Headers $requestHeaders -SkipHttpErrorCheck
       if ($response.StatusCode -ne 401) { throw 'Expected 401' }
   }
   ```

   Result: all five checks passed. Stopped the temporary container with `docker stop eks-flask-project-check`; `--rm` removed it. The local image remains available for reuse.
8. Updated this README with the change summary, actual verification evidence, and the ordered user checklist. Final review commands: `git diff --check`, `git -C 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157 diff --check`, and status/diff inspection. No commits or pushes were performed in either repository.

Local secret persistence (2026-11-09, assistant): checked `.env` absence with `Test-Path`, verified `git -C 01_ServerDeployment/project/udacity_server_deployment_exercises_cd0157 check-ignore .env`, and inspected `.dockerignore`. Created `.env` with PowerShell `[System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)` encoded with `[Convert]::ToHexString`, using `System.IO.FileMode.CreateNew` to avoid overwriting an existing file. Wrote only `JWT_SECRET=<generated value>` and a newline using ASCII encoding; verified the expected 64-hex-character format without printing the value. Confirmed Git ignores the file and Docker excludes `.env*`. Added the runtime instructions above and ran `git diff --check`. No AWS secret was created or changed.

### Publishing the fork — 2026-11-09

The user requested pushing the project submodule changes. Inspection found they had already been committed as `ba5983b8d7e1b61247c2d851cd94578d21d45778` (three configuration files only) in detached HEAD; no additional commit was needed. `.env` remains ignored and untracked. The assistant checked `git status --short`, `git remote -v`, `git branch -avv`, `git diff --check`, `git diff --stat`, `git check-ignore .env`, `git ls-files .env`, `git show --stat --oneline HEAD`, and the commit diff. Ran `git fetch origin master` successfully, then checked ancestry with `git merge-base --is-ancestor origin/master HEAD` and `git merge-base --is-ancestor master HEAD`. Next: fast-forward local `master`, push normally, and verify the remote commit. The initial implementation's statements that changes were uncommitted describe its earlier state, before this existing commit was observed.

Publishing result (2026-11-09, assistant): successfully ran `git switch master`, `git merge --ff-only ba5983b8d7e1b61247c2d851cd94578d21d45778`, and `git push origin master`. GitHub advanced `master` from `52ce056` to `ba5983b`. Verified with `git ls-remote origin refs/heads/master`: remote commit is `ba5983b8d7e1b61247c2d851cd94578d21d45778`. Final `git status --short` is empty, `git branch --show-current` is `master`, `git check-ignore .env` confirms exclusion, and `git ls-files .env` is empty. The parent README update and any parent submodule-pointer change were not committed or pushed by this action. The user's checklist step 1 (publishing the configuration) is now complete; proceed to tool verification and AWS sign-in.

For future entries, use: date/time (Europe/Budapest), actor, exact sanitized command or console action, result, verification/evidence, and next action. Include unsuccessful attempts and their resolution.

## Reviewer evidence

- External application URL: pending.
- Source repository: `https://github.com/mxagar/udacity_server_deployment_exercises_cd0157`, branch `master`; initial implementation published at `ba5983b8d7e1b61247c2d851cd94578d21d45778`. Final deployment/test-gate correction commit remains pending.
- Passing local tests and Docker endpoint checks: 2026-11-09, 11 pytest cases passed; Docker image built; health/auth/contents and missing/invalid token HTTP checks passed. See implementation session log.
- Successful pipeline/build execution: pending.
- Failed-test execution and proof publication/deployment were blocked: pending.
- Corrected successful execution and live endpoint checks: pending.
- Review completed / cleanup verified: pending.

## References

- [Full course project instructions](../README.md#project-deploy-your-flask-app-to-kubernetes-using-eks)
- [EKS Kubernetes version support](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)
- [EKS Kubernetes access methods](https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html)
- [CodeBuild environment variables](https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html)
