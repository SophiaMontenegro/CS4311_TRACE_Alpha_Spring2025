from collections import defaultdict
import random
import re
from typing import Dict, Set, Tuple, List


class CredentialMDP:
    """
    This class is responsbile for managing the Markov Decision Process for generating credentials

    Attributes:
        * `self.order: int`
        * `self.gamma: float`
        * `self.q_values: Dict[str, Dict[Tuple[str, str], float]]`
        * `self.state_transitions: Dict[str, Dict[str, Set[str]]]`
        * `self.used_usernames: Set[str]`
        * `self.epsilon: float`
        * `self.learning_rate: float`
        * `self.initial_states: List[str]`
    """

    def __init__(
        self,
        order: int = 2,
        gamma: float = 0.9,
    ) -> None:
        self.order = order
        self.gamma = gamma
        self.q_values: Dict[str, Dict[Tuple[str, str], float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.state_transitions: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        self.used_usernames: Set[str] = set()
        self.epsilon: float = 0.1
        self.learning_rate: float = 0.1
        self.initial_states: List[str] = []

    def calculate_password_strength(self, password: str) -> float:
        """
        Calculate the strength of a password based on various criteria.

        The strength score ranges from 0.0 to 1.0, with higher scores indicating stronger passwords.
        The following criteria contribute to the password strength:
        - Length (≥ 12 characters): +0.3
        - Contains uppercase letter: +0.2
        - Contains digit: +0.2
        - Contains special character (!@#$%^&*): +0.2
        - Has at least 8 unique characters: +0.1

        Args:
            password (str): The password string to evaluate

        Returns:
            float: A score between 0.0 and 1.0 indicating password strength
        """
        score = 0.0
        if len(password) >= 12:
            score += 0.3
        if re.search(r"[A-Z]", password):
            score += 0.2
        if re.search(r"[0-9]", password):
            score += 0.2
        if re.search(r"[!@#$%^&*]", password):
            score += 0.2
        if len(set(password)) >= 8:
            score += 0.1
        return score

    def calculate_username_quality(self, username: str) -> float:
        """
        Calculate the quality score for a username based on multiple criteria.

        The quality score ranges from 0.0 to 1.0, with higher scores indicating better usernames.
        The following criteria contribute to the username quality:
        - Length (≥ 6 characters): +0.3
        - Uniqueness (not in used_usernames): +0.4
        - Starts with lowercase letter: +0.2
        - Contains no whitespace: +0.1

        Args:
            username (str): The username string to evaluate

        Returns:
            float: A score between 0.0 and 1.0 indicating username quality
        """
        score = 0.0
        if len(username) >= 6:
            score += 0.3
        if username not in self.used_usernames:
            score += 0.4
        if re.match(r"^[a-z]", username):
            score += 0.2
        if not re.search(r"\s", username):
            score += 0.1
        return score

    def get_reward(self, state: str, action: str, next_char: str) -> float:
        """
        Calculate the reward for a transition based on username or password quality.

        This method determines whether the current state relates to a username or password
        and calculates an appropriate reward by applying the corresponding quality function.
        The reward is normalized by the length of the current string to encourage efficient
        character selection.

        Args:
            state (str): The current state string, expected to contain either "username" or "password"
            action (str): The action taken in the current state (not used in calculation)
            next_char (str): The character added to the state after taking the action

        Returns:
            float: A normalized reward value based on username quality or password strength

        Notes:
            - For username states: Uses calculate_username_quality() and normalizes by length
            - For password states: Uses calculate_password_strength() and normalizes by length
            - Assumes state string format includes the type at the beginning, with the actual
              string content starting at index 9
        """

        if "username" in state:
            current = state[9:] + next_char
            return self.calculate_username_quality(current) / len(current)
        else:
            current = state[9:] + next_char
            return self.calculate_password_strength(current) / len(current)

    def update_q_value(
        self, state: str, action: str, next_char: str, next_state: str, reward: float
    ) -> None:
        """
        Update the Q-value for a state-action-result tuple using the Q-learning algorithm.

        This method implements the Q-learning update formula:
        Q(s,a,r) ← Q(s,a,r) + α * [reward + γ * max Q(s',a',r') - Q(s,a,r)]

        The function calculates the maximum Q-value for all possible actions in the next state,
        then uses this to update the Q-value of the current state-action-result combination.

        Args:
            state (str): The current state
            action (str): The action taken in the current state
            next_char (str): The result/observation after taking the action
            next_state (str): The resulting state after taking the action
            reward (float): The reward received for this transition

        Returns:
            None: The method updates the internal q_values dictionary directly

        Notes:
            - Uses the class attributes learning_rate (α) and gamma (γ) for calculations
            - If the next state has no possible actions, the max_next_q defaults to 0
        """
        next_action_values = []
        for next_action in self.get_possible_actions(next_state):
            for next_next_char in self.state_transitions[next_state][next_action]:
                next_action_values.append(
                    self.q_values[next_state][(next_action, next_next_char)]
                )

        max_next_q = max(next_action_values, default=0)
        current_q = self.q_values[state][(action, next_char)]
        new_q = current_q + self.learning_rate * (
            reward + self.gamma * max_next_q - current_q
        )
        self.q_values[state][(action, next_char)] = new_q

    def get_possible_actions(self, state: str) -> List[str]:
        return list(self.state_transitions[state].keys())

    def choose_action(self, state: str) -> Tuple[str, str]:
        """
        Select an action to take from the current state using an epsilon-greedy policy.

        This method implements exploration vs. exploitation using the epsilon-greedy approach:
        - With probability epsilon: Choose a random action (exploration)
        - With probability (1-epsilon): Choose the action with the highest Q-value (exploitation)

        For the exploitation case, the method selects the action with the highest expected
        Q-value among all possible next characters resulting from that action.

        Args:
            state (str): The current state for which to choose an action

        Returns:
            Tuple[str, str]: A tuple containing (selected_action, expected_next_character)
            If no actions are possible, returns ("", "")

        Notes:
            - Uses the class attribute epsilon to control exploration/exploitation balance
            - If the best action has multiple possible next characters, one is chosen randomly
            - Falls back to random selection if no Q-values are available for valid actions
        """
        possible_actions = self.get_possible_actions(state)
        if not possible_actions:
            return "", ""

        if random.random() < self.epsilon:
            action = random.choice(possible_actions)
            next_char = random.choice(list(self.state_transitions[state][action]))
        else:
            # Choose best action based on Q-values
            action_values = {}
            for act in possible_actions:
                if self.state_transitions[state][act]:
                    value = max([
                        self.q_values[state][(act, nxt_ch)]
                        for nxt_ch in self.state_transitions[state][act]
                    ])
                    action_values[act] = value

            if action_values:
                action = max(action_values.items(), key=lambda x: x[1])[0]
                next_char = random.choice(list(self.state_transitions[state][action]))
            else:
                action = random.choice(possible_actions)
                next_char = random.choice(list(self.state_transitions[state][action]))

        return action, next_char
