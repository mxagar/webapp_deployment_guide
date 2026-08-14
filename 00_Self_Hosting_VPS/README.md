# Self-Hosting Guide

These are my notes after following the Udemy course [Self-Hosting with Docker & Linux: Run Your Own Services](https://www.udemy.com/course/self-hosting-docker-linux/), by Jason Canon.

Therefore, the credits go for the course author, Jason Canon.

Table of Contents:

- [Self-Hosting Guide](#self-hosting-guide)
  - [1. Introduction](#1-introduction)
  - [2. Fundamentals](#2-fundamentals)
    - [Why Self-Host?](#why-self-host)
    - [Virtual Private Servers (VPS)](#virtual-private-servers-vps)
  - [3. Linux Fundamentals](#3-linux-fundamentals)
    - [Choosing a Linux Distribution](#choosing-a-linux-distribution)
  - [4. Ubuntu Installation and Setup](#4-ubuntu-installation-and-setup)
    - [How to SSH to the Linux Docker](#how-to-ssh-to-the-linux-docker)
  - [5. Secure Networking with Tailscale](#5-secure-networking-with-tailscale)
    - [Using Tailscale for Secure Networking](#using-tailscale-for-secure-networking)
    - [Installing Tailscale on the Server / Docker Host](#installing-tailscale-on-the-server--docker-host)
    - [Installing Tailscale on the Local Client](#installing-tailscale-on-the-local-client)
      - [MacOS](#macos)
      - [iOS](#ios)
      - [Linux](#linux)
  - [6. Docker and Portainer Setup](#6-docker-and-portainer-setup)
  - [7. Secure Web Service Access with TDSProxy and Tailscale](#7-secure-web-service-access-with-tdsproxy-and-tailscale)
  - [8. Building a Centralized Dashboard](#8-building-a-centralized-dashboard)
  - [9. Publishing Services on Your Own Domain](#9-publishing-services-on-your-own-domain)
  - [10. Discovering \& Deploying Additional Self-Hosted Services and Applications](#10-discovering--deploying-additional-self-hosted-services-and-applications)


## 1. Introduction

Course material: [`lab/self-hosted-course/`](./lab/self-hosted-course/).

## 2. Fundamentals

### Why Self-Host?

- Self-hosting means running services, applications, or websites that you control.
  - Self-hosted tools can be reached from phones, laptops, desktops, and other allowed devices.
  - Access can stay private on a home network, be exposed remotely to selected users, or be made public.
  - You choose the balance between accessibility, privacy, and security.
- Self-hosting differs from traditional installed applications by making services network-accessible.
  - A locally installed application usually runs only on the device where it is installed.
  - A self-hosted application can be used from the hosting network and any other network you allow.
  - You decide who can connect and from where.
- Self-hosting is an alternative to third-party cloud, web application, and software as a service (SaaS) platforms.
  - The main difference is who controls the infrastructure and data.
  - You control how data is stored, accessed, backed up, and used by services.
  - You also accept responsibility for managing that data and those services.
- Many popular SaaS categories have self-hosted alternatives.
  - Cloud storage services:
    - Google Drive, Dropbox, Microsoft OneDrive, and Apple iCloud can be replaced by **Nextcloud**, **Seafile**, or **Syncthing**.
    - These tools store, sync, and share files across devices while keeping the data under your control.
  - Project management, task tracking, and to-do tools:
    - Trello, Asana, and Monday.com can be replaced by **Kanboard**, **Wekan**, or **OpenProject**.
    - These tools support organizing tasks, managing lists, and collaborating on projects.
  - Chat and messaging platforms:
    - Slack, Microsoft Teams, and Discord can be replaced by **Mattermost**, **Rocket.Chat**, or **Zulip**.
    - These tools support team communication without relying on a hosted messaging provider.
  - Photo and video organization:
    - Google Photos, Amazon Photos, and Flickr can be replaced by **Immich** or **PhotoPrism**.
    - These tools help organize and share personal media while keeping ownership of the library.
  - Media servers:
    - **Jellyfin** or **Plex** can replace some subscription-based media streaming workflows.

### Virtual Private Servers (VPS)

- A virtual private server (VPS) is a virtualized server that runs in a hosting provider's data center.
  - It lets you run self-hosted applications without owning or maintaining physical hardware.
  - It still gives you control over the operating system, configuration, and installed software.
  - It provides many benefits of self-hosting while shifting hardware maintenance to the provider.
- A VPS can be easier to operate than a physical home server.
- A VPS introduces a provider trust tradeoff.
- A VPS can still offer more control than third-party SaaS applications.
- Common VPS providers include:
  - DigitalOcean.
  - Vultr.
  - AWS Lightsail.
  - OVHcloud.
  - Hetzner.
- VPS pricing and provider choice depend on current plans and requirements.
  - At the time of the recording, DigitalOcean offered plans starting at about $4 per month.
  - Different providers offer different prices, regions, performance levels, and support options.
  - A quick provider comparison helps match the VPS plan to the applications you want to host.

## 3. Linux Fundamentals

### Choosing a Linux Distribution

- Linux has many distributions because it is open source.
- Docker support is a key self-hosting criterion.
  - Docker is one of the most common ways to package and run self-hosted software.
  - Choosing a Docker-supported distribution reduces installation and troubleshooting friction.
  - Current Docker Engine documentation lists installation support for CentOS, Debian, Fedora, Raspberry Pi OS, Red Hat Enterprise Linux (RHEL), Ubuntu, and generic binaries.
  - Docker may still run on related or derivative distributions, especially Ubuntu-based systems.
  - Unsupported distributions can work, but troubleshooting help may be thinner when problems appear.
- Ubuntu is a strong default choice for self-hosting.
  - It balances stability, ease of use, and broad community support.
  - Many self-hosting guides, tutorials, and Docker resources assume Ubuntu.
  - Ubuntu is widely used for personal systems and business-critical services.
  - Canonical, the company behind Ubuntu, offers commercial support for organizations that need it.
- Ubuntu Long Term Support (LTS) releases are better suited to self-hosting than short-lived releases.
  - LTS releases arrive every two years and receive five years of standard security and maintenance updates.
  - Ubuntu 24.04 LTS was released in April 2024.
  - Ubuntu version numbers use the release year and month, so `24.04` means April 2024.
  - Ubuntu also publishes non-LTS releases every six months, but those are supported for a much shorter period.
  - Non-LTS releases are useful for testing newer features, but LTS releases are better for stable, low-maintenance servers.
- We can install Linux/Ubuntu
  - on bare-metal hardware, such as a home server or desktop computer (most performant), or
  - on a virtual machine (VM) running on a host operating system, or
  - on a VPS provided by a hosting company.

## 4. Ubuntu Installation and Setup

Covered installations:

- WSL-Ubuntu on Windows 11.
- Ubuntu on VM hosted on MacOS.
- Ubuntu on bare-metal hardware.

### How to SSH to the Linux Docker

- Secure Shell (SSH) is the normal way to manage a Linux VPS or remote Linux machine.
  - Use SSH from your local terminal instead of typing commands into a hosting console or virtual machine (VM) console.
  - SSH gives you a proper shell with copy and paste, terminal history, local customization, and easier command editing.
  - The basic connection format is `ssh <username>@<server-ip-or-hostname>`.
- `openssh-server` is only needed on the machine you are connecting to.
  - Most VPS images already have SSH installed, enabled, and reachable because providers need a way for you to log in.
  - Ubuntu Server can install OpenSSH during setup, but it may be absent if that option was not selected.
  - Ubuntu Desktop, local machines, and some custom/minimal images may not include the SSH server by default.
  - The local machine you connect from only needs an SSH client, which is already available on macOS, Linux, and modern Windows.
- Check whether the SSH server is installed and running on the target machine.

```bash
systemctl status ssh
```

- Install and start OpenSSH server only when the target machine does not already provide SSH.

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

- Allow SSH through the operating system firewall when UFW is enabled.
  - UFW (Uncomplicated Firewall) blocks incoming connections unless a rule allows them.
  - Allow SSH before enabling UFW or before ending your current remote session.
  - `OpenSSH` is a named UFW application profile for port `22/tcp`.

```bash
sudo ufw allow OpenSSH
sudo ufw status
```

- Enable UFW only after the SSH rule is present.

```bash
sudo ufw enable
sudo ufw status verbose
```

- Check provider-level firewall rules for a VPS.
  - Cloud providers may have firewalls, security groups, or network access rules outside the Linux operating system.
  - Allow inbound TCP traffic on port `22` to the VPS.
  - Restrict SSH access to your own IP address when the provider firewall supports it.
- Find the target machine's IP address.
  - For a VPS, use the public IPv4 or IPv6 address from the provider dashboard.
  - For a local machine, run `ip addr` and use the `inet` address on the active network interface.
  - Do not use `127.0.0.1`; that address points back to the current machine.

```bash
# Show network interfaces and IP addresses on the target machine.
ip addr
```

- Connect from your local terminal.
  - Replace `root` with the username configured by your VPS provider or Linux installer.
  - Replace `203.0.113.10` with the server's public IP address or hostname.
  - SSH authentication usually uses either a password or an SSH private key, not a separate login token.
  - Many VPS providers inject your public SSH key into the server when it is created.
- Create an SSH key pair on your local machine when you do not already have one.
  - `id_ed25519` is the private key file.
  - `id_ed25519.pub` is the matching public key file.
  - Create `id_ed25519` on the local machine you will connect from.
  - Upload or copy only `id_ed25519.pub` to the server.
  - Keep `id_ed25519` secret and never upload the private key.
  - Ed25519 is a modern SSH key type with strong security and small key files.
  - Generating the key on the server and downloading the private key is possible, but it is the wrong habit for normal SSH access because it moves the secret key across machines.

```bash
# Create a new Ed25519 SSH key pair in the default SSH folder (local machine).
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -C "your_email@example.com"

# Print the public key so you can add it to your VPS provider or server.
cat ~/.ssh/id_ed25519.pub
```

- Add the public key to the server before using key-based login.
  - During VPS creation, paste `id_ed25519.pub` into the provider's SSH key field when available.
  - For an existing server with password login, copy the public key into the remote user's `authorized_keys` file.

```bash
# Copy your public key to an existing server where password login still works.
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@203.0.113.10
```

```bash
# Password-based login prompts for the user's password.
ssh root@203.0.113.10

# Key-based login uses your private key file.
ssh -i ~/.ssh/id_ed25519 root@203.0.113.10
```

- Complete the first SSH login.
  - Type `yes` when SSH asks whether to continue connecting to the new host.
  - Enter the Linux user's password when prompted, unless the server uses SSH keys.
  - Future connections to the same host normally skip the first-time host confirmation.
  - SSH does not take the password in the command; it prompts for it interactively.
- Prefer SSH keys for regular server administration.
  - Password login is convenient for first access, but SSH keys are safer for ongoing use.
  - After key-based login works, consider disabling password login in the SSH server configuration.

## 5. Secure Networking with Tailscale

### Using Tailscale for Secure Networking

Additional sources:

- [How Tailscale works](https://tailscale.com/blog/how-tailscale-works)
- [Tailscale Free Plan](https://tailscale.com/blog/free-plan)

- Tailscale creates a private network for your authenticated devices.
  - Devices in the same Tailscale network can communicate even when they are on different physical networks.
  - A Tailscale network is called a `tailnet`.
  - Each device receives a stable private Tailscale IP address.
  - Common devices include laptops, phones, home servers, VPSs, and cloud instances.
- Tailscale is useful for self-hosting because it avoids public exposure.
  - You can reach file servers, remote desktops, web applications, and other services without opening them to the public internet.
  - You usually do not need public IP addresses, dynamic Domain Name System (DNS), router port forwarding, or complex firewall rules.
  - Services stay inaccessible to devices outside your tailnet.
  - This reduces brute-force risk and keeps the public attack surface smaller.
- Tailscale behaves differently from a traditional hub-and-spoke VPN.
  - A traditional Virtual Private Network (VPN) often routes traffic through a central VPN server.
  - Tailscale creates a peer-to-peer mesh VPN where devices connect directly whenever possible.
  - Direct connections reduce latency and avoid a central routing bottleneck.
  - If one device or path is unavailable, other devices can still communicate when a viable route exists.
- Tailscale encrypts device traffic with WireGuard.
  - WireGuard provides encrypted tunnels between devices.
  - Captured traffic appears as encrypted data rather than readable content.
  - Tailscale coordinates device identity and connectivity, but it does not receive decrypted peer traffic.
- Tailscale handles difficult network conditions automatically.
  - Most home and office networks use Network Address Translation (NAT), which makes direct inbound connections difficult.
  - Tailscale uses NAT traversal to help devices connect across different routers and networks.
  - When a direct path cannot be established, Tailscale can relay encrypted traffic through DERP (Designated Encrypted Relay for Packets).
  - DERP keeps connectivity working, but relayed traffic may have more latency than a direct peer-to-peer path.
- Tailscale is easier to operate than many traditional VPN setups.
  - Installation and login are usually enough to add a device to the tailnet.
  - Devices discover each other automatically after authentication.
  - The web admin console lets you view devices, check status, rename or tag devices, and revoke access.
- Tailscale works across common platforms.
  - Supported device types include Linux, Windows, macOS, iOS, Android, and cloud servers.
  - This makes it practical to connect home devices, mobile devices, VPSs, and office systems into one private network.
- Exit nodes let one device route internet traffic for another device.
  - An exit node makes selected client traffic leave through a trusted device in your tailnet.
  - This can help on public Wi-Fi because traffic can route through a network you trust.
  - It can also make your connection appear to originate from the exit node's location.
  - A home server can act as an exit node when you want remote traffic to leave through your home network.
- Tailscale's pricing model separates personal use from business use.
  - The transcript describes a generous free tier for personal, individual, and non-business self-hosting.
  - Personal self-hosters usually get the core features needed to connect their own devices.
  - Business plans add features such as external user sharing, richer administrative controls, auditing, detailed logs, and larger account management.
  - Current limits and plan details should be checked on Tailscale's pricing page before relying on exact numbers.
- Tailscale can offer a free tier partly because most traffic does not need to cross Tailscale-operated VPN servers.
  - Direct peer-to-peer traffic keeps central infrastructure costs lower.
  - DERP relays are used as a fallback for connectivity, not as the default path for all traffic.

### Installing Tailscale on the Server / Docker Host

- Install Tailscale on the Ubuntu Docker host so it can join your private tailnet.
  - Log in to the Linux server, virtual machine (VM), bare-metal host, or Windows Subsystem for Linux (WSL) Ubuntu environment that will run Docker.
  - Use the current account password when `sudo` prompts for authentication.
  - Tailscale lets this host expose self-hosted services privately to other devices in the same tailnet.
- Update the operating system before installing Tailscale.
  - `apt update` refreshes package metadata.
  - `apt upgrade` installs available updates for packages already on the system.

```bash
sudo apt update
sudo apt upgrade -y
```

- Create or sign in to a Tailscale account before joining the host.
  - Tailscale commonly supports identity providers such as Google, Microsoft, GitHub, and Apple.
  - Personal self-hosting should use the personal/non-business path when Tailscale asks for account type.
  - The site layout may change, so follow the current onboarding flow rather than relying on exact button names.
- Install Tailscale with the official Linux install script.
  - The script configures the Tailscale package repository for the distribution and installs the Tailscale client.
  - Linux commands are case-sensitive, and spaces matter.
  - Type or paste the command exactly when working from a remote console.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

- Authenticate the server into your tailnet.
  - `tailscale up` starts the client and prints a login URL when browser authentication is required.
  - Open the URL in a browser where you can sign in to Tailscale.
  - Confirm the connection to add the Linux host as a device in the tailnet.

```bash
sudo tailscale up
```

- Verify the device in the Tailscale admin console.
  - Tailscale lists connected devices as machines.
  - The Docker host should appear as a newly connected Linux machine.
  - Rename or tag it if that helps you recognize it later.
- Decide whether to disable key expiry for the Docker host.
  - Tailscale devices periodically require re-authentication by default.
  - If a server key expires, the host can temporarily lose tailnet connectivity until it is re-authenticated.
  - For trusted always-on servers, disabling key expiry can prevent avoidable outages.
  - Disabling key expiry reduces one layer of automatic credential rotation, so reserve it for devices you trust and maintain.
- Add at least one client device next.
  - A second device is required to test private access to the Docker host over Tailscale.
  - Install Tailscale on your laptop, desktop, phone, or tablet and sign in to the same tailnet.
  - After both devices are connected, you can access self-hosted services through Tailscale-only private networking.


### Installing Tailscale on the Local Client

#### MacOS

[Download Tailscale for macOS](https://tailscale.com/download/mac)

- Install Tailscale on macOS so the Mac can join the same tailnet as the Docker host.
  - Download the macOS installer from Tailscale's download page.
  - Open the downloaded package from the browser or the `Downloads` folder.
  - Accept the default installer steps and enter the macOS administrator password when prompted.
  - Close the installer when installation finishes, then optionally move the installer package to the trash.
- Start Tailscale from the Applications folder.
  - Open Finder.
  - Go to `Applications`.
  - Launch `Tailscale`.
- Allow the macOS networking permissions Tailscale needs.
  - Tailscale may ask to install or enable a system extension or NetworkExtension.
  - Open System Settings when prompted.
  - Enable Tailscale and approve the VPN configuration.
  - These permissions let Tailscale create the local encrypted network tunnel.
- Sign in with the same Tailscale account used for the server.
  - Use the same identity provider, such as Google, Microsoft, GitHub, or Apple.
  - Confirm the connection when Tailscale asks to add the Mac to the tailnet.
  - Enable start-on-login when prompted if this Mac should stay available on the tailnet after reboots.
- Verify the Mac in the Tailscale dashboard.
  - The newly connected Mac should appear in the machine list.
  - Rename or tag the device if that helps identify it later.
  - Device keys expire periodically by default, so trusted long-lived devices may need key expiry adjusted in the admin console.
- Use the Mac as a Tailscale client for private service access.
  - After the Mac and Docker host are in the same tailnet, they can communicate over Tailscale private networking.
  - Self-hosted services can stay off the public internet while remaining reachable from the Mac.

#### iOS

[Download Tailscale for iOS](https://tailscale.com/download/ios)

- Install Tailscale on iOS so an iPhone or iPad can join the same tailnet as the Docker host.
  - Open the Tailscale iOS download page or search for Tailscale in the App Store.
  - Install the Tailscale app with the App Store `Get`, download, or install button.
  - Open the app after installation finishes.
- Complete the first-run prompts.
  - Tap `Get Started`.
  - Allow notifications when prompted so Tailscale can warn about reauthentication or key-expiry events.
  - Allow Tailscale to install its VPN configuration.
  - Enter the device passcode or approve the system prompt if iOS requests confirmation.
- Sign in with the same Tailscale account used for the server.
  - Use the same identity provider, such as Google, Microsoft, GitHub, or Apple.
  - Confirm the connection when Tailscale asks to add the iOS device to the tailnet.
  - After approval, the app shows the devices available in the tailnet.
- Control the iOS device's Tailscale connection from the app.
  - Disconnect temporarily with the in-app connection toggle when private networking is not needed.
  - Reconnect by opening Tailscale and turning the connection back on.
  - When connected, the iOS device can securely reach other devices and services in the same tailnet.
- Use iOS as a mobile client for self-hosted services.
  - The Docker host and iOS device must both be connected to the same tailnet.
  - Self-hosted services can remain private while still being reachable from the phone or tablet.

#### Linux

## 6. Docker and Portainer Setup

## 7. Secure Web Service Access with TDSProxy and Tailscale

## 8. Building a Centralized Dashboard

## 9. Publishing Services on Your Own Domain

## 10. Discovering & Deploying Additional Self-Hosted Services and Applications
