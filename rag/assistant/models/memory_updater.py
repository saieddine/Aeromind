import json

from ..llm.llm_client import llm_client
from ..prompts.memory_prompt import MemoryPrompt


class MemoryUpdater:
    """
    Uses the LLM to update AeroMind conversation state.
    """

    def update(self, conversation_state, question, answer):
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

        response = llm_client.client.chat.completions.create(
            model=llm_client.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
        )

        result = response.choices[0].message.content.strip()

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {}
