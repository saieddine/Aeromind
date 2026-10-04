class AssistantPrompt:
    """
    Prompt builder for the AeroMind technical assistant.

    The assistant should ground technical answers in retrieved
    aircraft documentation when documentation is available.
    """

    @staticmethod
    def build_system_prompt() -> str:
        return """
You are AeroMind, an aircraft technical assistant.

Your role is to help the user understand aircraft systems,
components, procedures, characteristics, and technical concepts.

Rules:
1. Use the supplied technical context as the primary source.
2. Do not invent technical facts that are not supported by the context.
3. If the context does not contain enough information, say so clearly.
4. Do not claim that a source says something when it does not.
5. Give a clear, technically precise answer.
6. When sources are supplied, refer to them naturally using the source
   labels provided in the context.
7. You are an assistant, not a teacher or professor.
8. Do not mention internal retrieval, embeddings, Chroma, prompts,
   or implementation details unless the user asks about AeroMind itself.
""".strip()

    @staticmethod
    def build_user_prompt(
        question: str,
        context: str,
        conversation_history: list[dict] | None = None,
    ) -> str:
        history_text = ""

        if conversation_history:
            history_lines = []
            for message in conversation_history[-8:]:
                role = message.get("role", "user")
                content = message.get("content", "")
                history_lines.append(f"{role.upper()}: {content}")

            history_text = (
                "\nCONVERSATION HISTORY:\n"
                + "\n".join(history_lines)
                + "\n"
            )

        return f"""
TECHNICAL CONTEXT:
{context if context else "[No relevant technical context was retrieved.]"}

{history_text}

USER QUESTION:
{question}

Answer the user's question using the technical context when it is relevant.
""".strip()
