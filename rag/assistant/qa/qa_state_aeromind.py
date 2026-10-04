"""AeroMind QA session state.

Stores the active aircraft/document context and the short conversation
history needed by the QA engine. It does not retrieve documents or call
the LLM.
"""

class QAState:
    """
    Runtime state for a Question & Answer session.

    Responsibilities:
    - Store the current aircraft and document.
    - Optionally store the concept the student is focusing on.
    - Keep the QA conversation history.
    - Track the number of questions asked.

    It does NOT:
    - Retrieve aircraft-document material.
    - Generate answers.
    - Store embeddings.
    - Control lecture progression.
    - Store long-term aircraft learning progress.
    """

    def __init__(self):
        self.aircraft_id = None
        self.document_id = None
        self.selected_section = None
        self.conversation_history = []
        self.question_count = 0

    def start_session(
        self,
        aircraft_id,
        document_id=None,
        selected_section=None
    ):
        """
        Start a new QA session and clear previous conversation state.
        """
        self.aircraft_id = aircraft_id
        self.document_id = document_id
        self.selected_section = selected_section
        self.conversation_history = []
        self.question_count = 0

    def set_concept(self, concept):
        """
        Set or change the optional concept context for the session.
        """
        self.selected_section = concept

    def add_message(self, role, content):
        """
        Add one message to the QA conversation history.
        """
        if not content:
            return

        self.conversation_history.append(
            {
                "role": role,
                "content": content,
            }
        )

    def add_question(self, question):
        """
        Record a user question.
        """
        self.add_message("user", question)
        self.question_count += 1

    def add_answer(self, answer):
        """
        Record the assistant's answer.
        """
        self.add_message("assistant", answer)

    def get_history(self):
        """
        Return the full QA conversation history.
        """
        return list(self.conversation_history)

    def clear(self):
        """
        Clear the current QA conversation while keeping the
        selected aircraft and document.
        """
        self.conversation_history = []
        self.question_count = 0

    def get_state(self):
        """
        Return a serializable snapshot of the current QA state.
        """
        return {
            "aircraft_id": self.aircraft_id,
            "document_id": self.document_id,
            "selected_section": self.selected_section,
            "conversation_history": self.get_history(),
            "question_count": self.question_count,
        }
