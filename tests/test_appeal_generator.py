"""
Tests for the appeal generator module.
Note: These tests require a valid API key and make actual API calls.
For unit testing without API calls, mock the genai module.
"""

import unittest
import os
from unittest.mock import Mock, patch
from parking_appeal.appeal_generator import AppealGenerator
from parking_appeal.appeal_strategies import AppealStrategyAnalyzer


class TestAppealGenerator(unittest.TestCase):
    """Test the AppealGenerator class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        generator = AppealGenerator(api_key="test_key")
        self.assertEqual(generator.api_key, "test_key")

    def test_init_without_api_key_raises_error(self):
        """Test initialization without API key raises error."""
        # Temporarily remove env var if it exists
        old_key = os.environ.pop('GOOGLE_GENERATIVE_AI_API_KEY', None)
        try:
            with self.assertRaises(ValueError):
                AppealGenerator()
        finally:
            if old_key:
                os.environ['GOOGLE_GENERATIVE_AI_API_KEY'] = old_key

    def test_format_dict(self):
        """Test dictionary formatting for prompts."""
        generator = AppealGenerator(api_key="test_key")
        data = {'test_key': 'test_value', 'another_key': 'another_value'}
        formatted = generator._format_dict(data)
        self.assertIn('Test Key', formatted)
        self.assertIn('test_value', formatted)

    def test_format_dict_empty(self):
        """Test formatting empty dictionary."""
        generator = AppealGenerator(api_key="test_key")
        formatted = generator._format_dict({})
        self.assertEqual(formatted, "None provided")

    @patch('parking_appeal.appeal_generator.genai')
    def test_build_appeal_prompt(self, mock_genai):
        """Test appeal prompt building."""
        generator = AppealGenerator(api_key="test_key")

        citation_details = {
            'citation_number': 'ABC123',
            'violation_type': 'expired meter',
        }

        location_info = {
            'state': {'name': 'California', 'statute_limitations_days': 21},
            'city': None,
        }

        angle = AppealStrategyAnalyzer.get_angle("procedural_error")
        evidence = {'photos': True}

        prompt = generator._build_appeal_prompt(
            citation_details, location_info, angle, evidence
        )

        self.assertIn("ABC123", prompt)
        self.assertIn("expired meter", prompt)
        self.assertIn("California", prompt)
        self.assertIn("Procedural Error", prompt)


class TestAppealGeneratorIntegration(unittest.TestCase):
    """
    Integration tests that actually call the API.
    These are skipped if no API key is available.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = os.getenv('GOOGLE_GENERATIVE_AI_API_KEY')
        if not self.api_key:
            self.skipTest("No API key available for integration tests")

        self.generator = AppealGenerator(api_key=self.api_key)

        self.citation_details = {
            'citation_number': 'TEST123',
            'citation_date': '01/15/2024',
            'location': '123 Main St',
            'violation_type': 'expired meter',
            'unclear_signage': True,
        }

        self.location_info = {
            'state': {
                'name': 'California',
                'statute_limitations_days': 21,
                'common_defenses': ['Test defense'],
            },
            'city': None,
        }

        self.evidence = {
            'has_photos': True,
            'photos_details': 'Photos of unclear signage',
        }

    def test_generate_comprehensive_appeal_integration(self):
        """Test generating a comprehensive appeal (actual API call)."""
        appeal = self.generator.generate_comprehensive_appeal(
            self.citation_details,
            self.location_info,
            ['signage_issues', 'procedural_error'],
            self.evidence
        )

        self.assertIsInstance(appeal, str)
        self.assertGreater(len(appeal), 100)
        # Should contain citation number
        self.assertIn('TEST123', appeal)

    def test_analyze_citation_strength_integration(self):
        """Test citation strength analysis (actual API call)."""
        analysis = self.generator.analyze_citation_strength(
            self.citation_details,
            self.location_info,
            self.evidence
        )

        self.assertTrue(analysis.get('success'))
        self.assertIn('analysis', analysis)
        self.assertIsInstance(analysis['analysis'], str)


if __name__ == '__main__':
    unittest.main()
