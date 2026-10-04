"""AeroMind reasoning engine.

Makes lightweight routing decisions around the aircraft Q&A workflow.
It does not execute actions itself; it returns Decision objects that
higher-level orchestration can use.

The initial implementation preserves the NPU system's simple keyword-based
reasoning behavior while removing NPU course/lecture assumptions.
"""

from .decision import Decision


class ReasoningEngine:
    """
    Central reasoning module of the AeroMind AI system.

    This class never performs actions.

    It only analyzes the current situation and returns
    Decision objects describing what should happen next.
    """

    def __init__(self):

        # Simple keywords for Version 1.
        self.follow_up_keywords = [

            "another",
            "again",
            "more",
            "continue",
            "it",
            "that",
            "this"

        ]

        self.ignore_keywords = [

            "thanks",
            "thank you",
            "bye",
            "goodbye",
            "hello",
            "hi"

        ]

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def before_retrieval(self, question, conversation_state):

        return self._reason_about_retrieval(
            question,
            conversation_state
        )

    def after_retrieval(self, retrieved_chunks):

        if len(retrieved_chunks) == 0:

            return Decision(

                action="retrieve_again",

                confidence=1.0,

                reason="No relevant chunks were retrieved."
            )

        return Decision(

            action="continue",

            confidence=0.95,

            reason="Retrieval successful."
        )

    def after_response(self, question, answer):

        return self._reason_about_response(
            question,
            answer
        )

    def should_update_memory(self, question, answer):

        return self._reason_about_memory(
            question,
            answer
        )

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _reason_about_retrieval(self, question, conversation_state):

        question_lower = question.lower().strip()

        if question_lower == "":

            return Decision(

                action="ignore",

                confidence=1.0,

                reason="Empty question."
            )

        for keyword in self.ignore_keywords:

            if keyword in question_lower:

                return Decision(

                    action="ignore",

                    confidence=1.0,

                    reason="Greeting or non-technical interaction."
                )

        for keyword in self.follow_up_keywords:

            if keyword in question_lower:

                return Decision(

                    action="expand_question",

                    confidence=0.95,

                    reason="Follow-up technical question detected.",

                    metadata={
                        "needs_conversation_state": True
                    }
                )

        return Decision(

            action="retrieve",

            confidence=0.95,

            reason="New aircraft-technical question."
        )

    def _reason_about_memory(self, question, answer):

        question_lower = question.lower()

        for keyword in self.ignore_keywords:

            if keyword in question_lower:

                return Decision(

                    action="skip_memory",

                    confidence=1.0,

                    reason="No technical information to retain."
                )

        return Decision(

            action="update_memory",

            confidence=0.95,

            reason="Technical interaction detected."
        )

    def _reason_about_response(self, question, answer):

        return Decision(

            action="verify",

            confidence=0.95,

            reason="Every technical response should be eligible for verification."
        )