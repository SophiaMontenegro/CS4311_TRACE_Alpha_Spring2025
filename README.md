# TRACE - Web Analysis Toolkit

TRACE is a comprehensive web analysis toolkit designed for security analysts. It provides a suite of tools for web scraping, data analysis, credential generation, and security testing.

## Overview

TRACE automates web scraping, analyzes data, and generates username-password pairs based on statistical and learning-based models. It includes multiple tools for different aspects of web security analysis and testing.

## Installation

### Installation/Setup Video Walkthrough

For a detailed video guide on installation and setup, refer to the following link:
[Installation/Setup Video Walkthrough](https://youtu.be/u_vyRit7tGM)

### Prerequisites

- Python 3.8+
- Node.js and npm
- Neo4j database

### Dependencies

**Backend:**
```bash
# Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd Backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd Frontend
npm install
```

## 🐍 Backend Setup (Python + Requirements)

To install all required Python dependencies for the backend:

### 📦 Step 1: Navigate to the Backend directory

```bash
cd Backend
```

### 📥 Step 2: Install dependencies

Use the following command to install all required packages:

```bash
pip install -r requirements.txt
```

This ensures that all necessary modules (such as FastAPI, neo4j, etc.) are available in your Python environment.

---

### 🧠 Local Neo4j Database Configuration for TRACE

This guide walks through the steps to configure a **local Neo4j instance** for the TRACE penetration testing suite. It includes instructions for both **Lead Analysts (who host the database)** and **Client Analysts (who connect remotely)**.

---

### 📥 Step 1: Download & Install Neo4j

### For ONLY THE LEAD's Machine

Download Neo4j Desktop:
➡️ [https://neo4j.com/download/](https://neo4j.com/download/)

Follow installation steps, including:
- Setting up an account
- Copying and pasting the activation code
- Skipping updates when prompted
- Choosing a save directory

---

### 🛠️ Step 2: Configure the Database (Lead Analyst)

#### 🔧 Create a Local DBMS

1. Open Neo4j Desktop and **add a local DBMS** (not a remote connection).
2. Set an easy-to-remember password.
3. Stop and delete any temporary projects you don’t need.

#### 📝 Modify the Configuration File

1. Go to **Manage → Settings** for your database.
2. Locate and **uncomment or set** these lines:

```properties
# Listen on all interfaces
dbms.default_listen_address=0.0.0.0

# Advertise the LAN IP (replace with actual IP)
dbms.default_advertised_address=192.168.X.X
```

### 🔥 Open the Firewall Ports

If you’re on Linux:
sudo ufw allow 7687/tcp
sudo ufw allow 7474/tcp

For Windows, ensure port 7687 and 7474 are allowed through the firewall.

### 📁 Step 3: Set Up the .env File

For Lead Analyst (Host)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

For Client Analysts (Remote Users)
NEO4J_URI=bolt://<host_ip>:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

### 🧪 Final Step: Test Your Setup
	•	Start the Neo4j instance via Neo4j Desktop.
	•	Run the TRACE backend locally and ensure there’s no authentication or connection error.

If you see:
Neo.ClientError.Security.Unauthorized

→ Double-check your .env credentials and make sure the database is running.

---

## 🌐 Frontend Setup (Vite + Node.js)

This project uses **Vite** with **Node.js** for the frontend.

### 📦 Step 1: Install Node.js and npm

Download the latest **LTS version** of Node.js, which includes npm:
➡️ [https://nodejs.org/en/download](https://nodejs.org/en/download)

After installation, verify versions:
```bash
node -v
npm -v
```

### 🚀 Step 2: Install Dependencies

Navigate to the frontend directory:
```bash
cd Frontend
npm install
```

This installs all required packages listed in `package.json`.

### ▶️ Step 3: Run the Frontend

```bash
npm run dev
```

This starts the Vite development server. You should see output showing the local server URL, e.g.:

```
  VITE vX.X.X  ready in Y ms

  ➜  Local:   http://localhost:5173/
```

Visit the provided URL in your browser to view the TRACE UI.

---
## Getting Started

### Starting the Application

1. **Start the Frontend:**
   ```bash
   cd Frontend
   npm run dev
   ```

2. **Start the Backend:**
   ```bash
   # In a separate terminal with virtual environment activated
   cd Backend
   python main.py
   ```

3. **Register and login** to the application

### Project Management

1. Create a new project as a lead analyst
2. Add team members by editing the project and adding their initials
3. Other analysts can then connect to the project once added

## Tools

### Crawler
Scans websites by following HTML links to map site structure and discover pages.

### Web Tree
Visualizes website structure from crawler results. Nodes are color-coded based on:
- Response codes
- Path sensitivity
- Potential security issues

### Intruder
Tests form vulnerabilities by:
- Identifying forms on target sites
- Allowing insertion of custom payloads at specified intrusion points
- Submitting crafted POST requests

### HTTP-Tester
A request crafting tool that allows you to:
- Create custom HTTP requests
- Edit and manipulate request parameters
- Resend modified requests to analyze responses

### Directory Brute Forcer
Discovers hidden directories and pages by:
- Testing paths not linked in HTML
- Using customizable wordlists
- Identifying resources through status code responses

### Fuzzer
Tests application parameter handling by:
- Injecting unexpected data into parameters
- Using various payload types
- Identifying potential vulnerabilities

## MDP Credential Generator

The Markov Decision Process (MDP) module generates high-quality usernames and passwords.

### How it Works

1. **Input Preparation**
   - Processes site data and wordlists for training credential generation

2. **State Transition Mapping**
   - Analyzes character sequences to build transition probability maps
   - Creates state-action pairs linking potential actions to resulting states

3. **Q-Learning Optimization**
   - Calculates rewards based on username quality and password strength
   - Penalizes reused credentials while rewarding structural patterns
   - Updates Q-values iteratively to improve future credentials

4. **Credential Generation**
   - Starts with initial state derived from wordlist
   - Iteratively extends username/password based on optimized transitions
   - Ensures quality criteria are satisfied

5. **Password Enhancement**
   - Adds capitalization, special characters, and digits for strength
   - Balances memorability with security

### Running the MDP Generator

1. **Prepare Input Files:**
   - `wordlist.txt`: Contains sample words for training (user-specified via file selection)
   - `site_list.csv`: Contains discovered directories from the spider functionality

2. **Run the Generator:**
   ```bash
   python mdp3.py
   ```

3. **Output:**
   - Generated credentials are displayed in the GUI
   - Results are stored as a CSV file for future reference

   Example output:
   ```
   Username: skipe487, Password: Computerst%
   ```

## Docker Environment

For containerized deployment, refer to `SETUP.md` inside the `docker-compose-demo` folder in the repository.

## Troubleshooting

- Ensure Neo4j is running before starting the application
- Check that all team members have the same Neo4j configuration
- Verify network connectivity between all components
- Check ports, firewall rules, and ip setups on the intranet
