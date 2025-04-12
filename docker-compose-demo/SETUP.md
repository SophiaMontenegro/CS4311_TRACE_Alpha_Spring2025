#  Docker DVWA + Apache + NGINX Testing Stack

This repo sets up a local Docker-based testing environment using:
- [DVWA] (Damn Vulnerable Web App)
- Apache
- MySQL 5.7
- NGINX (as reverse proxy)


---

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- If using Windows, make sure WSL option is enabled for Docker
- Terminal or PowerShell access

---

## How to Run

### 1. Clone or download this repo and navigate to testing folder.

```bash
git clone https://github.com/SophiaMontenegro/TRACE_Team_1_3_7.git
cd docker-dvwa-stack
```

### 2. Start Docker

### 3. Pull Image

```bash
docker pull --platform linux/amd64 vulnerables/web-dvwa
```

### 4. Launch the Stack

```bash
docker-compose up -d
```
This sets up the containers, mounts volumes, and starts services.

### 5. Verify services are accessible

You can do this by opening a web browser and searching for
- DVWA http://localhost:8080
- Apache http://localhost:8081
- NGINX Reverse Proxy http://localhost/
- Apache through NGINX http://localhost/apache

Note: DVWA default login is :
- User: admin
- Password: password

#### The environment is running and ready for testing.

## Want to drop your own files?

### You may place index.html and other html into apache2/ OR html/ and see them served.

### 6. Managing the environment
To stop, 
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
Restart one service:
```bash
docker-compose restart dvwa
```

## Final Notes
This was tested on Windows 10 with WSL2/Hyper-V Enabled for Docker, and on Silicon MacOS(M1,M2,M3)

- You can try dropping an ```index.html``` in ```apache2/``` -> that will show on http://localhost:8081
- You can also try the same in the ```html/``` folder

- Use ```init.sql``` to pre-load data into MySQL for SQL testing.




