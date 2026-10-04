"""AeroMind QA orchestration.

Coordinates question embedding, aircraft-document retrieval, answer
generation, and QA conversation state.

The engine does not generate the LLM answer itself; that responsibility
remains with the QA answerer.
"""

from .qa_state import QAState


class QAEngine:
    """
    Controller for Question & Answer Mode.

    Responsibilities:
    - Start and manage a QA session.
    - Generate the question embedding.
    - Attempt aircraft-document retrieval.
    - Pass available material and conversation history
      to the QA answerer.
    - Update QA conversation state.

    Important:
    Retrieval is a supporting source, not a requirement for
    answering a question.

    If retrieval returns no relevant material, the QA Answerer
    still receives the question and may answer using general
    knowledge.

    It does NOT:
    - Generate LLM responses itself.
    - Decide the content of the AeroMind's answer.
    - Manage Lecture Mode.
    - Store long-term learning progress.
    """

    def __init__(
        self,
        qa_retriever,
        qa_answerer,
        embedder,
        collection,
        top_k=5,
    ):
        self.qa_retriever = qa_retriever
        self.qa_answerer = qa_answerer
        self.embedder = embedder
        self.collection = collection
        self.top_k = top_k

        self.state = QAState()

    def start_session(
        self,
        aircraft_id,
        document_id,
        selected_section=None,
    ):
        """Start a new QA session."""
        self.state.start_session(
            aircraft_id=aircraft_id,
            document_id=document_id,
            selected_section=selected_section,
        )

    def ask(self, question):
        """
        Process one user question.

        Retrieval is best-effort:
        - relevant material found -> use it
        - no relevant material -> continue normally
        - retrieval failure -> continue with no retrieved material

        The answerer remains responsible for deciding how to use
        aircraft-document material, general knowledge, and conversation history.
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if self.state.aircraft_id is None:
            raise RuntimeError("QA session has not been started.")

        question = question.strip()

        conversation_history = self.state.get_history()
        question_embedding = self.embedder(question)

        retrieved_chunks = []

        try:
            retrieved_chunks = self.qa_retriever(
                collection=self.collection,
                query=question,
                question_embedding=question_embedding,
                aircraft_id=self.state.aircraft_id,
                document_id=self.state.document_id,
                top_k=self.top_k,
            )

            if retrieved_chunks is None:
                retrieved_chunks = []

        except Exception:
            # Retrieval failure must not prevent the AeroMind
            # from answering. Logging can be added later.
            retrieved_chunks = []

        answer = self.qa_answerer.answer(
            question=question,
            retrieved_chunks=retrieved_chunks,
            aircraft_id=self.state.aircraft_id,
            document_id=self.state.document_id,
            conversation_history=conversation_history,
        )

        self.state.add_question(question)
        self.state.add_answer(answer)

        return answer

    def clear_session(self):
        """Clear the current QA conversation."""
        self.state.clear()

    def get_state(self):
        """Return a serializable snapshot of the current QA state."""
        return self.state.get_state()