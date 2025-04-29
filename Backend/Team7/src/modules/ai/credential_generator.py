import csv
import os
import random
import re
import time
from typing import List, Tuple, clear_overloads
import warnings

import ollama

from .credential_mdp import CredentialMDP


class Credential_Generator:
    """
    In charge of generating usernames and passwords using AI-based learning models.

    Attributes:
        No public attributes.

    Methods:
        calculate_password_strength(self, password: str) -> float:

        calculate_username_strenth(self, username: str) -> float:

        _get_ai_hyperparameters(self) -> list[str]:

        get_ai_wordlist(self) -> list[str]:

        process_ai_wordlist(self, credentials_list: list[str]) -> None:

    Notes:
        This class doesn't inherit from any superclass.
    """

    def __init__(
        self,
        csv_path: str | None = None,
        wordlist_path: str | None = None,
        min_username_length: int = 8,
        username_caps: bool = True,
        username_numbers: bool = True,
        username_special_chars: bool = False,
        min_password_length: int = 12,
        password_caps: bool = True,
        password_numbers: bool = True,
        password_special_chars: bool = True,
    ):
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

        except FileNotFoundError as e:
            print(f"Error loading input files in Credential_Generator: {e}")
            self.web_text = csv_path if csv_path else ""
            self.wordlists = wordlist_path if wordlist_path else []

        self.username_mdp = CredentialMDP(order=2)
        self.password_mdp = CredentialMDP(order=3)
        self.min_username_length = (
            min_username_length if min_username_length is not None else 8
        )
        self.username_cap = username_caps if username_caps is not None else True
        self.username_numbers = (
            username_numbers if username_numbers is not None else True
        )
        self.username_special_chars = (
            username_special_chars if username_special_chars is not None else False
        )
        self.min_password_length = (
            min_password_length if min_password_length is not None else 12
        )
        self.password_cap = password_caps if password_caps is not None else True
        self.password_special_chars = (
            password_special_chars if password_special_chars is not None else True
        )
        self.password_numbers = (
            password_numbers if password_numbers is not None else True
        )

    def calculate_password_strength(self, password: str) -> str:
        """
        Calculates the strength of a given password and evaluates it using MDP evaluator.

        Args:
            password (str): The password to evaluate. Must not be empty.

        Returns:
            str: Evaluation response from MDP Evaluator.

        Raises:
            ValueError: If the password is empty.
        """
        if not password:
            raise ValueError("Password cannot be empty")

        # Basic strength score to replace embeddings.
        score = self.password_mdp.calculate_password_strength(password)

        if score > 0.7:
            return "secure - meets best practices"
        else:
            return "not secure - does not meet all best practices."

    def _suggest_password(self, password: str, score: float) -> str:
        """
        Uses Ollama to suggest a more secure version of a given password,
        while maintaining some resemblance to the original.

        Args:
            password (str): The password to evaluate and improve.
            score (float): The security score of the original password.

        Returns:
            str: A new, AI-suggested secure password based on the original.
        """
        improved_password = ""
        
        # Get configuration options
        include_numbers = self.password_numbers
        include_special_chars = self.password_special_chars
        include_capitalization = self.password_cap
        password_length = self.min_password_length
        
        # Build configuration string
        config_str = (
            f"Length: {password_length}+ characters. "
            f"Include numbers: {include_numbers}. "
            f"Include special characters: {include_special_chars}. "
            f"Include capitalization: {include_capitalization}."
        )
        
        system_message = (
            "You are a password generator that creates secure but memorable passwords. "
            "You follow the user's specific configuration requirements for length, numbers, "
            "special characters, and capitalization. Your suggestions should balance security "
            "and usability."
        )

        query = (
            f"Original password: '{password}'\n\n"
            f"Configuration: {config_str}\n\n"
            f"Please generate an improved, secure version of this password while:\n"
            f"1. Making it more secure but still somewhat memorable\n"
            f"2. Following the configuration requirements exactly\n"
            f"3. Using a mix of character types as specified\n"
            f"4. Avoiding common password patterns\n\n"
            f"Special character options (if requested): !@#$%^&*()_-+=\n\n"
            f"Return ONLY the new password with no explanation."
        )

        message = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]

        try:
            response = ollama.chat(model="gemma3:latest", messages=message)
            improved_password = response["message"]["content"].strip().replace("\n", "")
            
            # Basic validation to ensure requirements are met
            if len(improved_password) < password_length:
                improved_password += str(random.randint(100, 999))
                
            if include_numbers and not any(char.isdigit() for char in improved_password):
                improved_password += str(random.randint(10, 99))
                
            if include_special_chars and not any(char in "!@#$%^&*()_-+=" for char in improved_password):
                improved_password += random.choice("!@#$%^&*()_-+=")
                
            if include_capitalization and not any(char.isupper() for char in improved_password):
                # Capitalize a random character
                char_positions = [i for i, char in enumerate(improved_password) if char.isalpha()]
                if char_positions:
                    pos = random.choice(char_positions)
                    improved_password = improved_password[:pos] + improved_password[pos].upper() + improved_password[pos+1:]
        except Exception as e:
            warnings.warn(
                f"Error calling Ollama for password improvement: {e}\nUsing fallback method."
            )
            improved_password = self._improve_password(password)

        return improved_password

    def calculate_username_strength(self, username: str) -> float:
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

    def _suggest_username(self, username: str, score: float) -> str:
        """
        Uses Ollama to suggest a more secure and unique version of a given username,
        while maintaining its original concept.

        Args:
            username (str): The username to evaluate and improve.
            score (float): The similarity or quality score of the original username.

        Returns:
            str: A new, AI-suggested secure username based on the original.
        """
        improved_username = ""
        
        # Get configuration options
        include_numbers = self.username_numbers
        include_special_chars = self.username_special_chars
        include_capitalization = self.username_cap
        username_length = self.min_username_length
        
        # Build configuration string
        config_str = (
            f"Length must be {username_length}. "
            f"Include numbers: {include_numbers}. "
            f"DON'T Include special characters. "
            f"Include capitalization: {include_capitalization}."
        )
        
        system_message = (
            "You are a username generator that creates simple, readable, and memorable usernames. "
            "You follow the user's specific configuration requirements for length, numbers, and special characters. "
            "Your suggestions should be practical for online platforms."
        )

        query = (
            f"Original username: '{username}'\n\n"
            f"Configuration: {config_str}\n\n"
            f"Please generate an improved version of this username while:\n"
            f"1. Keeping it readable and memorable\n"
            f"2. Preserving some aspect of the original username\n"
            f"3. Following the configuration requirements exactly\n"
            f"4. Making it unique but not overly complex\n\n"
            f"Return ONLY the new username with no explanation."
        )

        message = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]

        try:
            response = ollama.chat(model="gemma3:latest", messages=message)
            improved_username = response["message"]["content"].strip().replace("\n", "")
            
            # Basic validation to ensure requirements are met
            if len(improved_username) < username_length:
                improved_username += str(random.randint(10, 99))
                
            if include_numbers and not any(char.isdigit() for char in improved_username):
                improved_username += str(random.randint(1, 99))
                
            if include_capitalization and improved_username.islower():
                # Capitalize a random character
                pos = random.randint(0, len(improved_username) - 1)
                improved_username = improved_username[:pos] + improved_username[pos].upper() + improved_username[pos+1:]
        except Exception as e:
            warnings.warn(
                f"Error calling Ollama for username improvement: {e}\nUsing fallback method."
            )
            improved_username = self._improve_username(username)

        return improved_username

    def get_ai_wordlist(self) -> List[str] | str:
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
            username_score = self.calculate_username_strength(username)
            password_response = self.calculate_password_strength(password)
            is_secure = "secure" in password_response.lower()

            processed_credentials.append(
                {
                    "username": username,
                    "username_score": username_score,
                    "password": password,
                    "is_secure": is_secure,
                    "password_evaluation": password_response,
                }
            )

        with open(
            "processed_credentials.csv", "w", newline="", encoding="utf-8"
        ) as outfile:
            fieldnames = [
                "username",
                "username_score",
                "password",
                "is_secure",
                "password_evaluation",
            ]
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
        words = re.findall(r"\w+", text.lower())
        return [
            word for word in words if len(word) >= 4
        ]  # Filter out words shorter than 4 chars

    def _build_state_transitions(self):
        """
        Build state transitions for username and password generation.
        """
        username_date = set(self._preprocess_text(self.web_text) + self.wordlists)
        password_data = set(word for word in username_date if len(word) >= 8)

        for word in username_date:
            for i in range(len(word) - self.username_mdp.order):
                state = f"username_{word[i : i + self.username_mdp.order]}"
                action = word[i + self.username_mdp.order]
                next_char = word[i + self.username_mdp.order]
                self.username_mdp.state_transitions[state][action].add(next_char)
                if i == 0:
                    self.username_mdp.initial_states.append(state)

        for word in password_data:
            for i in range(len(word) - self.password_mdp.order):
                state = f"password_{word[i : i + self.password_mdp.order]}"
                action = word[i + self.password_mdp.order]
                next_char = word[i + self.password_mdp.order]
                self.password_mdp.state_transitions[state][action].add(next_char)
                if i == 0:
                    self.password_mdp.initial_states.append(state)

    def generate_credential(self) -> Tuple[str, str]:
        """
        Generate a username and password pair.

        Returns:
            tuple[str, str]: Generated username and password.
        """
        # -- Generate username --
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
            next_state = f"username_{username[-self.username_mdp.order :]}"
            reward = self.username_mdp.get_reward(state, action, next_char)
            self.username_mdp.update_q_value(
                state, action, next_char, next_state, reward
            )
            state = next_state

        username_score = self.calculate_username_strength(username)
        username = self._suggest_username(username, username_score)
        # if self._get_username_status(username) != 0b111:
        #     username = self._improve_username(username)
        self.username_mdp.used_usernames.add(username)

        # -- Generate password --
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
            next_state = f"password_{password[-self.password_mdp.order :]}"
            reward = self.password_mdp.get_reward(state, action, next_char)
            self.password_mdp.update_q_value(
                state, action, next_char, next_state, reward
            )
            state = next_state

        password_score = self.password_mdp.calculate_password_strength(password)
        password = self._suggest_password(password, password_score)
        if self._get_password_status(password) != 0b111:
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

    def _get_password_status(self, password: str) -> int:
        """
        Evaluates a password and returns a status code as a binary flag integer.

        This function checks if the password meets various strength criteria and
        represents the results as a binary flag where:
        - 0b0001 (1): Contains special characters
        - 0b0010 (2): Contains capital letters
        - 0b0100 (4): Meets minimum length requirement
        - 0b1000 (8): Contains a numerical character

        The flags are combined using bitwise OR operations, so a fully compliant
        password would return 0b111 (7).

        Args:
            password (str): The password string to evaluate

        Returns:
            int: Binary flag integer representing which criteria are met
                 - 0 if no criteria are met
                 - 1-15 depending on which combination of criteria are met

        Example:
            >>> get_password_status("a")
            0
            >>> get_password_status("Password1234")
            6  # Meets length and capitalization requirements (4+2)
            >>> get_password_status("Password!")
            15  # Meets all requirements (8+4+2+1)
        """
        status = 0b0000  # Default to not having anything set
        if re.search(r"[0-9]", password) or not self.password_numbers:
            status |= 0b1000
        if len(password) >= self.min_password_length:
            status |= 0b0100
        if re.search(r"[A-Z]", password) or not self.password_cap:
            status |= 0b0010
        if (
            re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password)
            or not self.password_special_chars
        ):
            status |= 0b0001
        return status

    def _update_capitalization(self, password: str) -> str:
        """
        Randomly capitalizes one lowercase letter in the password or adds a capital letter if none present.

        This function identifies all lowercase letters in the given password,
        randomly selects one, and converts it to uppercase. If the password
        contains no lowercase letters, it adds a capital letter 'A' to the end
        of the password.

        Args:
            password (str): The password string to modify

        Returns:
            str: A new password string with either one randomly capitalized letter,
                 or the original password with an added capital letter if no lowercase
                 letters were present

        Examples:
            >>> _update_capitalization("hello123")
            "hEllo123"  # The 'e' was randomly selected to be capitalized

            >>> _update_capitalization("12345")
            "12345A"    # No lowercase letters to capitalize, so 'A' was added
        """

        lowercase_indices = [
            i for i, char in enumerate(password) if re.match(r"[a-z]", char)
        ]
        if lowercase_indices:
            random_capitalize = random.choice(lowercase_indices)
            char = password[random_capitalize]
            password = (
                password[:random_capitalize]
                + char.upper()
                + password[random_capitalize + 1 :]
            )
        else:
            password += "A"
        return password

    def _add_length(self, password: str) -> str:
        """
        Extends a password to meet the minimum required length.

        This function calculates how many additional characters are needed
        to reach the minimum password length, then generates a random string
        of that length using a diverse character set (including lowercase letters,
        numbers, and special characters) and appends it to the original password.

        Args:
            password (str): The original password to extend

        Returns:
            str: The extended password that meets the minimum length requirement

        Note:
            The function uses `self.min_password_length` to determine the
            required minimum length.

        Example:
            If min_password_length is 8:
            >>> _add_length("abc")
            "abc1x!p4"  # Random 5 characters added to reach length 8
        """
        # Additional 5 characters to increase complexity of password
        length_to_add = self.min_password_length - len(password) + 5
        character_set = "abcdefghijklmnopqrstuvwxyz0123456789"
        salt = "".join(random.choice(character_set) for _ in range(length_to_add))
        password += salt
        return password

    def _add_digits(self, password: str) -> str:
        """
        Adds prefix or suffix to password

        Args:
            password (str): The original password missing digits

        Returns:
            str: The extended password that meets the requirement
        """
        numbers = "0123456789"
        digits = ""
        for _ in range(3):
            digits += random.choice(numbers)
        return password + digits

    def _improve_password(self, password: str) -> str:
        """
        Enhance the generated password with additional complexity, depending on the
        parameters set by:
        - self.min_password_length
        - self.password_cap
        - self. password_special_chars

        Args:
            password (str): The password to enhance.

        Returns:
            str: Enhanced password.
        """
        required_flags = 0b0100  # Length is always required
        if self.password_cap:
            required_flags |= 0b0010
        if self.password_special_chars:
            required_flags |= 0b0001
        if self.password_numbers:
            required_flags |= 0b1000
        password_status = self._get_password_status(password)
        missing_flags = required_flags & ~password_status

        special_chars = "!@#$%^&*()_+-=[]{}|;:,./<>"
        enhanced = password

        if (missing_flags & 0b0100) == 0b0100:  # Missing Length
            enhanced = self._add_length(enhanced)
        if (missing_flags & 0b0010) == 0b0010:  # Missing capitalization
            for _ in range(3):
                enhanced = self._update_capitalization(enhanced)
        if (missing_flags & 0b0001) == 0b0001:
            for _ in range(3):  # Add 3 random special chars
                enhanced += random.choice(special_chars)
        if (missing_flags & 0b1000) == 0b1000:  # Missing numbers
            enhanced = self._add_digits(password)

        return enhanced

    def _improve_username(self, username: str) -> str:
        """
        Enhance the generated username with additional complexity, depending on the
        parameters set by:
        - self.min_username_length
        - self.username_cap
        - self.username_special_chars
        - self.username_numbers

        Args:
            username (str): The username to enhance.

        Returns:
            str: Enhanced username.
        """
        required_flags = 0b0100  # Length is always required
        if self.username_cap:
            required_flags |= 0b0010
        if self.username_special_chars:
            required_flags |= 0b0001
        if self.username_numbers:
            required_flags |= 0b1000
        username_status = self._get_username_status(username)
        missing_flags = required_flags & ~username_status
        special_chars = "!@#$%^&*()_+-=[]{}|;:,./<>"
        enhanced = username
        if (missing_flags & 0b0100) == 0b0100:
            enhanced = self._add_length(enhanced)
        if (missing_flags & 0b0010) == 0b0010:
            enhanced = self._update_capitalization(enhanced)
        if (missing_flags & 0b0001) == 0b0001:
            for _ in range(3):  # Add 3 random special chars
                enhanced += random.choice(special_chars)
        if (missing_flags & 0b1000) == 0b1000:
            enhanced = self._add_digits(enhanced)
        return enhanced

    def _get_username_status(self, username: str) -> int:
        """
        Evaluates a username and returns a status code as a binary flag integer.

        Flags:
        - 0b0001 (1): Meets minimum length
        - 0b0010 (2): Has capitalization
        - 0b0100 (4): Contains special character
        - 0b1000 (8): Contains numerical character

        Returns:
         int: A combined status flag from 0 to 7
        """
        status = 0b0000

        if len(username) >= self.min_username_length:
            status |= 0b0001
        if re.search(r"[A-Z]", username) or not self.username_cap:
            status |= 0b0010
        if (
            re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', username)
            or not self.username_special_chars
        ):
            status |= 0b0100
        if re.search(r"[0-9]", username) or not self.username_numbers:
            status |= 0b1000

        return status

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
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        try:
            with open(csv_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if not {"id", "content", "url"}.issubset(set(reader.fieldnames or [])):
                    raise ValueError("CSV must contain columns: id, content, url")
                contents = []
                for row in reader:
                    if row["content"]:
                        contents.append(row["content"].lower())
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
            raise FileNotFoundError(f"Wordlist file not found: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                words = [line.strip().lower() for line in file if line.strip()]
                return words
        except Exception as e:
            raise ValueError(f"Error reading wordlist file: {e}")


if __name__ == "__main__":
    cdg = Credential_Generator()
    password = "frick"
    score = cdg.password_mdp.calculate_password_strength(password)
    cdg._suggest_password(password, score)
