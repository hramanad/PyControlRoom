# DMFR Automations: Enterprise Automation Control Room and Orchestration Suite

## 1. Executive Summary
This repository contains the source code, configuration schemas, and deployment specifications for the DMFR Automations Enterprise Automation Control Room[cite: 1]. The system provides centralized queue monitoring, multi-user role-based access control, and real-time execution log telemetry across a three-tier Windows Server topology using **Streamlit** (Control Room Interface) and **Prefect** (Workflow Orchestration Engine)[cite: 1].

---

## 2. System Architecture

The platform is segmented across three dedicated server tiers to isolate user interface operations, database persistence, and bot execution workloads[cite: 1]:

| Server Tier | Role | Core Services | Network Ports |
| :--- | :--- | :--- | :--- |
| **App Server** | Orchestrator & Control Room Hub | Streamlit Control Room, Prefect Server UI & API | TCP `8501`, TCP `4200`[cite: 1] |
| **DB Server** | Transactional Persistence Tier | Microsoft SQL Server (`DMFR_Automations`) | TCP `1433`[cite: 1] |
| **RTR / Dev Server** | Bot Execution Tier | Python Runtime, Prefect Workers, Automation Scripts | Outbound to `4200` & `1433`[cite: 1] |

### Architectural Data Flow
1. **Control Room (App Server - Port 8501):** Human operators authenticate into the Streamlit web portal from any authorized machine on the internal network to monitor work queues, inspect exceptions, and trigger manual dispatches[cite: 1].
2. **Orchestration API (App Server - Port 4200):** Prefect Server manages workflow states, scheduling, and centralized log aggregation[cite: 1].
3. **Bot Execution (RTR / Dev Server):** Automation scripts decorated with `@flow` and `@task` execute on the RTR or Dev servers, polling the SQL database (`Port 1433`) for work items and streaming real-time console logs to the App Server (`Port 4200`)[cite: 1].

---

## 3. Repository Structure

```text
DMFR-Automations/
├── .streamlit/
│   └── config.toml            # Production Streamlit server configuration
├── logs/
│   ├── service_out.log        # NSSM standard output log
│   └── service_err.log        # NSSM standard error log
├── App.py                     # Primary Streamlit Control Room application
├── config.yaml                # Encrypted user credentials and session configuration
├── PasswordHasher.py          # Utility script for generating bcrypt password hashes
├── requirements.txt           # Python package dependencies
└── README.md                  # System documentation
```

---

## 4. Prerequisites and Network Configuration

### Software Requirements
* **Operating System:** Windows Server (App, DB, and RTR environments)[cite: 1]
* **Python Runtime:** Python 3.12+ (64-bit AMD64)[cite: 1]
* **Service Manager:** NSSM (Non-Sucking Service Manager) for background Windows Service registration[cite: 1]

### Firewall Rules
Execute the following command in an elevated PowerShell prompt on the App Server to permit inbound traffic from the DB, RTR, and operator workstations[cite: 1]:

```powershell
New-NetFirewallRule -DisplayName "DMFR RPA Control Room (Streamlit & Prefect)" -Direction Inbound -LocalPort 8501, 4200 -Protocol TCP -Action Allow
```

Verify that the ports are actively listening on the host interface[cite: 1]:

```powershell
Get-NetTCPConnection -LocalPort 8501, 4200 -State Listen -ErrorAction SilentlyContinue
```

Identify the App Server hostname and IPv4 address for cross-server configuration[cite: 1]:

```powershell
Write-Host "Hostname: $(hostname)"; ipconfig | findstr /i "IPv4"
```

---

## 5. Control Room Setup (Streamlit)

### 5.1 Dependency Installation
Install the required libraries on the App Server[cite: 1]:

```powershell
python -m pip install --upgrade pip
python -m pip install streamlit streamlit-authenticator pyyaml bcrypt pandas pyodbc
```

### 5.2 Credential Hashing
User passwords are encrypted using `bcrypt` prior to storage[cite: 1]. Run `PasswordHasher.py` to generate hashes for the administrator accounts (`dev1`, `dev2`, `manager`)[cite: 1]:

```python
import streamlit_authenticator as stauth

# Plaintext passwords for your 3 users
passwords = ['Admin@1234', 'Admin@1234', 'Admin@1234']

# Newer version syntax: classmethod call
hashed_passwords = stauth.Hasher.hash_list(passwords)

print("Admin:", hashed_passwords[0])
print("Dev1:", hashed_passwords[1])
print("Manager:", hashed_passwords[2])
```

### 5.3 Authentication Configuration (`config.yaml`)
Create `config.yaml` in the root application directory[cite: 1]. Setting `expiry_days: 0` enforces transient session-only cookies, terminating the authenticated session immediately when the client browser is closed[cite: 1].

```yaml
credentials:
  usernames:
    dev1:
      email: "dev1@ttu.edu"
      name: "Developer 1"
      password: "$2b$12$REPLACE_WITH_GENERATED_HASH_1"
      roles:
        - "admin"
    dev2:
      email: "dev2@ttu.edu"
      name: "Developer 2"
      password: "$2b$12$REPLACE_WITH_GENERATED_HASH_2"
      roles:
        - "admin"
    manager:
      email: "manager@ttu.edu"
      name: "Manager"
      password: "$2b$12$REPLACE_WITH_GENERATED_HASH_3"
      roles:
        - "admin"
cookie:
  expiry_days: 0
  key: "rpa_control_room_signature_secret_key"
  name: "rpa_session_cookie"
```

### 5.4 Application Capabilities (`App.py`)
* **Concurrent Multi-User Sessions:** Isolated `st.session_state` threads allow `dev1`, `dev2`, and `manager` to log in simultaneously from separate machines without session interference[cite: 1].
* **Locked Enterprise UI:** Native Streamlit header bars, deployment buttons, and form instruction subtexts are suppressed via CSS overrides[cite: 1].
* **System Management Modal (`@st.dialog`):** Accessible via the bottom-left sidebar, providing[cite: 1]:
  * **Account Security:** Self-service password rotation with live `bcrypt` verification and automatic persistence to `config.yaml`[cite: 1].
  * **Application Operations:** Administrative session rerun (`st.rerun()`) and in-memory cache invalidation (`st.cache_data.clear()`)[cite: 1].
  * **System Diagnostics:** Runtime version and server topology metadata[cite: 1].

### 5.5 Launching the Control Room
Execute the following command in PowerShell on the App Server[cite: 1]:

```powershell
cd "C:\Users\hramanad\Documents\DMFR Automations\PY"
python -m streamlit run App.py --server.address 0.0.0.0 --server.port 8501
```

---

## 6. Orchestration Engine Setup (Prefect)

### 6.1 App Server Configuration
By default, the Prefect UI attempts to communicate with `127.0.0.1`, which fails when accessed remotely from the DB or RTR servers. Configure the App Server Prefect profile to bind to all network interfaces and route UI API requests to the App Server's actual IPv4 address:

```powershell
# 1. Bind Prefect API to all network interfaces
python -m prefect config set PREFECT_SERVER_API_HOST="0.0.0.0"

# 2. Assign the standard Prefect port
python -m prefect config set PREFECT_SERVER_API_PORT="4200"

# 3. Configure the UI to point to the App Server IPv4 address
python -m prefect config set PREFECT_UI_API_URL="http://<APP_SERVER_IPV4>:4200/api"
```

Start the Prefect Server instance on the App Server:

```powershell
python -m prefect server start --host 0.0.0.0
```

### 6.2 Remote Execution Server Configuration (RTR / Dev Server)
To enable bots running on the RTR Server or Dev Server to transmit execution states and console logs to the App Server, configure the remote Prefect profile:

```powershell
python -m prefect config set PREFECT_API_URL="http://<APP_SERVER_IPV4>:4200/api"
```
