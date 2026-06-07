"""Unit tests for the serverless FastAPI application."""

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.services.parser_service import ParserService


class TestAppEndpoints(unittest.TestCase):
    """Test case suite for FastAPI endpoints and parser services."""

    def setUp(self) -> None:
        """Sets up the TestClient before each test."""
        self.client = TestClient(app)

    def test_read_root(self) -> None:
        """Verifies that the root health check endpoint returns 200 and correct status."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "healthy",
            "service": "Serverless FastAPI Application"
        })

    def test_parser_empty_bytes(self) -> None:
        """Verifies that the ParserService raises ValueError when passed empty bytes."""
        with self.assertRaises(ValueError):
            ParserService.extract_text_from_pdf(b"")


if __name__ == "__main__":
    unittest.main()
