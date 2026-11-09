# Deploy Your Flask App to Kubernetes Using EKS

This README is the project's requirements checklist, execution guide, and activity log. The detailed [course instructions](../README.md#project-deploy-your-flask-app-to-kubernetes-using-eks) remain the source for the assignment and rubric.

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
| Runtime | Python 3.13 locally, in Docker, and in CodeBuild; dependencies declared in `pyproject.toml`, fixed in `uv.lock`, and installed with uv. | Pending project checkout |
| Docker | Successful local build using `python:3.13-slim`; locked runtime dependencies; entry point `["gunicorn", "-b", ":8080", "main:APP"]`; all endpoints tested. | Pending |
| Local secret | Supply `JWT_SECRET` at runtime through an ignored environment file; do not embed it in the image. | Pending |
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

Initial inspection found its directory unpopulated. The parent records commit `52ce056932fdb1f899505eee8454216a20f48871`. The earlier lab checkout contains a modernized app and regression tests, but does not prove the project checkout's contents. Its reference buildspec lacks pytest execution and a publication guard, and its manifest lacks the Kubernetes Secret reference.

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

Complete local API tests and Docker endpoint checks using the course's Part 1 instructions before provisioning AWS. Record every command and result here. Required buildspec changes include pytest after `uv sync --locked` and `test "$CODEBUILD_BUILD_SUCCEEDING" = "1"` as the first `post_build` command before push/deployment. Add the Pod secret reference described in step 6.

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

For future entries, use: date/time (Europe/Budapest), actor, exact sanitized command or console action, result, verification/evidence, and next action. Include unsuccessful attempts and their resolution.

## Reviewer evidence

- External application URL: pending.
- Source repository and final commit: pending.
- Passing local tests and Docker endpoint checks: pending.
- Successful pipeline/build execution: pending.
- Failed-test execution and proof publication/deployment were blocked: pending.
- Corrected successful execution and live endpoint checks: pending.
- Review completed / cleanup verified: pending.

## References

- [Full course project instructions](../README.md#project-deploy-your-flask-app-to-kubernetes-using-eks)
- [EKS Kubernetes version support](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)
- [EKS Kubernetes access methods](https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html)
- [CodeBuild environment variables](https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html)
