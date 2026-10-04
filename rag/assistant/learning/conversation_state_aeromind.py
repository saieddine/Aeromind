import copy
import json


class ConversationState:
    """
    Stores the current state of an AeroMind conversation.

    This class is the ONLY owner of the conversation state.
    Other modules should not modify self.state directly.
    They should use get_state() and update_state().
    """

    def __init__(self):
        self.state = {
            "current_topics": [],
            "discussed_topics": [],
            "important_facts": [],
            "technical_examples": [],
            "comparisons": [],
            "user_preferences": [],
            "last_question": "",
            "last_answer_summary": ""
        }

    # --------------------------------------------------
    # Get Current State
    # --------------------------------------------------

    def get_state(self):
        """
        Return a safe copy of the conversation state.
        """
        return copy.deepcopy(self.state)

    # --------------------------------------------------
    # Apply Updates
    # --------------------------------------------------

    def update_state(self, updates):
        """
        Merge updates into the conversation state.

        Parameters
        ----------
        updates : dict
            JSON returned by the MemoryUpdater.
        """

        if not isinstance(updates, dict):
            return

        for key, value in updates.items():

            if key not in self.state:
                continue

            # Merge lists
            if isinstance(self.state[key], list):

                if isinstance(value, list):

                    for item in value:
                        if item not in self.state[key]:
                            self.state[key].append(item)

            # Replace scalar values
            else:
                self.state[key] = value

    # --------------------------------------------------
    # Reset
    # --------------------------------------------------

    def reset(self):
        """
        Reset the conversation state.
        """
        self.__init__()

    # --------------------------------------------------
    # Print
    # --------------------------------------------------

    def print_state(self):
        """
        Pretty-print the conversation state.
        """
        print("\n" + "=" * 60)
        print("Conversation State")
        print("=" * 60)

        print(json.dumps(self.state, indent=4))

        print("=" * 60)
