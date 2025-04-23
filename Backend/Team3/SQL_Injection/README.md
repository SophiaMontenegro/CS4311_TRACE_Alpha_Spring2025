# TRACE

TRACE is a tool that automates web scraping, analyzes data, and generates username-password pairs based on statistical and learning-based models.

## Dependencies

Install Steps:
-	Clone the repository or download the provided files.
-	Navigate to the project directory.
- Required Python libraries:
  - `beautifulsoup4`
  - `numpy`
  - `requests`
- Install dependencies by running the following command: 
```bash
pip install -r requirements.txt
```

## How To Run
1.	Prepare Input Files:
-	wordlist.txt: Contains sample words for training. *(In your implementation: this shoudl be user specified via a "select file" funcitonality that lets them point to a wordlist within the user's file structure)*
-	site_list.csv: Has an id and website. *(In your implementation: this will need to be the discovered directories via the **spider** functionality of TRACE. this should be automatically gathered but the user should be able to specify which host:port's site_list to utilize)*
2.	Run the Script:
-	Save the script and run the following command:
```bash
python mdp3.py
```


## Markov Decision Process (MDP) 
The script processes the CSV and wordlist to build state transitions and generates credentials based on MDPs, enhancing the quality of usernames and passwords. It uses reinforcement learning and Q-learning to refine credential generation based on quality and strength criteria.

### How it Works
1. Input Preparation
- The script requires a dataset (site_list.cvs) and a wordlist (wordlist.txt) for training and generating credentials.
2. State Transition
- The script analyzes sequences of characters to build state transition maps for username and passwords.
- Transitions are stored as state-action pairs, linking potential actions to their resulting states.
3. Q-Learning for Credential Optimization
- Rewards are calculated based on unsername quality and password strength
- Username Quality: Penalizes reused names, rewards structural patterns
- Password Strength: Encourages diversity, length, and use of special characters
- Q-values are updated iteratively to improve future credentials
4. Credential Generation
- Starts with an initial state derived from the wordlist
- Iteratively chooses actions to extend username/password
- Ends when length or quality criteria are satisfied
- Adds additional randomization for security
5. Password Enhancement
- Adds a capitalized character, a special character, and a random digit to strengthen password further
6. Generated Output
-	Generated Usernames and Passwords: The script generates a list of usernames and passwords based on the MDP learning process.
-	The improved credentials are printed to the console. *(In your Implementation: these will be printed within the GUI and stored as a CSV file on each generation)*
Example: 
```bash
Username: skipe487, Password: Computerst%
```
