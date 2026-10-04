import json

from ..llm.llm_client import llm_client
from ..prompts.memory_prompt import MemoryPrompt


class MemoryUpdater:
    """
    Uses the LLM to update the user's AeroMind conversation state.

    This class does NOT modify the ConversationState directly.
    It only asks the LLM to produce a JSON update and returns
    the parsed dictionary.
    """

    def __init__(self, model_name: str):
        self.client = llm_client.client
        self.model_name = model_name

    def update(self, conversation_state, question, answer):
        """
        Ask the LLM to generate a conversation-state update.

        Parameters
        ----------
        conversation_state : dict
            Current AeroMind conversation state.
        question : str
            Latest user question.
        answer : str
            Latest assistant answer.

        Returns
        -------
        dict
            Parsed JSON update returned by the LLM.
        """

        system_prompt = MemoryPrompt.build_prompt()

        user_prompt = f"""
Current Conversation State:

{json.dumps(conversation_state, indent=4)}

------------------------------------------------------------

User Question:

{question}

------------------------------------------------------------

Assistant Answer:

{answer}

------------------------------------------------------------

Update the Conversation State.

Return ONLY valid JSON.
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()

        try:
            return json.loads(result)

        except json.JSONDecodeError:
            print("\nMemory Updater Error")
            print("----------------------")
            print("The LLM returned invalid JSON.\n")
            print(result)
            return {}
