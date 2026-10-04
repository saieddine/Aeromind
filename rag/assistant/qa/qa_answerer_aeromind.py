"""AeroMind QA answer generation.

Builds technical-document context and conversation context, passes them
to the AeroMind prompt builder, and sends the resulting prompt to the LLM.

The prompt builder remains a separate dependency and will be adapted after
the original NPU teacher_prompt.py is inspected.
"""

from ..prompts.teacher_prompt import TeacherPrompt


class QAAnswerer:
    """
    Generates aircraft QA responses for Question & Answer Mode.
    """

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def answer(
        self,
        question,
        retrieved_chunks,
        aircraft_id,
        document_id,
        conversation_history=None,
    ):

        if retrieved_chunks:
            context_parts = []

            for i, chunk in enumerate(retrieved_chunks, start=1):
                context_parts.append(
                    f"""
TECHNICAL MATERIAL {i}

Concept:
{chunk.get("concept")}

Page:
{chunk.get("page")}

Content:
{chunk.get("text")}
"""
                )

            technical_material = "\n".join(context_parts)

        else:
            technical_material = "No relevant technical material was retrieved."

        if conversation_history:
            history_parts = []

            recent_history = conversation_history[-8:]

            for message in recent_history:
                role = message.get("role")
                content = message.get("content")

                if not content:
                    continue

                if role == "student":
                    speaker = "USER"
                elif role == "assistant":
                    speaker = "ASSISTANT"
                else:
                    speaker = role.upper()

                history_parts.append(f"{speaker}:\n{content}")

            conversation_context = (
                "\n\n".join(history_parts)
                if history_parts
                else "No previous conversation."
            )

        else:
            conversation_context = "No previous conversation."

        prompt = TeacherPrompt.build(
            question=question,
            aircraft_id=aircraft_id,
            document_id=document_id,
            conversation_context=conversation_context,
            technical_material=technical_material,
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
        )

        return completion.choices[0].message.content.strip()