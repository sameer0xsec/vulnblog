# VulnBlog — Vulnerable Modern Publishing & Blog Lab

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Backend-Python%20%7C%20Flask-3776AB?logo=python&logoColor=white)](https://flask.palletsprojects.com/)
[![Vue.js](https://img.shields.io/badge/Frontend-Vue%203%20%7C%20Vite-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![MySQL](https://img.shields.io/badge/Database-MySQL%208.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Apache](https://img.shields.io/badge/Reverse%20Proxy-Apache%20httpd-D22128?logo=apache&logoColor=white)](https://httpd.apache.org/)
[![Lab](https://img.shields.io/badge/Security-Lab%20Only-red.svg)](#disclaimer)

**VulnBlog** is an intentionally vulnerable full-stack publishing web application created for offensive security testing, secure development training, code review, and DevSecOps learning.

> [!CAUTION]
> **DISCLAIMER: FOR EDUCATIONAL AND LAB USE ONLY**
> This application contains intentionally severe vulnerabilities (Python Pickle Deserialization RCE, Werkzeug Debugger Console RCE, SQL Injection, SSRF, XXE, and more). **Never deploy or expose this application to the public internet or untrusted networks.** Run only within isolated local or lab environments.

---

## Architecture & Technology Stack

| Component | Technology | Container Name | Internal Port | Host Port |
| :--- | :--- | :--- | :--- | :--- |
| **Reverse Proxy** | Apache httpd 2.4 (`mod_proxy`) | `vulnblog-apache` | `80` | `8081` (Primary Entry Point) |
| **Frontend** | Vue 3, Vite, Vue Router | `vulnblog-frontend` | `5173` | `5173` |
| **Backend API** | Python 3.12, Flask, MySQL Connector | `vulnblog-backend` | `5000` | `5000` |
| **Database** | MySQL 8.0 | `vulnblog-db` | `3306` | `3306` |

```text
Browser / Attacker
       │
       ▼
 [ Apache Proxy ] (Port 8081)
       ├───► / (Frontend UI - Vue 3 / Vite :5173)
       ├───► /api/* (Flask Backend :5000)
       ├───► /uploads/* (Static Uploads via Apache)
       └───► /internal/* (Admin API Proxy)
               │
               ▼
          [ MySQL 8 ] (Port 3306)
```

---

## Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/)

### Deployment
Clone the repository and launch the container cluster:

```bash
git clone git@github.com:sameer0xsec/vulnblog.git
cd vulnblog
docker compose up -d --build
```

Access the application in your browser at:
👉 **`http://localhost:8081`**

To stop and clean up containers and volumes:
```bash
docker compose down -v
```

---

## Seeded Credentials

The database is pre-seeded with sample user accounts (passwords hashed using unsalted SHA1):

| Username | Password | Role | Purpose |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | `admin` | Administrative account |
| `alice` | `password123` | `user` | Standard blogger account |
| `bob` | `letmein` | `user` | Standard blogger account |

---

## Deliberate Vulnerabilities Overview

VulnBlog contains **26+ intentional security vulnerabilities** accompanied by inline code annotations (`# VULN:`). For step-by-step exploit guides, see [VULNERABILITIES.md](VULNERABILITIES.md).

### 1. Remote Code Execution (RCE)
- **Insecure Python Deserialization (`pickle`)**: Draft saving/loading (`/api/tools/draft`) blindly executes `pickle.loads()` on user data.
- **Flask Interactive Debugger**: Werkzeug interactive debugger enabled in development mode leaks full stack traces and provides a PIN-protected interactive Python console.
- **OS Command Injection**: PDF post export endpoint executes unvalidated shell commands via `subprocess.check_output(..., shell=True)`.

### 2. Injection Flaws
- **SQL Injection (Authentication Bypass)**: Raw string formatting on login queries (`auth.py`).
- **SQL Injection (UNION Exfiltration)**: Post search endpoint (`/api/posts/search`) leaks user credentials via UNION queries.
- **XML External Entity (XXE)**: Post XML importer processes external entities, enabling local file disclosure.

### 3. Broken Authentication & Session Management
- **Broken JWT Verification**: Accepts `alg: "none"` tokens and lacks token expiration validation.
- **Hardcoded Secret Key**: Flask session secret (`changeme`) hardcoded in source.
- **Predictable Password Reset Tokens**: 4-digit tokens returned directly in HTTP response payloads.
- **Weak Cryptographic Hashing**: Unsalted SHA-1 password hashes crackable via rainbow tables.
- **No Rate Limiting**: Unlimited credential attempts on login endpoints.

### 4. Broken Access Control & IDOR
- **Mass Assignment**: Registration endpoint permits self-assignment of `role: admin`.
- **Missing Role Validation**: Administrative user management routes accessible without `admin` privilege verification.
- **Unauthorized Resource Modification**: Unauthenticated/unauthorized post deletion endpoint.

### 5. Client-Side & File Handling Flaws
- **Stored XSS**: Post and comment contents rendered unsanitized using `v-html`.
- **Reflected XSS**: Search query reflected without HTML entity encoding.
- **Arbitrary File Upload**: Unvalidated file uploads in `/api/upload` allowing script hosting.
- **Path Traversal**: Arbitrary server file read via `/api/files?name=../../../../etc/passwd`.

### 6. Infrastructure & Reverse Proxy Misconfigurations
- **Server-Side Request Forgery (SSRF)**: Link preview generator accesses arbitrary internal microservices.
- **Apache httpd Misconfigurations**: Enabled `mod_status` server info, `TRACE` method (XST), directory listing on `/uploads`, missing HTTP security headers, and open proxying of `/internal/`.

---

## Example Attack Chain

1. **Reconnaissance & Auth Bypass**: Exploit the SQL Injection on `/api/auth/login` to authenticate directly as `admin` without knowing the password.
2. **Privilege Escalation**: Use the admin session to access draft authoring tools.
3. **Exploitation (RCE)**: Submit a crafted serialized Python `pickle` payload to the draft endpoint; triggering deserialization executes shell commands on the backend container.
4. **Alternative Vector**: Exploit SSRF on `/api/tools/link-preview` to discover internal hosts and read cloud metadata or backend network services.

---

## Practice Workflow

1. **Reconnaissance**: Inspect UI workflows and discover hidden routes with Burp Suite or `curl`.
2. **Analysis**: Match endpoints with vulnerability notes in [VULNERABILITIES.md](VULNERABILITIES.md).
3. **Exploitation**: Construct working Proof-of-Concepts (PoCs) for each vulnerability class.
4. **Remediation**: Implement defensive controls (parameterized queries, secure JSON serializers, output escaping, hardened Apache configuration).

---

## License & Legal Notice

This repository is strictly intended for educational, defensive, and authorized penetration testing training. Any unauthorized use against targets without written permission is strictly prohibited.
