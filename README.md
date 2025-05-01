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

### Neo4j Configuration

1. Install and start Neo4j locally
2. Modify the `.env` file inside `Backend/Team3/Database` with your Neo4j credentials
3. Configure Neo4j to allow connections from any IP on the intranet
4. Ensure your firewall permits these connections

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
