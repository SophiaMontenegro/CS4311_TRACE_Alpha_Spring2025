# Docker DVWA + Apache + NGINX Testing Stack

This repo sets up a local Docker-based testing environment using:
- [DVWA] (Damn Vulnerable Web App)
- Apache
- MySQL 5.7
- NGINX (as reverse proxy)

---

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (for Mac/Windows)
- [Docker Engine](https://docs.docker.com/engine/install/) (for Linux)
- If using **Windows**, ensure WSL option is enabled for Docker
- Terminal or PowerShell access

---

## How to Run

### **For Mac (M1/M2/M3), Windows (WSL2)**

#### 1. Clone or download this repo and navigate to the testing folder.

```bash
git clone https://github.com/SophiaMontenegro/CS4311_TRACE_Alpha_Spring2025.git
cd docker-compose-demo
```

#### 2. Start Docker Desktop

#### 3. Pull DVWA image (amd64 platform)

```bash
docker pull --platform linux/amd64 vulnerables/web-dvwa
```

#### 4. Launch the Stack

```bash
docker-compose up -d
```

---

### **For Linux (ARM64) on Mac (e.g., Kali Linux on UTM with M1/M2)**

#### 1. Clone or download this repo and navigate to the testing folder.

```bash
git clone https://github.com/SophiaMontenegro/CS4311_TRACE_Alpha_Spring2025.git
cd docker-compose-demo
```

#### 2. Install Docker Engine (if not already installed)

Refer to Docker’s official guide:  
https://docs.docker.com/engine/install/

#### 3. Install QEMU for cross-platform emulation

```bash
docker run --rm --privileged tonistiigi/binfmt --install all
```

This allows **amd64** containers to run on your **ARM64** system.

#### 4. Test cross-architecture support

```bash
docker run --rm --platform linux/amd64 alpine uname -m
```

You should see `x86_64` confirming emulation is working.

#### 5. Launch the Stack

```bash
sudo docker-compose up -d
```

---

## 5. Verify services are accessible

Open a web browser and navigate to:

- DVWA: http://localhost:8080
- Apache: http://localhost:8081
- NGINX Reverse Proxy: http://localhost/
- Apache through NGINX: http://localhost/apache

**DVWA default login:**
- User: `admin`
- Password: `password`

---

## Want to drop your own files?

- Place `index.html` and other files in:
  - `apache2/` (served by Apache)
  - `html/` (served by NGINX)

---

## Managing the environment

To stop:

```bash
docker-compose down
```

Check logs:

```bash
docker-compose logs
docker-compose logs <service-name>
```

Check running containers:

```bash
docker ps
```

Restart a service:

```bash
docker-compose restart dvwa
```

---

## Final Notes

- Tested on:
  - **Windows 10** with **WSL2/Hyper-V**
  - **MacOS (M1/M2/M3)** with **Docker Desktop**
  - **Linux (ARM64)** (e.g., Kali Linux on UTM on M1/M2) with **Docker Engine + QEMU binfmt**

- Example:
  - Drop an `index.html` in `apache2/` → see it on http://localhost:8081
  - Drop an `index.html` in `html/` → served by NGINX

- Use `init.sql` to pre-load data into MySQL for SQL testing.