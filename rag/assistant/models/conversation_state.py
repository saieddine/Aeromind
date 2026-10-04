import copy
import json


class ConversationState:
    """
    Stores the current state of an AeroMind conversation.
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
            "last_answer_summary": "",
        }

    def get_state(self):
        return copy.deepcopy(self.state)

    def update_state(self, updates):
        if not isinstance(updates, dict):
            return

        for key, value in updates.items():
            if key not in self.state:
                continue

            if isinstance(self.state[key], list):
                if isinstance(value, list):
                    for item in value:
                        if item not in self.state[key]:
                            self.state[key].append(item)
            else:
                self.state[key] = value

    def reset(self):
        self.__init__()

    def print_state(self):
        print("\n" + "=" * 60)
        print("Conversation State")
        print("=" * 60)
        print(json.dumps(self.state, indent=4))
        print("=" * 60)
