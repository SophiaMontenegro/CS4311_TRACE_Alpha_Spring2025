import random
import os
import csv
from typing import List, Tuple
import re
# NOTE: 'genai' comes from 'google-generativeai', not 'google'
import google.generativeai as genai

from .credential_mdp import CredentialMDP

class Credential_Generator:
    """
    In charge of generating usernames and passwords using AI-based learning models.

    Attributes:
        No public attributes.

    Methods:
        calculate_password_strength(self, password: str) -> float:

        calcualte_username_strenth(self, username: str) -> float:

        get_ai_hyperparameters(self) -> list[str]:

        get_ai_wordlist(self) -> list[str]:

        process_ai_wordlist(self, credentials_list: list[str]) -> None:

    Notes:
        This class doesn't inherit from any superclass.
    """

    def __init__(self, csv_path: str = None, wordlist_path: str = None):
        """
        Initialize the Credential Generator.

        Args: 
            csv_path (str, optional): Path to CSV with web text.
            wordlist_path (str, optional): Path to wordlist file.
        """
        try:
            if csv_path and os.path.exists(csv_path):
                self.web_text = self._load_web_text(csv_path)
            else:
                self.web_text = ""

            if wordlist_path and os.path.exists(wordlist_path):
                self.wordlists = self._load_wordlist(wordlist_path)
            else:
                self.wordlists = []

        except (FileNotFoundError) as e:
            print(f"Error loading input files in Credential_Generator: {e}")
            self.web_text = csv_path if csv_path else ""
            self.wordlists = wordlist_path if wordlist_path else []
        
        self.username_mdp = CredentialMDP(order=2)
        self.password_mdp = CredentialMDP(order=3)
        self.min_username_length = 5
        self.min_password_length = 10


    def calculate_password_strength(self, password: str) -> str:
        """
        Calculates the strength of a given password and evaluates it using Ollama.

        Args:
            password (str): The password to evaluate. Must not be empty.

        Returns:
            str: Evaluation response from Ollama.

        Raises:
            ValueError: If the password is empty.
        """
        if not password:
            raise ValueError("Password cannot be empty")

        good_practices_info = (
            "Good password practices include the following: "
            "1. Length: Passwords should be at least 12 characters long. "
            "2. Complexity: Passwords should include a mix of uppercase letters, lowercase letters, numbers, and special characters. "
            "3. Unpredictability: Avoid common words, phrases, or predictable patterns like '1234' or 'qwerty'. "
            "4. Uniqueness: Passwords should be unique for every account to prevent leaks. "
            "5. Avoid personal information: Avoid using easily guessable information, such as names or birthdays. "
            "6. Use of password managers: Consider using password managers for securely storing passwords."
        )

        # Basice strength score to replace embeddings.
        score = self.password_mdp.calculate_password_strength(password)

        query = (
            f"{good_practices_info}\n\n"  
            f"Here's a password: '{password}'. "
            f"Based on best practices for creating secure passwords, and considering the cosine similarity "
            f"of '{score:.2f}' with similar insecure passwords, is this password secure? "
            f"\n\nIf the cosine similarity is high and the password follows a strong pattern, it should be considered secure. "
            f"If both the cosine similarity is high and the password has a weak pattern, it should be considered not secure. "
            f"If there is no cosine similarity, but the password has a strong pattern, it should be considered secure. "
            f"\n\nIf the password is weak according to best practices, mention that first and explain why. "
            f"Please answer with 'secure' or 'not secure', followed by a brief explanation (max 5 words) that includes: "
            f"whether best practices were followed, which practice was not followed (if applicable) and what is weak about the pattern (if the pattern is weak), and whether cosine similarity was high."
        ) 

        system_message = 'You are a password security expert. Evaluate passwords carefully and provide concise feedback.'

        message = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': query},
        ]

        try:
            client = genai.Client(api_key='') 
            gemini_resp = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=[
                   system_message + query
                    ],
            )

            return gemini_resp.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            if score > 0.7:
                return "secure - meets best practices"
            else:
                return "not secure - does not meet all best practices."


    def calcualte_username_strenth(self, username: str) -> float:
        """
        Calculate the strength of a given username.

        Args:
            username (str): The username to evaluate. Must not be empty.

        Returns:
            float: A strength score between 0.0 and 1.0.

        Raises:
            ValueError: If the username is empty.
        """
        if not username:
            raise ValueError("Username cannot be empty")
        
        return self.username_mdp.calculate_username_quality(username)

    def get_ai_hyperparameters(self) -> list[str]:
        """
        Retrieves the AI Hyperparameters for the ML model from the user.

        Args:
            None

        Returns:
            list[str]: the list of hyperparameters for the AI model.

        Raises:
            ValueError: If there are no hyperparameters.
        """
        return [
            ""
        ]

    def get_ai_wordlist(self) -> list[str]:
        """
        Provides the results of the AI results as a word list.

        Args:
            None

        Returns:
            list[str]: the wordlist that has been generated.

        Raises:
            ValueError: if there is no wordlist that has been generated.
        """
        if not self.wordlists:
            raise ValueError("No wordlist has been generated or loaded")
        return self.wordlists

    def process_ai_wordlist(self, credentials_list: list[str]) -> None:
        """
        Processes the wordlist containing usernames and passwords along with the score of their confidence.

        Args:
            credentials_list (list[tuple[str, str]]): the wordlist that needs to be processed.

        Returns:
            None

        Raises:
            ValueError: if the credentials_list is empty.
        """
        if not credentials_list:
            raise ValueError("Credential list cannot be empty")
        
        # Process and score each credential
        processed_credentials = []
        for username, password in credentials_list:
            username_score = self.calcualte_username_strenth(username)
            password_response = self.calculate_password_strength(password)
            is_secure = "secure" in password_response.lower()

            processed_credentials.append({
                "username": username,
                "username_score": username_score,
                "password": password,
                "is_secure": is_secure,
                "password_evaluation":password_response
            })

        with open("Team7/src/database/ai/processed_credentials.csv", "w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["username", "username_score", "password", "is_secure", "password_evaluation"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_credentials)

    def _preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text data for training.
        
        Args:
            text (str): The text to preprocess.
            
        Returns:
            List[str]: List of words.
        """
        words = re.findall(r'\w+', text.lower())
        return [word for word in words if len(word) >= 4]  # Filter out words shorter than 4 chars

    def _build_state_transitions(self):
        """
        Build state transitions for username and password generation.
        """
        username_date = set(self._preprocess_text(self.web_text) + self.wordlists)
        password_data = set(word for word in username_date if len(word) >= 8)

        for word in username_date:
            for i in range(len(word) - self.username_mdp.order):
                state = f"username_{word[i:i+self.username_mdp.order]}"
                action = word[i+self.username_mdp.order]
                next_char = word[i+self.username_mdp.order]
                self.username_mdp.state_transitions[state][action].add(next_char)
                if i == 0:
                    self.username_mdp.initial_states.append(state)
        
        for word in password_data:
            for i in range(len(word) - self.password_mdp.order):
                state = f"password_{word[i:i+self.password_mdp.order]}"
                action = word[i+self.password_mdp.order]
                next_char = word[i+self.password_mdp.order]
                self.password_mdp.state_transitions[state][action].add(next_char)
                if i == 0:
                    self.password_mdp.initial_states.append(state)
    
    def generate_credential(self) -> Tuple[str, str]:
        """
        Generate a username and password pair.
        
        Returns:
            tuple[str, str]: Generated username and password.
        """
        # Generate username
        if not self.username_mdp.initial_states:
            state = f"username_{random.choice(self.wordlists)[:2] if self.wordlists else 'user'}"
        else:
            state = random.choice(self.username_mdp.initial_states)

        username = state[9:]
        while len(username) < self.min_username_length:
            action, next_char = self.username_mdp.choose_action(state)
            if not action or not next_char:
                break
            username += next_char
            next_state = f"username_{username[-self.username_mdp.order:]}"
            reward = self.username_mdp.get_reward(state, action, next_char)
            self.username_mdp.update_q_value(state, action, next_char, next_state, reward)
            state = next_state

        username = f"{username}{random.randint(1, 999)}"
        self.username_mdp.used_usernames.add(username)

        # Generate password
        if not self.password_mdp.initial_states:
            state = f"password_{random.choice(self.wordlists)[:3] if self.wordlists else 'pwd'}"
        else:
            state = random.choice(self.password_mdp.initial_states)

        password = state[9:]
        while len(password) < self.min_password_length:
            action, next_char = self.password_mdp.choose_action(state)
            if not action or not next_char:
                break
            password += next_char
            next_state = f'password_{password[-self.password_mdp.order:]}'
            reward = self.password_mdp.get_reward(state, action, next_char)
            self.password_mdp.update_q_value(state, action, next_char, next_state, reward)
            state = next_state

        password = self._improve_password(password)
        return username, password
    
    def generate_credentials(self, count: int = 10) -> List[Tuple[str, str]]:
        """
        Generate multiple credentials.
        
        Args:
            count (int): Number of credentials to generate.
            
        Returns:
            list[tuple[str, str]]: List of generated username and password pairs.
        """
        self._build_state_transitions()
        credentials = []
        for _ in range(count):
            username, password = self.generate_credential()
            credentials.append((username, password))
        return credentials
    
    def _improve_password(self, password: str) -> str:
        """
        Enhance the generated password with additional complexity.

        Args:
            password (str): The password to enhance.

        Returns:
            str: Enhanced password.
        """
        enhanced = password.capitalize()
        enhanced = f'{enhanced}{random.choice("!@#$%^&*")}{random.randint(0, 9)}'
        return enhanced

    def _load_web_text(self, csv_path: str) -> str:
        """
        Load web text from a CSV file.
        
        Args:
            csv_path (str): Path to the CSV file.
            
        Returns:
            str: Concatenated content from the CSV.
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist.
            ValueError: If the CSV doesn't have the required columns.
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f'CSV file not found: {csv_path}')
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                if not {'id', 'content', 'url'}.issubset(set(reader.fieldnames or [])):
                    raise ValueError("CSV must contain columns: id, content, url")
                contents = []
                for row in reader:
                    if row['content']:
                        contents.append(row['content'].lower())
            return " ".join(contents)
        except csv.Error as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
    def _load_wordlist(self, file_path: str) -> List[str]:
        """
        Load wordlist from a file.
        
        Args:
            file_path (str): Path to the wordlist file.
            
        Returns:
            List[str]: List of words from the file.
            
        Raises:
            FileNotFoundError: If the wordlist file doesn't exist.
            ValueError: If there's an error reading the file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Wordlist file not found: {file_path}')
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                words = [line.strip().lower() for line in file if line.strip()]
                return words
        except Exception as e:
            raise ValueError(f'Error reading wordlist file: {e}')