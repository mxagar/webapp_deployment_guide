# Vast.ai GPU Deployment Guide

> **Companion notebook:** [`lab/vastai.ipynb`](./lab/vastai.ipynb) contains the tested, end-to-end example for this guide. It rents a 2×RTX 3090 instance, starts the official `ollama/ollama` image, pulls **Qwen3.8-27B** as `qwen3.8:27b-q4_K_M`, reaches Ollama through a private SSH tunnel, calls its OpenAI-compatible API, measures tokens per second, and destroys the instance afterward.

The notebook is the canonical runnable example for this guide. It deliberately keeps Ollama's unauthenticated local API off the public Internet.

This guide was reviewed against the current Vast.ai and Ollama documentation on 2026-09-04. Marketplace prices, available offers, templates, image versions, and serverless defaults can change; verify those values in the console immediately before renting capacity.

## Official references

- [Vast.ai: Find and rent instances](https://docs.vast.ai/guides/instances/choosing/find-and-rent)
- [Vast.ai CLI quickstart](https://docs.vast.ai/cli/hello-world)
- [Vast.ai: Create an instance](https://docs.vast.ai/cli/reference/create-instance)
- [Vast.ai: SSH connections and port forwarding](https://docs.vast.ai/guides/instances/connect/ssh)
- [Vast.ai billing FAQ](https://docs.vast.ai/guides/reference/faq/billing)
- [Vast.ai security FAQ](https://docs.vast.ai/guides/reference/faq/security)
- [Vast.ai: Ollama and Open WebUI](https://docs.vast.ai/ollama-webui)
- [Vast.ai Serverless](https://docs.vast.ai/guides/serverless)
- [Ollama Docker documentation](https://docs.ollama.com/docker)
- [Ollama API documentation](https://docs.ollama.com/api/introduction)
- [Ollama Qwen3.8 model tags](https://ollama.com/library/qwen3.8/tags)

## Table of contents

- [1. What Vast.ai provides](#1-what-vastai-provides)
- [2. Choosing a deployment mode and trust level](#2-choosing-a-deployment-mode-and-trust-level)
- [3. Billing and storage](#3-billing-and-storage)
- [4. Account, CLI, and SSH setup](#4-account-cli-and-ssh-setup)
- [5. Templates, offers, and instances](#5-templates-offers-and-instances)
- [6. Console quickstart](#6-console-quickstart)
- [7. Tested example: Qwen3.8-27B with Ollama](#7-tested-example-qwen38-27b-with-ollama)
- [8. Using Vast.ai's Ollama and Open WebUI template](#8-using-vastais-ollama-and-open-webui-template)
- [9. When to use vLLM](#9-when-to-use-vllm)
- [10. Vast.ai Serverless](#10-vastai-serverless)
- [11. Cleanup and troubleshooting](#11-cleanup-and-troubleshooting)

## 1. What Vast.ai provides

Vast.ai is a marketplace where independent hosts and datacenters offer GPU capacity. Unlike a conventional cloud with a fixed instance catalogue, availability, pricing, network quality, storage cost, and maximum rental duration vary by offer.

The core objects are:

- **Template:** a reusable launch configuration containing a Docker image, runtime type, ports, environment variables, disk recommendation, and startup commands.
- **Offer:** a specific rentable slice of a host machine, including GPU type and count, VRAM, price, network characteristics, reliability, location, and maximum duration.
- **Instance:** a rental created from an offer and either a template or explicit Docker settings.
- **Serverless endpoint:** an autoscaled entry point backed by one or more workergroups and temporary worker instances.

Most workloads run inside Linux containers. The host supplies the GPU driver and NVIDIA container runtime; the chosen image supplies Ollama, vLLM, PyTorch, or another application stack.

![Vast.ai Search](./assets/vastai_search.png)

![Vast.ai Templates](./assets/vastai_templates.png)

## 2. Choosing a deployment mode and trust level

### On-demand instance or Serverless?

| Mode | Best for | Main trade-off |
|---|---|---|
| On-demand instance | Experiments, notebooks, SSH access, long interactive sessions, fixed private services | You manage startup, health, security, and cleanup |
| Interruptible instance | Checkpointed batch jobs and disposable experiments | The host can interrupt the workload |
| Reserved instance | Predictable longer-running workloads | Requires prepayment/commitment and does not guarantee a stopped GPU remains available |
| Vast.ai Serverless | Bursty inference, autoscaling APIs, and variable demand | More moving parts, cold starts, benchmarking, and serverless-compatible templates |

The companion notebook uses an **on-demand instance** because it is the shortest reliable path for a private Ollama server.

### Machine trust levels

Vast.ai distinguishes three broad machine tiers:

- **Unverified:** not yet validated by Vast.ai and normally filtered out by default.
- **Verified:** passed Vast.ai's internal tests. This is useful for reliability but is not equivalent to a certified datacenter.
- **Secure Cloud / Datacenter:** verified machines hosted in datacenters meeting Vast.ai's stated certification criteria. Prefer this tier for production or sensitive data.

Containers isolate renters from one another, but the underlying provider technically controls the host. For sensitive workloads, use Secure Cloud, encrypt data before upload, avoid storing long-lived credentials on the instance, and use external secret management where practical. See the [Vast.ai security FAQ](https://docs.vast.ai/guides/reference/faq/security).

## 3. Billing and storage

Vast.ai bills separate components:

- Active GPU rental
- Allocated storage
- Upload and download bandwidth

Important consequences:

- GPU billing begins when the instance becomes active/running; Vast.ai does not charge active GPU rental while the instance is still shown as **Loading**.
- Storage is billed while the instance and its allocated container storage exist, including when the instance is stopped. Storage charges can therefore continue after GPU charges stop.
- Bandwidth is charged according to the selected host's rates.
- Destroying an instance deletes its container storage. A stopped instance preserves it and continues incurring storage charges.
- Persistent Vast volumes survive instance deletion, remain tied to their physical host, and have their own storage charges.
- Billing is per actual usage duration rather than rounded to a full hour.

Before renting, inspect the price breakdown for compute, storage, and bandwidth. Enable balance notifications or automatic billing only after choosing limits appropriate to your expected daily or weekly spend.

## 4. Account, CLI, and SSH setup

### Install and authenticate the CLI

Install the current CLI from PyPI:

```bash
python -m pip install --upgrade vastai
vastai --version
```

Create an API key in the Vast.ai account settings and configure the CLI:

```bash
vastai set api-key YOUR_VAST_API_KEY
vastai show user
```

`vastai set api-key` stores the key in the user's configuration directory. For automation, use the `VAST_API_KEY` environment variable or a secret manager. Never commit the key to source control or print it in notebook output. Prefer a separately scoped key when automation does not need full account permissions.

### Register an SSH key

Vast.ai SSH instances use public-key authentication rather than passwords.

Create a dedicated key if needed:

```bash
ssh-keygen -t ed25519 -C "vastai" -f ~/.ssh/id_vastai_ed25519
chmod 600 ~/.ssh/id_vastai_ed25519
```

Register the public half before creating an instance:

```bash
vastai create ssh-key ~/.ssh/id_vastai_ed25519.pub
```

Account-level keys are injected into subsequently created instances. To add a key to an existing container instance, use the console's SSH-key action or:

```bash
vastai attach ssh INSTANCE_ID ~/.ssh/id_vastai_ed25519.pub
```

Retrieve the current connection address instead of assuming port 22 is public:

```bash
vastai ssh-url INSTANCE_ID
```

Vast.ai can provide either a direct SSH endpoint or a proxy endpoint. Direct SSH is normally faster; the proxy path works for hosts that cannot accept direct inbound connections.

## 5. Templates, offers, and instances

### Search filters

The CLI accepts a query expression and can emit JSON with `--raw`:

```bash
vastai search offers \
  'gpu_name=RTX_3090 num_gpus=2 gpu_ram>=24 disk_space>=80 reliability>=0.98 verified=true rentable=true' \
  --order dph_total \
  --raw
```

Useful fields include:

- `gpu_name`, `num_gpus`, `gpu_ram`, and `gpu_total_ram`
- `disk_space`
- `reliability`, `verified`, and `datacenter`
- `geolocation`
- `direct_port_count` and `static_ip`
- `cuda_vers` and `compute_cap`
- `rentable` and `duration`

In the `vastai` CLI query language, `gpu_ram` and `gpu_total_ram` are expressed in GB. The REST API schema reports comparable memory values in MB, so do not copy numeric filters between interfaces without checking their units.

Offers are ephemeral: another renter may take an offer between search and creation. Production automation should handle an unavailable offer by searching again.

### Runtime selection matters

When creating a custom-image instance, choose the runtime explicitly:

- `--ssh --direct`: inject SSH support and request direct connectivity.
- `--jupyter --direct`: launch the Jupyter runtime and also provide its configured connection services.
- `--args ...`: pass arguments to the image entrypoint. Everything following `--args` is consumed by the container entrypoint, so it must appear last.
- `--onstart-cmd`: startup script for SSH/Jupyter runtime instances.

If a later step expects SSH but the instance was created without `--ssh` or `--jupyter`, `vastai ssh-url` and SSH tunnelling will not work. This was the principal failure in the original Qwen notebook.

## 6. Console quickstart

For a template-driven deployment:

1. Open the [Vast.ai console](https://cloud.vast.ai/).
2. Choose a maintained template for the workload.
3. Set enough disk for the Docker image, model weights, caches, and temporary files. Container disk size is fixed at creation.
4. Filter offers by GPU memory, reliability, location, duration, and trust tier.
5. Review compute, storage, and bandwidth pricing before clicking **Rent**.
6. Wait for **Loading** to become **Running** or **Connectable**.
7. Use the instance's **Open** or connection actions to access the portal, Jupyter, SSH, application UI, and logs exposed by the template.
8. Copy important data elsewhere and destroy the instance when finished.

![Vast.ai Instances](./assets/vastai_instances.png)

![Vast.ai Open Instance](./assets/vastai_open_instance.png)

### HTTPS certificates in the instance portal

Some template services use Vast.ai's HTTPS portal and a locally trusted Vast.ai certificate. A browser may warn until its certificate chain is trusted. Only install a root certificate obtained from an authenticated/official Vast.ai source and understand that trusting a root certificate grants it broad authority on that machine.

For a disposable command-line test, certificate verification can technically be disabled with `curl -k` or `httpx.Client(verify=False)`, but that also disables server identity verification and should not be the normal production configuration. SSH tunnelling avoids this issue for services deliberately kept on remote localhost, as in the companion notebook.

## 7. Tested example: Qwen3.8-27B with Ollama

Open [`lab/vastai.ipynb`](./lab/vastai.ipynb) for the complete executable workflow.

### What it deploys

- Docker image: `ollama/ollama:latest`
- Model: `qwen3.8:27b-q4_K_M`
- Published Ollama artifact: approximately 18 GB, 27.3B parameters, Q4_K_M, 256K native context
- Tested hardware: 2×RTX 3090 with 24 GB VRAM each
- Container disk: 80 GB
- Access: SSH tunnel only; no public Ollama API port

The model's artifact size is not its full runtime memory requirement. KV cache, context length, multimodal components, CUDA state, and Ollama overhead also consume memory. In the verified notebook run, Ollama spread the loaded model across both RTX 3090 GPUs and reported about 35.9 GB of VRAM in use at a 262,144-token context.

### Architecture

```text
Local OpenAI/Ollama client
  -> 127.0.0.1:<random local port>
  -> encrypted SSH tunnel
  -> remote 127.0.0.1:11434
  -> Ollama
  -> Qwen3.8-27B on two GPUs
```

The instance is created with an SSH runtime and no `-p 11434:11434` mapping:

```bash
vastai create instance OFFER_ID \
  --image ollama/ollama:latest \
  --disk 80 \
  --label ollama-qwen3.8-27b \
  --ssh \
  --direct \
  --onstart-cmd 'mkdir -p /workspace/ollama-models; OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=/workspace/ollama-models nohup ollama serve >/tmp/ollama-serve.log 2>&1 &'
```

After resolving the host and SSH port with `vastai ssh-url`, the notebook opens the equivalent of:

```bash
ssh -i ~/.ssh/id_vastai_ed25519 \
  -N \
  -L 127.0.0.1:LOCAL_PORT:127.0.0.1:11434 \
  -p SSH_PORT \
  root@SSH_HOST
```

It then pulls the model through Ollama's native streaming API:

```http
POST /api/pull
Content-Type: application/json

{"model": "qwen3.8:27b-q4_K_M", "stream": true}
```

Using the HTTP API for the pull exposes progress and streamed errors directly in the notebook. It is easier to diagnose than hiding `ollama pull` output in a remote startup log.

### Calling the model

Ollama implements an OpenAI-compatible chat-completions endpoint:

```python
from openai import OpenAI

client = OpenAI(
    base_url=f"http://127.0.0.1:{LOCAL_PORT}/v1/",
    api_key="ollama",  # required by the SDK but ignored by local Ollama
)

response = client.chat.completions.create(
    model="qwen3.8:27b-q4_K_M",
    messages=[{"role": "user", "content": "Write a Python function that merges overlapping intervals."}],
    reasoning_effort="none",
)

print(response.choices[0].message.content)
```

Omit `max_tokens` when no explicit application-level output cap is wanted. Generation still stops at an end-of-sequence condition or a runtime/context limit.

### Measuring tokens per second

The OpenAI-compatible response can provide an end-to-end approximation:

```python
tok_s = response.usage.completion_tokens / elapsed_seconds
```

This includes model loading, prompt evaluation, tunnel/network overhead, and generation. For generation-only throughput, use Ollama's native non-streaming `/api/chat` response:

```python
generation_tok_s = metrics["eval_count"] / (metrics["eval_duration"] / 1e9)
```

Ollama reports durations in nanoseconds. Run a warm request after the first model load when comparing GPU offers. The notebook prints both measures, prompt speed, load time, and total request time.

### Security boundary

Ollama's local API does not authenticate callers. The string `api_key="ollama"` is only a placeholder for the OpenAI SDK and adds no security.

The notebook is private by construction:

- Ollama binds to `127.0.0.1:11434` inside the container.
- Container port 11434 is not published.
- The SSH tunnel requires the registered private key.
- The local end of the tunnel also binds to `127.0.0.1`, so other computers cannot connect to it.

Knowing the instance IP and SSH port is insufficient to call the model. An attacker would need the SSH private key, access to the local computer while the tunnel is open, a vulnerability in the SSH/container stack, or control of the underlying host.

Do not add `-p 11434:11434`, set `OLLAMA_HOST=0.0.0.0`, or bind the local tunnel to `0.0.0.0` unless a real authentication proxy and appropriate firewall restrictions are added.

## 8. Using Vast.ai's Ollama and Open WebUI template

Vast.ai also provides a maintained **Ollama + Open WebUI** path for users who want a browser chat interface rather than a minimal private API.

The documented template flow is:

1. Select the Ollama/Open WebUI template.
2. Allocate enough disk and total GPU memory for the chosen Ollama tag.
3. Rent an offer and open the instance portal.
4. Create the Open WebUI administrator account when prompted.
5. Pull a model from **Admin Panel → Settings → Models**.
6. Use the WebUI or the API endpoint exposed by the portal.

This security model differs from the companion notebook. The Vast.ai template can expose Ollama through the instance portal and requires the portal's `OPEN_BUTTON_TOKEN` in the `Authorization` header. Ollama itself still does not validate that token; the portal/proxy does. Follow the current [Vast.ai Ollama template documentation](https://docs.vast.ai/ollama-webui) because template ports and image versions can change.

## 9. When to use vLLM

Choose **Ollama** when the priority is straightforward model management, local experimentation, a chat UI, or a small number of concurrent users.

Choose **vLLM** when the priority is higher concurrency, continuous batching, production throughput, tensor parallelism, or detailed serving controls. Vast.ai offers vLLM templates for both ordinary instances and Serverless.

For an ordinary instance, prefer the maintained Vast.ai template and its authenticated instance-portal route. If launching `vllm/vllm-openai` directly:

- Match the image's CUDA requirements to the host driver.
- Use `--tensor-parallel-size` when intentionally spanning multiple GPUs.
- Match `--quantization` to the checkpoint format rather than guessing from the repository name.
- Treat Hugging Face tokens as secrets.
- Do not publish an unauthenticated `-p 8000:8000` endpoint to the Internet. Use vLLM's `--api-key`, an authenticated reverse proxy, a firewall/IP allowlist, or an SSH tunnel.

Consult the current [Vast.ai instance-creation documentation](https://docs.vast.ai/cli/reference/create-instance) and [vLLM documentation](https://docs.vllm.ai/) before pinning an image tag or launch flags.

## 10. Vast.ai Serverless

Vast.ai Serverless is intended for variable or bursty workloads where workers should scale according to measured demand. It is not used by the companion Ollama notebook.

The current architecture consists of:

- **Endpoint:** the named API entry point and scaling configuration.
- **Workergroup:** a serverless-compatible template, offer-search criteria, launch overrides, and hardware requirements.
- **Worker:** a recruited GPU instance running the workload and Vast.ai's PyWorker integration.

Vast.ai also documents a higher-level **Deployments** interface that packages Python code and manages endpoint/workergroup infrastructure. Use the [current Serverless quickstart](https://docs.vast.ai/guides/serverless/quickstart) rather than copying old endpoint defaults: minimum workers, maximum workers, cold capacity, and queue settings have operational and cost consequences and can evolve.

For a vLLM Serverless endpoint, Vast.ai provides an OpenAI-compatible proxy:

```python
from openai import OpenAI

client = OpenAI(
    api_key=VAST_API_KEY,
    base_url="https://openai.vast.ai/ENDPOINT_NAME",
)

response = client.chat.completions.create(
    model="",  # required by the SDK; endpoint MODEL_NAME selects the model
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=256,
)
```

The proxy currently supports text `/v1/chat/completions` and `/v1/completions`, including streaming. The endpoint's `MODEL_NAME` selects the actual model, so the request's `model` value is ignored. Review the [OpenAI-compatible proxy limitations](https://docs.vast.ai/guides/serverless/openai-compatible-api) before relying on vision, audio, embeddings, moderation, or parallel tool calls.

Do not assume that an ordinary Ollama model tag can be dropped into a vLLM Serverless workergroup. Ollama tags package GGUF artifacts for Ollama, while vLLM templates expect supported Hugging Face checkpoints and model architectures.

## 11. Cleanup and troubleshooting

### Cleanup

List and destroy ordinary instances:

```bash
vastai show instances
vastai destroy instance INSTANCE_ID
```

Stopping an instance releases GPU compute but preserves its container storage and storage billing. Destroy the instance when the data is no longer needed, and separately delete any persistent volumes or serverless resources that should stop accruing charges.

The companion notebook contains an emergency cleanup function and a final cell that closes the local SSH tunnel before destroying the instance.

### Common failures

**The instance remains in Loading**

- Large Docker images and slow host networking can take several minutes.
- Inspect `status_msg` with `vastai show instance INSTANCE_ID --raw`.
- Vast.ai says active GPU rental is not charged during Loading, but allocated storage may still accrue.
- If startup is abnormally slow, destroy it and choose another offer.

**The instance is Running but SSH fails**

- Confirm it was launched with `--ssh` or a Jupyter runtime.
- Run `vastai ssh-url INSTANCE_ID` instead of assuming the host or port.
- Confirm the public key was registered before instance creation.
- Use the exact private key and set its permissions to `600`.
- Try the proxy SSH endpoint if direct connectivity is unavailable.

**Ollama is unreachable through the tunnel**

- Confirm the tunnel process is still running.
- Confirm both tunnel endpoints use `127.0.0.1` and the remote target is port 11434.
- Inspect `/tmp/ollama-serve.log` over SSH.
- Check the process with `ps aux | grep '[o]llama serve'`.
- Check the local endpoint with `curl http://127.0.0.1:LOCAL_PORT/api/tags`.

**The model pull fails or appears stuck**

- Verify the exact model tag and case against the [Ollama model library](https://ollama.com/library/qwen3.8/tags).
- Check free disk space with `df -h` and model storage with `du -sh /workspace/ollama-models`.
- Stream `/api/pull` responses and check for an `error` object; errors can arrive after the HTTP response has already started.
- Remember that the model artifact size is smaller than its possible runtime VRAM requirement.

**The model loads but inference runs on CPU**

- Use `ollama ps` or `GET /api/ps` to inspect loaded model placement and VRAM usage.
- Inspect Ollama startup logs for GPU discovery.
- Verify the host driver supports the CUDA runtime bundled with the current Ollama image.

**A command exposes a secret in notebook output**

- Rotate the affected API key immediately.
- Clear the output before committing.
- Pass secrets through environment variables or subprocess environments, not echoed command arguments.
