"""Offline interface checks. These do not test real retrieval or answer quality."""
import unittest
from unittest.mock import AsyncMock, patch

from LighRag import lightrag_service as service
from LighRag import rag_factory


class ServiceContractTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        service._instances.clear()

    async def asyncTearDown(self):
        service._instances.clear()

    async def test_a320_request_and_real_reference_format(self):
        rag = AsyncMock()
        rag.aquery.return_value = "Retrieved answer.\n### References\n- [1] A320 manual\n* [2] Hydraulics"
        with patch.object(service, "get_rag", AsyncMock(return_value=rag)) as factory:
            result = await service.ask("a320", "What are the A320 hydraulic systems?", "test_001")
            await service.ask("a320", "How is the blue hydraulic system powered?", "test_001")
        factory.assert_awaited_once_with("a320")
        self.assertEqual(result["answer"], "Retrieved answer.")
        self.assertEqual(result["sources"], [{"title": "A320 manual"}, {"title": "Hydraulics"}])
        self.assertEqual(result["metadata"]["method"], "lightrag")
        self.assertEqual(result["metadata"]["aircraft_id"], "a320")
        self.assertEqual(result["metadata"]["conversation_id"], "test_001")
        self.assertEqual(rag.aquery.await_args.kwargs["param"].mode, "hybrid")
        self.assertGreaterEqual(result["metadata"]["latency_ms"], 0)

    async def test_missing_references_do_not_create_fake_sources(self):
        rag = AsyncMock()
        rag.aquery.return_value = "Answer without references."
        with patch.object(service, "get_rag", AsyncMock(return_value=rag)):
            result = await service.ask("a320", "How does the RAT work?", "test_002")
        self.assertEqual(result["sources"], [])

    async def test_empty_question_and_invalid_mode_fail_before_initialization(self):
        with patch.object(service, "get_rag", AsyncMock()) as factory:
            with self.assertRaises(ValueError):
                await service.ask("a320", "   ", "test_003")
            with self.assertRaises(ValueError):
                await service.ask("a320", "Question", "test_003", mode="unknown")
        factory.assert_not_awaited()

    async def test_provider_error_propagates_for_backend_logging(self):
        rag = AsyncMock()
        rag.aquery.side_effect = RuntimeError("Provider unavailable")
        with patch.object(service, "get_rag", AsyncMock(return_value=rag)):
            with self.assertRaisesRegex(RuntimeError, "Provider unavailable"):
                await service.ask("a320", "How does the RAT work?", "test_004")

    async def test_aircraft_path_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            await rag_factory.get_rag("../outside")

    async def test_missing_configuration_fails_before_creating_storage(self):
        with patch.object(rag_factory, "LLM_KEY", None):
            with self.assertRaisesRegex(RuntimeError, "LLM_BINDING_API_KEY"):
                await rag_factory.get_rag("a320")


if __name__ == "__main__":
    unittest.main()
