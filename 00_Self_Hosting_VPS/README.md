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


