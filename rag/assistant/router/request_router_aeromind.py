"""AeroMind request router.

The router decides which assistant pipeline should handle a user request.
It does not execute the selected pipeline; it only returns a structured
RouteDecision for the backend/orchestrator to act on.
"""

import json

from ..llm.llm_client import llm_client
from ..prompts.router_prompt import RouterPrompt
from .route import Route
from .route_decision import RouteDecision
from ..config import ROUTER_MODEL, ROUTER_TEMPERATURE


class RequestRouter:
    """Select the appropriate AeroMind pipeline for a user request."""

    def __init__(self):
        self.client = llm_client.client
        self.model = ROUTER_MODEL

    def route(self, question: str) -> RouteDecision:
        """Classify a user request and return the selected route."""

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        prompt = RouterPrompt.build(question.strip())
        response = self._call_llm(prompt)
        decision = self._parse_response(response)

        self._print_debug(question, decision)

        return decision

    def _call_llm(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=ROUTER_TEMPERATURE,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return completion.choices[0].message.content

    def _parse_response(self, response: str) -> RouteDecision:
        try:
            data = json.loads(response)

            route = Route[data["route"]]
            confidence = float(data["confidence"])
            summary = data["decision_summary"]
            reply = data.get("response")

            return RouteDecision(
                route=route,
                confidence=confidence,
                reason=summary,
                response=reply,
            )

        except Exception as error:
            print("\nRouter JSON Error:")
            print(error)

            print("\nRaw Response:")
            print(response)

            return self._fallback()

    def _fallback(self) -> RouteDecision:
        """Use ordinary RAG as the safe knowledge-search fallback."""

        return RouteDecision(
            route=Route.RAG,
            confidence=0.60,
            reason="Router failed to produce valid JSON.",
            response=None,
        )

    def _print_debug(self, question: str, decision: RouteDecision):
        print("\n" + "=" * 60)
        print("AEROMIND REQUEST ROUTER")
        print("=" * 60)

        print("\nQuestion:")
        print(question)

        print("\nRoute:")
        print(decision.route.value)

        print("\nConfidence:")
        print(decision.confidence)

        print("\nDecision Summary:")
        print(decision.reason)

        if decision.response:
            print("\nConversation Response:")
            print(decision.response)

        print("=" * 60)
