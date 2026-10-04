"""
==============================================================
AeroMind Technical Context Builder
==============================================================

Builds a rich runtime technical context for AeroMind.

This class converts the current conversation state into natural
language that is easy for an LLM to understand.

It does NOT communicate with the LLM.
It does NOT build prompts.
It only prepares technical context.
"""


class TeachingContextBuilder:

    @staticmethod
    def build(component_context, technical_state, user_action) -> str:

        history = component_context.history

        return f"""
==================================================
LESSON STATE
==================================================

Course:
{technical_state.course}

Lesson:
{technical_state.technical session}

Current Technical Context

Title:
{component_context.title}

Section Position:
{technical_state.current_component_context_index + 1} / {technical_state.total_component_contexts}

Lesson Progress:
{technical_state.progress_percentage}%
==================================================
CURRENT STUDENT REQUEST
==================================================

{TeachingContextBuilder._action_description(user_action)}

==================================================
LEARNING HISTORY
==================================================

This component_context has already been taught.

Examples Given:
{history.examples_given}

Re-Explanations:
{history.re_explanations}

Simplifications:
{history.simplifications}

Current Detail Level:
{TeachingContextBuilder._detail_name(history.detail_level)}

==================================================
PROFESSOR OBJECTIVE
==================================================

{TeachingContextBuilder._objective(user_action)}

==================================================
GUIDANCE
==================================================

{TeachingContextBuilder._guidance(history)}

==================================================
IMPORTANT
==================================================

Remain on the current component_context.

Do not introduce a new component_context.

Do not restart the entire technical explanation.

Stop after completing the requested technical action.
"""

    # ======================================================
    # Detail Level
    # ======================================================

    @staticmethod
    def _detail_name(level: int) -> str:

        if level <= 0:
            return "Beginner"

        if level == 1:
            return "Basic"

        if level == 2:
            return "Intermediate"

        if level == 3:
            return "Advanced"

        return "Expert"

    # ======================================================
    # Student Action
    # ======================================================

    @staticmethod
    def _action_description(action) -> str:

        return action.name.replace("_", " ").title()

    # ======================================================
    # Technical Objective
    # ======================================================

    @staticmethod
    def _objective(action) -> str:

        objectives = {

            "START":
                "Introduce the current component_context and build intuition.",

            "CONTINUE":
                "Teach the next component_context supplied by the system.",

            "EXPLAIN_AGAIN":
                "Explain the same component_context using a different approach.",

            "SIMPLIFY":
                "Explain the same component_context using simpler language and analogies.",

            "MORE_DETAIL":
                "Increase the technical depth without restarting.",

            "EXAMPLE":
                "Provide one worked example immediately.",

            "MORE_EXAMPLES":
                "Provide a completely different worked example.",

            "STATUS":
                "Summarize the user's current learning progress.",

            "FINISH":
                "Politely conclude the technical explanation."
        }

        return objectives.get(
            action.name,
            "Respond appropriately."
        )

    # ======================================================
    # Guidance
    # ======================================================

    @staticmethod
    def _guidance(history) -> str:

        guidance = []

        if history.examples_given == 0:
            guidance.append(
                "- No examples have been given yet."
            )

        elif history.examples_given == 1:
            guidance.append(
                "- One example has already been shown. Use a different scenario."
            )

        else:
            guidance.append(
                "- Several examples have already been used. Avoid repetition."
            )

        if history.re_explanations > 0:
            guidance.append(
                "- Use a different mental model than previous explanations."
            )

        if history.simplifications > 0:
            guidance.append(
                "- The user benefits from simpler explanations."
            )

        if history.detail_level >= 2:
            guidance.append(
                "- Assume the user understands the fundamentals."
            )

        guidance.append(
            "- Keep the response focused on one component_context."
        )

        guidance.append(
            "- Do not ask whether the user wants to continue."
        )

        return "\n".join(guidance)