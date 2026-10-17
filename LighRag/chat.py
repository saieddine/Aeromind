
import asyncio
import logging

from lightrag_service import ask

# Hide Python logging messages
logging.disable(logging.CRITICAL)


async def main():
    aircraft_id = "a320"
    conversation_id = "test_chat"
    method = "lightrag"

    print("AeroMind Chat")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nAsk a question: ").strip()

        if question.lower() in ("exit", "quit"):
            break

        if not question:
            continue

        try:
            result = await ask(
                aircraft_id=aircraft_id,
                question=question,
                conversation_id=conversation_id,
                mode="hybrid"
            )

            print("\nAnswer:")
            print(result["answer"])

            print("\nSources:")
            print(result.get("sources", []))

            print("\nMetadata:")
            print({
                **result.get("metadata", {}),
                "method": method,
                "aircraft_id": aircraft_id,
                "conversation_id": conversation_id
            })

        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
