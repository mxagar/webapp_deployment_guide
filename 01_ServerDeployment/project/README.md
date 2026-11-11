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
docker build -t simple-flask-project .
docker run --rm --name simple-flask-container --publish 127.0.0.1:8080:8080 --env-file .env simple-flask-project
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
| Build gate | pytest runs before image build; failed builds cannot publish or deploy. | Verified live in Part 2 D, 2026-11-11 |
| Deployment | Image pushed to ECR; manifest applied; rollout completes; external Service URL serves all three endpoints. | Verified for corrected commit `7c9bf6e`; three ready replicas |
| Evidence | Reviewer URL, successful pipeline execution, failed-test gate demonstration, and corrected successful execution recorded. Final tests pass. | Recorded below and in the fork's `evidence/` directory |
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

### Reusing a JWT after restarting the server

**Restarting the server does not require a new JWT.** You can reuse an existing token as long as it has not expired and the server loads the same `JWT_SECRET`. This project's tokens expire two weeks after issuance.

The local `.env` file preserves the signing secret between restarts, but the application does not read that file automatically: load it into the server's environment before starting Python, or pass it to Docker with `--env-file .env`. Reuse that saved secret rather than generating a new one at every startup.

Changing `JWT_SECRET` invalidates tokens signed with the previous value. Request a new token from `/auth` if the old token expires or the signing secret changes. Also distinguish server restarts from closing the client terminal: closing that terminal loses its temporary `TOKEN` variable, so you would need to supply the existing token again or request a new one.

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

Use **PowerShell** for this step. Environment variables use the `$env:` prefix both when assigning and reading them:

```powershell
$env:AWS_PROFILE="deployment-course"
$env:AWS_DEFAULT_REGION="eu-central-1"
$env:CLUSTER_NAME="simple-jwt-api"
$env:STACK_NAME="simple-jwt-api-pipeline"
$env:PATH = 'C:\Program Files\Amazon\AWSCLIV2;' + $env:PATH

aws --version
eksctl version
kubectl version --client
```

If the SSO profile is absent, run the wizard once:

```powershell
aws configure sso --profile deployment-course
aws configure set region eu-central-1 --profile deployment-course
```

Then authenticate and verify the intended account:

```powershell
aws sso login --profile $env:AWS_PROFILE
aws sts get-caller-identity --profile $env:AWS_PROFILE
aws eks describe-cluster-versions --profile $env:AWS_PROFILE --region $env:AWS_DEFAULT_REGION --output table
```

Record the selected account/profile/region and supported version. The identity needs permissions to create EKS, networking, EC2 nodes, IAM roles/policies, CloudFormation, CodePipeline, CodeBuild, ECR, S3, Lambda, and SSM resources. An SSO login does not itself grant these permissions. Resolve denied permissions before proceeding.

### 3. Create and verify EKS

Use **PowerShell**, with the profile and region set in step 2. This starts chargeable AWS resources. First check whether an existing course cluster can be reused:

```powershell
aws eks list-clusters --region $env:AWS_DEFAULT_REGION --profile $env:AWS_PROFILE
```

For a new dedicated cluster, after verifying regional version availability:

```powershell
$env:CLUSTER_NAME = 'simple-jwt-api'
$env:KUBERNETES_VERSION = '1.37'
eksctl create cluster --name $env:CLUSTER_NAME --nodes 2 --version $env:KUBERNETES_VERSION --instance-types t3.medium --region $env:AWS_DEFAULT_REGION --profile $env:AWS_PROFILE
aws eks update-kubeconfig --name $env:CLUSTER_NAME --region $env:AWS_DEFAULT_REGION --profile $env:AWS_PROFILE
kubectl config current-context
kubectl get nodes
aws eks describe-cluster --name $env:CLUSTER_NAME --region $env:AWS_DEFAULT_REGION --profile $env:AWS_PROFILE --query 'cluster.{version:version,authenticationMode:accessConfig.authenticationMode}' --output table
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

This step stores the **same signing secret in two places**:

| Location | Resource name | Purpose |
| --- | --- | --- |
| AWS Systems Manager → Parameter Store | `JWT_SECRET`, type `SecureString` | Encrypted storage in your selected AWS account and region; CodeBuild retrieves the value using the buildspec's `parameter-store` mapping. |
| EKS cluster → Kubernetes Secret | `default/jwt-secret`, key `JWT_SECRET` | Supplies the value to the Flask Pods through the manifest's `secretKeyRef`. |

The flow is: generate a value in your terminal → send it to Parameter Store with `aws ssm put-parameter` → copy the same value into Kubernetes with `kubectl create secret ... | kubectl apply ...` → expose it as the Pod's `JWT_SECRET` environment variable at startup. When copying a value already stored in Parameter Store, retrieve it privately using `aws ssm get-parameter --with-decryption` first. CodeBuild's environment and the application's Pod environment are separate; both must receive the intended value.

The local **`.env` remains a separate local file**. The generation command below creates a new secret for AWS and does not read or update `.env`. To reuse your local secret, load `.env` into the terminal environment first and skip generation. These resources store the signing secret, not the JWT access tokens issued to clients. Preserve existing project secrets unless deliberately rotating them; keep values out of Git and shared output.

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

AWS CLI troubleshooting (2026-11-09, user and assistant): user reported `aws --version` failing in the Poetry `quality-bot` environment with missing `awscli`. Assistant used the systematic-debugging workflow; ran `Get-Command aws -All`, `where.exe aws`, `Test-Path 'C:/Program Files/Amazon/AWSCLIV2/aws.exe'`, and `Get-Command winget` to inspect resolution and available tooling. Consulted official AWS CLI installation/troubleshooting documentation. Ran `& 'C:/Program Files/Amazon/AWSCLIV2/aws.exe' --version` successfully, then temporarily prepended its directory to PATH in the assistant's PowerShell process and verified `aws --version` and `(Get-Command aws).Source`: AWS CLI 2.27.22 from the standalone installation. Documented Bash/PowerShell commands above for the user's separate terminal; their application there remains pending. Ran `git diff --check` after updating this README. No AWS account calls, installations, or persistent environment changes were made.

Region-variable troubleshooting (2026-11-09, user and assistant): user ran `aws eks describe-cluster-versions --region "$AWS_DEFAULT_REGION" --output table`; CLI argument parsing failed with `--region: expected one argument`, before a service request. Assistant documented setting/exporting the profile and region in the current shell, displaying their non-secret values, and retrying; also provided an explicit profile/region alternative and PowerShell syntax. Retry and regional version results remain pending user execution. README edited with `apply_patch` and checked using `git diff --check`.

PowerShell correction (2026-11-09, assistant, requested by user): read the current step 2 and corrected its mixed Bash/PowerShell block to PowerShell only. Updated SSO login, STS identity, and EKS version commands to use `$env:AWS_PROFILE` and `$env:AWS_DEFAULT_REGION`; corrected the region troubleshooting section and its earlier incorrect inference about the user's shell. Documented the shell scope of these assignments. Updated using `apply_patch` and verified documentation formatting with `git diff --check`; no AWS commands were executed.

Section 3 PowerShell conversion (2026-11-09, assistant): inspected the current EKS section using `Get-Content` and `rg`, then used `apply_patch` to convert its fenced commands and environment-variable references to PowerShell. Set the cluster name and version with `$env:` and made profile/region explicit in AWS calls. Verified the documentation with `git diff --check`. Commands are instructions only; no EKS resources were created or queried during this edit.

Dual-shell course instructions (2026-11-11, assistant): at the user's request, updated all 53 Bash command blocks within `../README.md`'s “Project: Deploy Your Flask App to Kubernetes Using EKS” section. Each mixed `text` block now contains `# Bash` followed by the original commands, then `# PowerShell` with equivalent commands. Added guidance to run only one alternative. Converted environment variables, inline assignments, line continuations, HTTP/JSON requests, temporary paths, secret cleanup, and UTF-8 file writing where needed. PowerShell HTTP examples use `Invoke-RestMethod`; buildspec/Dockerfile/YAML/JSON/Python syntax remains unchanged.

Documentation-edit commands: inspected repository guidance/status with `rg --files --hidden -g AGENTS.md`, `git status --short`, `git diff --stat`, and scoped `rg`/`Get-Content` reads; extracted the section's Bash fences using PowerShell regular expressions. Used a temporary `.tmp_convert_project_shells.py` helper, created with `apply_patch` and run via `python .tmp_convert_project_shells.py`, to apply the conversions. The helper asserted that all 53 original Bash alternatives and all text before the project section were preserved. Then used `[System.Management.Automation.Language.Parser]::ParseInput` on every PowerShell alternative: all 53 parsed without errors; a scan found no remaining Bash `export`, `unset`, `printf`, or backslash continuation syntax in those alternatives. Ran `git diff --check` successfully (only Git's existing line-ending conversion warnings), reviewed the diff, and removed the temporary helper with `apply_patch`. Existing user edits in both README files were retained. This session changed documentation only; no AWS, EKS, Docker, application, commit, or push operations were performed.

Optional jq installation failure (2026-11-11, user and assistant): user ran `choco install jq` in a non-elevated Windows shell, accepted the continuation prompt, and reported failure installing jq 1.8.2. Chocolatey could not access its package lock or create `C:\ProgramData\chocolatey\lib-bad`; installation did not succeed. The supplied output establishes filesystem permission failures but does not prove an abandoned lock. Assistant inspected the endpoint instructions with `rg`/`Get-Content`, clarified in the course README that jq is unnecessary for the PowerShell alternatives, removed the PowerShell installation command, and explained `$auth.token` extraction. User can continue directly to Part 1 A step 5 using PowerShell's `Invoke-RestMethod` and `ConvertTo-Json`. Changes applied using `apply_patch` and checked with `git diff --check`. No installation retry, lock deletion, system permission changes, or AWS operations were performed.

Optional Windows jq installation instructions (2026-11-11, assistant): user asked how to install jq on Windows despite its being optional for these PowerShell examples. Checked `Get-Command winget` (available) and the [official jq download instructions](https://jqlang.org/download/). Suggested the following PowerShell commands; these are planned user actions, not executed installations:

```powershell
winget install --id jqlang.jq --exact --source winget
# Close and reopen PowerShell after installation, then verify:
jq --version
```

Alternatively, open PowerShell with **Run as Administrator** and run `choco install jq -y`, then verify `jq --version` in a new terminal. This addresses the earlier non-elevated permission failure; a continuing lock error requires further diagnosis rather than deleting the lock blindly. No package installation or system changes were performed by the assistant. Added these instructions using `apply_patch` and checked formatting with `git diff --check`.

Windows jq installation result (2026-11-11, user-reported): `winget install jqlang.jq` successfully installed jq 1.8.2, verified the downloaded executable's hash, added the `jq` command alias, and reported a PATH update requiring a shell restart. The user immediately ran `jq --version` in the same PowerShell session and received `CommandNotFoundException`; verification has not yet succeeded because that session still has its previous PATH. Next: close and reopen the terminal (restart the host application too if its integrated terminal still inherits an old PATH), then run `jq --version`. Alternatively, append the saved user PATH to the current process with `$env:Path += ';' + [Environment]::GetEnvironmentVariable('Path', 'User')` and retry. No reinstall is needed based on the reported output. Assistant recorded the result using `apply_patch` and checked documentation with `git diff --check`; did not run an installation or modify the system PATH.

Local API connection troubleshooting (2026-11-11, user and assistant): user reported `Invoke-RestMethod` to `http://127.0.0.1:8080/auth` failing with “Unable to connect to the remote server”. Assistant checked listening ports with `Get-NetTCPConnection -State Listen` filtered to 80/8080/18080 (no listeners returned), inspected available `docker`/`uv` commands and local `.env`/`.venv`/`main.py` presence without reading secret values into output, and confirmed `main.py` starts Flask on 127.0.0.1:8080. `docker ps --format '{{.Names}} {{.Ports}} {{.Status}}'` failed because the Docker Desktop Linux engine pipe was absent. Added PowerShell instructions to the course's Part 1 A step 5: start Flask in terminal 1 with the saved `.env` secret, leave it running, then verify health and issue requests in terminal 2. Also clarified the container's host port 80 and same-machine localhost requirement. Used `apply_patch` and `git diff --check` for documentation; no server or Docker engine was started, and no AWS actions were performed. User startup/retry results remain pending.

Local API connection cause confirmed (2026-11-11, user-reported): user confirmed the Flask server had not been started when `/auth` was requested. Start it in terminal 1 and leave it running, then retry the health/auth workflow in terminal 2. Successful startup and endpoint responses have not yet been reported for this attempt. Assistant recorded this clarification using `apply_patch`; no commands or services were started.

JWT reuse remark (2026-11-11, assistant): at the user's request, inspected the JWT/local-secret sections with `rg`, then added the server-restart explanation using `apply_patch`: unexpired tokens remain valid with the same signing secret, this starter uses a two-week lifetime, `.env` must be loaded explicitly, and closing the client shell loses its temporary token variable. Checked formatting with `git diff --check`. Documentation only; no tokens, secrets, servers, or AWS resources were changed.

JWT remark location clarification (2026-11-11, assistant): user reported the remark was not visible. Verified with `rg` that it existed under “Reusing a JWT after restarting the server” in this project README, then also placed the explanation beside the environment/server-start instructions in `../README.md`, the course project section. Clarified that random secret generation is initial setup and that subsequent starts should load the saved `.env` value. Updated using `apply_patch` and checked with `git diff --check`; documentation only.

Environment filename clarification (2026-11-11, user and assistant): user confirmed the local environment file is `.env`. Assistant located filename references using `rg`, then used a scoped PowerShell text replacement to change the course project section's environment-file creation examples, Git-ignore checks, Docker `--env-file` arguments, cleanup guidance, and rubric example to `.env`. Added a warning to skip initial file creation when `.env` already holds the signing secret. This project README already used `.env`. Verified with `rg` and `git diff --check`. Documentation only; no environment file or secret was read, overwritten, renamed, or rotated.

Descriptive local Docker image name (2026-11-11, assistant): user proposed `simple-flask-project` instead of `myimage`. Inspected references with `rg`, then updated the course project section's Bash/PowerShell build and run commands, accompanying explanation, and cleanup reference using a scoped PowerShell replacement. Updated this README's active local build/run example with `apply_patch`. Historical verification logs retain the actual `eks-flask-project:local` name used during that earlier session. Checked with `git diff --check`. Documentation only; no Docker images were built, retagged, or removed.

Descriptive local Docker container name (2026-11-11, assistant): at the user's request, located references with `rg` and replaced `myContainer` with `simple-flask-container` within the course project section, including Bash/PowerShell run, stop, remove, and cleanup examples. Updated this README's active Docker run example from `flask-project` to the same container name using `apply_patch`. Earlier unrelated course examples and historical execution logs were preserved. Checked formatting with `git diff --check`. Documentation only; no running container was renamed or changed.

Docker quoted log-level failure and recovery (2026-11-11, user and assistant): user ran `docker run --name simple-flask-container --env-file=.env -p 127.0.0.1:80:8080 simple-flask-project`; Gunicorn exited because Python logging received literal quote characters in `LOG_LEVEL` (`ValueError: Unknown level: '"DEBUG"'`). Assistant inspected only the `LOG_LEVEL` line via `Get-Content .../.env | Where-Object { $_ -match '^\s*LOG_LEVEL\s*=' }` and checked submodule status. Initial `docker inspect --format '{{.State.Status}} {{.State.ExitCode}} {{json .Mounts}}' simple-flask-container` was sandbox-blocked; approved retry showed `exited 3 []`. An attempted narrowly scoped `.env` correction aborted without writing because the quoted line no longer matched. Reinspection, including the log-level line's character codes, confirmed it had already become `LOG_LEVEL=DEBUG`; the assistant did not write the file or change the signing secret.

After verifying again that the named container was stopped, the assistant successfully executed from the submodule directory:

```powershell
docker rm simple-flask-container
docker run --detach --name simple-flask-container --env-file .env -p 127.0.0.1:80:8080 simple-flask-project
```

New container ID: `e9381df6c866374900629108555aea670fcf86db221886a87721bdcf21b81bc5`. Verified health with `Invoke-RestMethod -Uri 'http://127.0.0.1:80/'`, issued a token via `Invoke-RestMethod -Method Post` with a JSON test body, and used that token in the Authorization header to verify `/contents`; all passed and neither token nor signing secret was displayed. Then ran `docker inspect --format '{{.State.Status}}' simple-flask-container` and `docker logs --tail 8 simple-flask-container`: state `running`, successful worker startup, and application DEBUG logging confirmed. Container remains running in the background on host port 80. Added the quoting/recreation explanation to the course README with `apply_patch` and checked documentation using `git diff --check`. No rebuild, application-code changes, or AWS operations were needed.

README visibility check (2026-11-11, assistant): user could not see the edits. Used `Get-Location`, scoped `rg`, `Get-Item`, and `git status --short` to verify the saved course README contains the Docker quoting explanation at line 4757 and this project README contains the recovery log at line 593. Also searched through the user's `C:/Users/A200239740/git_repositories/webapp_deployment_guide` path and confirmed the same passages are visible there; `git rev-parse --show-toplevel` resolved to the E: workspace. Both README changes remain local and uncommitted. The README inside the forked submodule is a separate file and was not the destination of these documentation edits.

Existing container name conflict (2026-11-11, user and assistant): user repeated `docker run --name simple-flask-container --env-file=.env -p 127.0.0.1:80:8080 simple-flask-project`; Docker rejected it because container `e9381df6c866374900629108555aea670fcf86db221886a87721bdcf21b81bc5` from the preceding recovery already exists. Assistant ran `docker ps -a --filter name=^/simple-flask-container$ --format '{{.Names}} {{.Status}} {{.Ports}}'`; sandbox pipe access was denied, so an approved read-only retry confirmed it was running with `127.0.0.1:80->8080/tcp`. `Invoke-RestMethod -Uri 'http://127.0.0.1:80/' -TimeoutSec 5` returned `Healthy`. Existing container can be used directly; nothing was stopped, removed, or recreated. Added the distinction between Docker run/start and existing running containers to the course README with `apply_patch`; verified formatting using `git diff --check`.

Pipeline overview simplification (2026-11-11, assistant): at the user's request, inspected Part 2 A and its table-of-contents entries with `rg`, then rewrote the overview as eight concise bullets without subsections. Preserved its runtime/dependency context, regional constraint, IAM policy files and trust relationship, Kubernetes RBAC mapping, GitHub token parameters, CloudFormation/buildspec links, separate secret delivery, deployment flow, and pytest publication/deployment gate. Explicitly identified Parts 2 B–D as the successive implementation sections and removed the three obsolete subsection links from the table of contents. Applied with `apply_patch`; verified using a scoped section check and `git diff --check`. Documentation only; no implementation or AWS commands were run.

Recurring AWS launcher conflict (2026-11-11, user and assistant): user attempted `aws sso login --profile "$env:AWS_PROFILE"` and then `aws sso login --profile "deployment-course"`; both failed importing `awscli` from the old Poetry launcher's `Scripts/aws.cmd`. Assistant ran `Get-Command aws -All` and `& 'C:/Program Files/Amazon/AWSCLIV2/aws.exe' --version`: standalone AWS CLI 2.27.22 works, while Python environment launchers precede it on PATH. Added the session PATH correction and version check directly to the course's Part 2 B PowerShell setup, plus the absolute executable fallback and explanation that profile changes do not fix command selection. Applied using `apply_patch` and checked with `git diff --check`. No SSO login, profile edit, permanent PATH change, or AWS resource operation was performed; user login retry remains pending.

CloudFormation role-field clarification (2026-11-11, assistant): user asked whether to add the Udacity deployment role during stack creation. Inspected course step 2.3 and the fork template's `KubectlRoleName` parameter, custom resource, and CodeBuild role ARN configuration using `rg`. Consulted [AWS CloudFormation service-role documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-servicerole.html). Clarified course steps 2–3: supply `UdacityFlaskDeployCBKubectlRole` as the template parameter's role name; it must already exist. The optional stack Permissions/IAM role field is a different CloudFormation service role and should remain empty for this exercise unless account policy requires a separately configured service role. Used `apply_patch` and `git diff --check`; no AWS role or stack changes were made.

Stack submission reported (2026-11-11, user and assistant): user confirmed the CloudFormation stack was already submitted before revisiting the parameter instructions. Exact submitted name, current status, parameter values, and whether the optional execution-role selection was removed have not yet been confirmed. Assistant inspected step 2.3 and template defaults with `rg` and consulted AWS stack-status/service-role recovery documentation. `KubectlRoleName` defaults to `UdacityFlaskDeployCBKubectlRole`, so not editing that parameter does not by itself establish an error. Added guidance to inspect the existing stack's status, non-secret parameters, Stack info role, and first failure event before deciding recovery. Used `apply_patch` and `git diff --check`; no cloud stack was inspected through the account, updated, deleted, or recreated by the assistant.

Submitted stack role inspection instructions (2026-11-11, assistant): user asked how to check the optional execution-role selection. Consulted official AWS stack-information documentation, inspected the existing guidance with `rg`, and added the console path **Stack info → Overview → IAM role**, interpretation of unset versus the Udacity role ARN, and a read-only `describe-stacks` query limited to status and `RoleARN`. Provided Bash and PowerShell alternatives; the PowerShell version uses the standalone AWS CLI path and backtick continuations. Applied with `apply_patch` and checked formatting with `git diff --check`. Commands are instructions only; user results remain pending, and no AWS account query or change was performed by the assistant.

Submitted deployment-role parameter confirmed (2026-11-11, user-reported): the AWS console's Parameters tab shows `KubectlRoleName = UdacityFlaskDeployCBKubectlRole`, matching the template's expected deployment role. This confirms that parameter only; the separate CloudFormation execution role under **Stack info → Overview → IAM role** and the stack's current status are still unconfirmed. Assistant recorded the result using `apply_patch` and checked formatting with `git diff --check`; no AWS changes were made.

Kubernetes signing-secret reference rechecked (2026-11-11, assistant): user asked to add the `JWT_SECRET` environment block in `simple_jwt_api.yml`. Read the manifest with `Get-Content` and verified the existing `simple-jwt-api` container already has exactly the requested `secretKeyRef` (`name: jwt-secret`, `key: JWT_SECRET`) alongside its image, readiness probe, security context, and ports. `git status --short` in the submodule was clean, and `git log -1 --oneline` showed implementation commit `ba5983b`, previously pushed. No duplicate or code change was needed. Updated the course instruction with `apply_patch` to make the existing implementation explicit, then ran `git diff --check`. Creating/verifying the actual cluster Secret remains a separate user step; no Kubernetes or AWS command was executed.

Signing-secret storage explanation (2026-11-11, assistant): at the user's request, inspected the secret-delivery sections with `rg` and added the explanation to both the course README (Part 2 C step 3) and this project README (execution-guide step 6). Documented Parameter Store versus Kubernetes Secret names/purposes, terminal-to-AWS/cluster flow, CodeBuild versus Pod environments, the separate local `.env`, newly generated versus reused values, and signing secrets versus client access tokens. Updated using `apply_patch` and verified with `git diff --check` and scoped text searches. Documentation only; no secret values were read or changed and no AWS/Kubernetes commands were executed.

Initial pipeline Parameter Store failure investigated (2026-11-11, user and assistant): user supplied CodeBuild logs showing `DOWNLOAD_SOURCE` failed at 15:28 UTC (16:28 Europe/Budapest), with `Decrypted Variables: parameter does not exist: JWT_SECRET`. No buildspec phase commands ran in that execution. Assistant inspected the buildspec's `JWT_SECRET: JWT_SECRET` mapping and the existing guide, then consulted official CodeBuild troubleshooting/buildspec documentation through web and Context7. Used the standalone AWS CLI v2 for read-only checks under profile `deployment-course`; no secret values were printed or decrypted.

Read-only command record (all AWS calls used `C:\Program Files\Amazon\AWSCLIV2\aws.exe`; executed in PowerShell):

```powershell
aws configure get region --profile deployment-course
aws sts get-caller-identity --profile deployment-course --query '{Account:Account}' --output json
aws ssm get-parameter --name JWT_SECRET --profile deployment-course --region eu-central-1 --query 'Parameter.{Name:Name,Type:Type,Version:Version}' --output json
aws ssm get-parameter --name JWT_SECRET --profile deployment-course --region eu-central-1 --query 'Parameter.{Name:Name,Type:Type,Version:Version,LastModifiedDate:LastModifiedDate}' --output json
aws codebuild batch-get-projects --names simple-jwt-api-pipeline --profile deployment-course --region eu-central-1 --query '{Projects:projects[].{Name:name,Arn:arn,ServiceRole:serviceRole},NotFound:projectsNotFound}' --output json
$buildIds = aws codebuild list-builds-for-project --project-name simple-jwt-api-pipeline --sort-order DESCENDING --profile deployment-course --region eu-central-1 --query 'ids[:3]' --output json | ConvertFrom-Json
aws codebuild batch-get-builds --ids $buildIds --profile deployment-course --region eu-central-1 --query 'builds[].{Id:id,Status:buildStatus,Started:startTime,Phase:currentPhase}' --output json
```

Findings: `JWT_SECRET` now exists as `SecureString`, version 1, in `eu-central-1`, account `077073585279`. Its last-modified/initial creation timestamp is **16:35:30.815 Budapest time**, after the failed run. The CodeBuild project `simple-jwt-api-pipeline` is in that same account/region. Its only returned build was `simple-jwt-api-pipeline:679d237f-5c32-4e3f-ada5-e5620d9db148`, started 16:27:51.755, status FAILED; no newer retry was found. This supports a missing parameter at initial build time, now resolved by the later parameter creation. Do not overwrite it merely to fix the historical failure. Next user action: complete the secret-delivery steps if still outstanding, then choose **CodePipeline → pipeline → Release change** and inspect the new execution. The assistant did not create/rotate a parameter, change IAM, or retry/deploy the pipeline. Added the failure explanation to the course README and this log using `apply_patch`; verified with `git diff --check`.

Build-trigger explanation added (2026-11-11, assistant): at the user's request, read the course's “4. Understand and configure buildspec.yml” section with `rg`, then added the initial CloudFormation → CodePipeline → CodeBuild sequence, subsequent GitHub push triggers, manual **Release change** executions, pipeline artifact dependency, and the fact that Parameter Store changes do not trigger or resume builds. Also explained `DOWNLOAD_SOURCE` secret resolution before buildspec commands and why the initial run can precede parameter creation. Applied with `apply_patch` and checked using `git diff --check`. Documentation only; no pipeline execution or AWS change was initiated.

CodePipeline reference added (2026-11-11, assistant): user requested an explicit CodePipeline reference in the buildspec section. Read the current section with `Get-Content`/`rg`, then linked its explanation to the earlier CloudFormation pipeline-creation section and the regional CodePipeline console. Clarified the template's Source → Build stages and that CodeBuild runs the buildspec's publication/deployment commands. Applied using `apply_patch` and checked with `git diff --check`. Documentation only; no pipeline was started or changed.

### Part 2 D live test-gate demonstration — 2026-11-11

User requested implementing all of Part 2 D, including its temporary failing-test commit/push and corrected commit/push. The existing fork already runs pytest after dependency synchronization and guards `post_build` before publication/deployment. Baseline: clean `master` at `67a0fea95f572af1783bfc2343cac83c8ccd7826`, matching fetched `origin/master`; 11 local tests passed. Latest build `simple-jwt-api-pipeline:032089cb-814e-497d-ba92-521a1930fe5a` succeeded for that commit, and the deployment has three ready replicas.

Execution checklist:

- [x] Inspect Part 2 D, existing test gate/tests, clean fork branch, remote, and live successful baseline. Initial uv cache access was sandbox-blocked; approved retry passed all 11 cases.
- [x] Save sanitized baseline image, replica, endpoint, and ECR evidence in [baseline.json](./udacity_server_deployment_exercises_cd0157/evidence/baseline.json): healthy endpoint, three ready replicas, deployment revision 2, and two ECR images.
- [x] Add the prescribed temporary assertion inside `test_health`, verify local failure, commit/push to the monitored fork branch, and wait for the triggered pipeline.
- [x] Verify the pipeline fails on pytest, publishes no new image, and leaves the baseline deployment healthy and unchanged. Saved [failed-run.json](./udacity_server_deployment_exercises_cd0157/evidence/failed-run.json).
- [x] Remove the assertion, rerun all tests, commit/push the correction, and verify a new successful pipeline/rollout and live API checks. Saved [restored-run.json](./udacity_server_deployment_exercises_cd0157/evidence/restored-run.json).
- [x] Save execution IDs, commits, results, and commands here; finish with passing tests and a clean fork checkout. Preserved unrelated parent/lab changes.

Progress: inserted the prescribed assertion in `test_health`; local pytest returned exactly one intentional failure and 10 passes. Created commit `d01c8400093f7a11ba43112d6b20ee62eca91dc5`. The first `git push` waited in Git Credential Manager and was canceled; a GitHub connector write attempt returned HTTP 403 and made no change. Git's existing configuration has both `manager` and `store` helpers. Inspected them with `git config --show-origin --get-all credential.helper` and read `git credential-manager github login --help`. Retried successfully using the already-configured store without interactive prompts: `git -c credential.helper= -c credential.helper=store -c credential.interactive=never push origin master` (with `GIT_TERMINAL_PROMPT=0` for that process). No credential values were read or printed and no persistent Git configuration was changed. GitHub change detection then automatically started pipeline execution `8dfc1287-f54e-4bce-af0d-63ebe861a0fd`, with build `simple-jwt-api-pipeline:f7ce2d8b-cd12-44a3-918b-49214350f96f` for the expected failure commit. Results are recorded below.

Failure result: pipeline and build failed as intended. CloudWatch logs show `AssertionError: Intentional check: this commit must not deploy` and `1 failed, 10 passed`; `PRE_BUILD` failed and later build/publication/deployment phases did not run. Compared ECR digest/tag sets, Deployment image and revision, Pod UIDs, ready replica count, and endpoint with the baseline: all unchanged, three ready replicas, `Healthy`. A later read needed to refresh the AWS SSO cache; the sandbox denied that cache write, and an approved retry succeeded. No secret values were queried or displayed. Restored the original test file, reran the full suite (11 passed), then committed/pushed `7c9bf6e79b512fe32ccd2cf5e187e2d6f92b9f34` to `master`. The final source tree matches the pre-demonstration tree; the two commits retain evidence of the failing/passing sequence.

**Corrected execution succeeded.** CodePipeline automatically started `b3de9dbe-67cb-4e3f-89bd-4580d985e652`; CodeBuild `simple-jwt-api-pipeline:98bb9388-2e29-4b3c-a0f9-7ed56e4f0e65` ran from 17:25:52 to 17:26:53 Budapest time. Logs show **11 passed**, a successful build-status check, Docker push, manifest apply, and successful rollout. Verified the deployed ECR tag ends in `7c9bf6e7`, all three replicas are updated/ready, and health/auth/contents work at the external URL. Missing and invalid tokens both return 401. The failed run did not enter `post_build`; the successful run executed its guard before publication. No temporary failing assertion remains.

| Evidence | Intentional failure | Restored passing suite |
| --- | --- | --- |
| Fork commit | [`d01c840`](https://github.com/mxagar/udacity_server_deployment_exercises_cd0157/commit/d01c8400093f7a11ba43112d6b20ee62eca91dc5) | [`7c9bf6e`](https://github.com/mxagar/udacity_server_deployment_exercises_cd0157/commit/7c9bf6e79b512fe32ccd2cf5e187e2d6f92b9f34) |
| Pipeline execution | `8dfc1287-f54e-4bce-af0d-63ebe861a0fd` — Failed | `b3de9dbe-67cb-4e3f-89bd-4580d985e652` — Succeeded |
| CodeBuild run suffix | `f7ce2d8b-cd12-44a3-918b-49214350f96f` | `98bb9388-2e29-4b3c-a0f9-7ed56e4f0e65` |
| pytest | 1 intentional failure, 10 passed | 11 passed locally and in CodeBuild |
| Publication/deployment | No push/apply; ECR, revision, image and Pods unchanged | New tag published, rollout completed, 3 ready replicas |
| Saved results | [failed-run.json](./udacity_server_deployment_exercises_cd0157/evidence/failed-run.json) | [restored-run.json](./udacity_server_deployment_exercises_cd0157/evidence/restored-run.json) |

Local execution commands (run from the fork's submodule; the assertion was edited with `apply_patch` and later removed):

```powershell
git status --short
git branch -avv
git fetch origin master
git rev-parse HEAD
git rev-parse origin/master
git check-ignore .env
uv run --locked python -m pytest test_main.py
# After inserting the prescribed temporary assertion: expected 1 failed, 10 passed.
uv run --locked python -m pytest test_main.py
git diff --check
git diff --name-only
git add -- test_main.py
git commit -m 'test: demonstrate failing tests block EKS deployment'
$env:GIT_TERMINAL_PROMPT = '0'
git -c credential.helper= -c credential.helper=store -c credential.interactive=never push origin master
# After verifying the cloud failure and removing the assertion:
uv run --locked pytest
git diff --check
git add -- test_main.py
git commit -m 'test: restore passing suite after deployment-gate proof'
git -c credential.helper= -c credential.helper=store -c credential.interactive=never push origin master
git diff --exit-code 67a0fea95f572af1783bfc2343cac83c8ccd7826 HEAD
git status --short
```

Cloud verification command record: AWS calls used the standalone CLI and explicit `deployment-course`/`eu-central-1`; repeated read-only status calls waited for the expected commit and terminal results. Queried only selected pipeline/build metadata, not environment secret values. Commands below show the verification calls; the CloudWatch group/stream variables were populated from each build's metadata:

```powershell
$awsExe = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
$pipelineName = 'simple-jwt-api-pipeline-CodePipelineGitHub-upDPTJrhUW5M'
$projectName = 'simple-jwt-api-pipeline'
$repository = 'simple-jwt-api-pipeline-ecrdockerrepository-esyamizthgc4'
$failedBuildId = 'simple-jwt-api-pipeline:f7ce2d8b-cd12-44a3-918b-49214350f96f'
$restoredBuildId = 'simple-jwt-api-pipeline:98bb9388-2e29-4b3c-a0f9-7ed56e4f0e65'
& $awsExe codepipeline list-pipelines --profile deployment-course --region eu-central-1 --query 'pipelines[].{Name:name,Type:pipelineType}' --output json
& $awsExe codepipeline get-pipeline --name $pipelineName --profile deployment-course --region eu-central-1 --query 'pipeline.{ExecutionMode:executionMode,Source:stages[0].actions[0].configuration.{Repository:Repo,Owner:Owner,Branch:Branch,Polling:PollForSourceChanges}}' --output json
& $awsExe codepipeline list-pipeline-executions --pipeline-name $pipelineName --max-results 3 --profile deployment-course --region eu-central-1 --query 'pipelineExecutionSummaries[].{Id:pipelineExecutionId,Status:status,Started:startTime,Commit:sourceRevisions[0].revisionId}' --output json
& $awsExe codebuild list-builds-for-project --project-name $projectName --sort-order DESCENDING --profile deployment-course --region eu-central-1 --query 'ids[:4]' --output json
foreach ($buildId in @($failedBuildId, $restoredBuildId)) {
    $build = & $awsExe codebuild batch-get-builds --ids $buildId --profile deployment-course --region eu-central-1 --query 'builds[0].{Id:id,Status:buildStatus,Commit:resolvedSourceVersion,Started:startTime,Ended:endTime,Phases:phases[].{Name:phaseType,Status:phaseStatus,Contexts:contexts},LogGroup:logs.groupName,LogStream:logs.streamName}' --output json | ConvertFrom-Json
    $messages = & $awsExe logs get-log-events --log-group-name $build.LogGroup --log-stream-name $build.LogStream --start-from-head --profile deployment-course --region eu-central-1 --query 'events[].message' --output json | ConvertFrom-Json
    # Only relevant test, phase, push/apply, guard, and rollout messages were saved.
}
foreach ($executionId in @('8dfc1287-f54e-4bce-af0d-63ebe861a0fd', 'b3de9dbe-67cb-4e3f-89bd-4580d985e652')) {
    & $awsExe codepipeline get-pipeline-execution --pipeline-name $pipelineName --pipeline-execution-id $executionId --profile deployment-course --region eu-central-1 --query 'pipelineExecution.{Id:pipelineExecutionId,Status:status}' --output json
}
& $awsExe ecr describe-images --repository-name $repository --profile deployment-course --region eu-central-1 --query 'imageDetails[].{Digest:imageDigest,Tags:imageTags,Pushed:imagePushedAt}' --output json
kubectl config current-context
kubectl get deployment simple-jwt-api --namespace default -o json
kubectl get service simple-jwt-api --namespace default -o json
kubectl get pods --namespace default -l app=simple-jwt-api -o json
kubectl rollout status deployment/simple-jwt-api --namespace default --timeout=180s
```

Saved snapshots used `ConvertTo-Json` / `Set-Content -Encoding utf8` in `evidence/part2d/`; `Compare-Object` checked ECR digest/tag signatures and Pod UIDs, with direct comparisons for the deployment image, revision, and ready replicas. Live verification used `Invoke-RestMethod` for health, JSON `/auth`, and bearer `/contents`, and `Invoke-WebRequest -SkipHttpErrorCheck` for missing/invalid-token 401 checks. Test tokens were held in memory and removed, never printed or saved. Checked evidence JSON and documentation formatting with `git diff --check` and verified the final fork checkout is clean and matches `origin/master`. Final `git -c credential.helper= -c credential.helper=store -c credential.interactive=never ls-remote origin refs/heads/master` confirmed GitHub's master is `7c9bf6e79b512fe32ccd2cf5e187e2d6f92b9f34`; a scan found no bearer JWT strings in the three evidence JSON files. Parent README/evidence changes and the updated submodule pointer remain local for review; unrelated lab-submodule changes were preserved.

Submission guidance added (2026-11-11, assistant): user requested a Submission section immediately before Cleaning Up. Inspected the course rubric, fork README/runtime/Dockerfile, saved baseline/restored evidence, and current repository status using `rg`, `Get-Content`, and `git status --short`. Added source/evidence handoff instructions, a criterion-to-evidence table, an explicit `python:stretch` versus `python:3.13-slim` rubric exception note, other modernization/naming changes, copyable reviewer notes with the verified commit/URL/execution IDs, and a final submission/review/cleanup checklist. Distinguished the parent guide's evidence files from the standalone fork and avoided claiming a specific portal upload format or screenshot count. Updated the table of contents. Applied using `apply_patch` and checked formatting/section order and referenced evidence paths. Documentation only; no files were packaged, commits/pushes performed, or submission sent.

Evidence publication review (2026-11-11, assistant): user asked whether the evidence files are dangerous and should be committed. Parsed all three `evidence/part2d/*.json` files, reviewed their fields/selected logs, and scanned for bearer JWTs, AWS access-key identifiers, GitHub token patterns, private-key headers, and secret assignments: no matches. Confirmed `.env` is ignored and absent from tracked submodule files with `git check-ignore .env` and `git ls-files .env`. The snapshots contain account/resource identifiers, ECR image metadata, timestamps, execution/Pod IDs, and the public API address; those expose infrastructure details but do not provide credentials. Consulted official AWS identifier guidance and GitHub secret-handling documentation. Recommended committing these curated snapshots for review, with a private review-accessible destination if infrastructure visibility is a concern. Added the scope/limits of this review to the Submission section using `apply_patch` and checked formatting with `git diff --check`. No evidence was altered, committed, pushed, or removed by this audit.

Evidence relocation and submission notes (2026-11-11, user and assistant): user moved the three snapshots into the forked submodule's `evidence/` directory; inspected with `rg --files`, `Get-ChildItem`, and submodule Git status (evidence additions were already staged). `SUBMISSION.md` existed but was empty on disk. Populated it with reviewer notes, relative evidence links, the explicit relocation note, the evidence safety review/disclosed metadata, verification IDs/results, and declared rubric differences. Updated active evidence links in both parent READMEs and corrected the handoff text to reflect the new location. Historical activity entries retain their original capture paths; current files are now under `udacity_server_deployment_exercises_cd0157/evidence/`. Applied with `apply_patch` and scoped PowerShell text replacements; validated JSON, local links, secret-pattern scans, and `git diff --check`. Evidence contents and existing staging were preserved; no commits or pushes were performed. The unrelated staged deletion of `01_ServerDeployment/.gitignore` was left untouched.

Reviewer-facing submission wording corrected (2026-11-11, assistant): user clarified that `SUBMISSION.md` must address the reviewer. Read the existing file and rewrote its framing, API verification steps, evidence provenance, and safety explanation as direct reviewer notes. Removed author-side instructions about committing, packaging, adding screenshots, or choosing private attachments. Retained the verified application commit, live URL, execution IDs, in-repository evidence links, sanitized-metadata explanation, and declared historical rubric differences. Applied using `apply_patch`; checked evidence-link resolution, matching saved results, and `git diff --check`. No evidence, source behavior, staging, commits, or deployment changed.

For future entries, use: date/time (Europe/Budapest), actor, exact sanitized command or console action, result, verification/evidence, and next action. Include unsuccessful attempts and their resolution.

## Reviewer evidence

- Submission notes and evidence safety explanation: [SUBMISSION.md](./udacity_server_deployment_exercises_cd0157/SUBMISSION.md); the evidence snapshots now live in that fork's `evidence/` directory.
- External application URL: [Flask API](http://a801c89a3b3334c9aa490f41d56834f7-6753305.eu-central-1.elb.amazonaws.com).
- Source repository: `https://github.com/mxagar/udacity_server_deployment_exercises_cd0157`, branch `master`; final test-gate correction commit `7c9bf6e79b512fe32ccd2cf5e187e2d6f92b9f34`, pushed and successfully deployed.
- Passing local tests and Docker endpoint checks: 2026-11-09, 11 pytest cases passed; Docker image built; health/auth/contents and missing/invalid token HTTP checks passed. See implementation session log.
- Successful pipeline/build execution: `b3de9dbe-67cb-4e3f-89bd-4580d985e652` / `simple-jwt-api-pipeline:98bb9388-2e29-4b3c-a0f9-7ed56e4f0e65`.
- Failed-test execution and proof publication/deployment were blocked: `8dfc1287-f54e-4bce-af0d-63ebe861a0fd`; unchanged ECR/deployment/Pods confirmed in [failed-run.json](./udacity_server_deployment_exercises_cd0157/evidence/failed-run.json).
- Corrected successful execution and live endpoint checks: 11 tests passed, rollout succeeded, 3 updated/ready replicas, API and 401 checks passed; see [restored-run.json](./udacity_server_deployment_exercises_cd0157/evidence/restored-run.json).
- Review completed / cleanup verified: pending.

## References

- [Full course project instructions](../README.md#project-deploy-your-flask-app-to-kubernetes-using-eks)
- [EKS Kubernetes version support](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)
- [EKS Kubernetes access methods](https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html)
- [CodeBuild environment variables](https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html)
