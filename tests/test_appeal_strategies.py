"""
Tests for the appeal strategies module.
"""

import unittest
from parking_appeal.appeal_strategies import AppealStrategyAnalyzer, AppealAngle


class TestAppealStrategies(unittest.TestCase):
    """Test the AppealStrategyAnalyzer class."""

    def test_get_all_angles(self):
        """Test retrieving all appeal angles."""
        angles = AppealStrategyAnalyzer.get_all_angles()
        self.assertIsInstance(angles, dict)
        self.assertGreater(len(angles), 0)

    def test_get_specific_angle(self):
        """Test retrieving a specific appeal angle."""
        angle = AppealStrategyAnalyzer.get_angle("procedural_error")
        self.assertIsNotNone(angle)
        self.assertIsInstance(angle, AppealAngle)
        self.assertEqual(angle.name, "Procedural Error")

    def test_analyze_situation_procedural_error(self):
        """Test situation analysis identifies procedural errors."""
        citation_details = {
            'has_errors': True,
            'incorrect_vehicle_info': True,
        }
        angles = AppealStrategyAnalyzer.analyze_situation(citation_details)
        self.assertIn("procedural_error", angles)

    def test_analyze_situation_signage(self):
        """Test situation analysis identifies signage issues."""
        citation_details = {
            'unclear_signage': True,
            'no_visible_signs': True,
        }
        angles = AppealStrategyAnalyzer.analyze_situation(citation_details)
        self.assertIn("signage_issues", angles)

    def test_analyze_situation_emergency(self):
        """Test situation analysis identifies emergency circumstances."""
        citation_details = {
            'emergency_situation': True,
        }
        angles = AppealStrategyAnalyzer.analyze_situation(citation_details)
        self.assertIn("emergency_circumstances", angles)

    def test_analyze_situation_multiple_angles(self):
        """Test situation analysis identifies multiple angles."""
        citation_details = {
            'unclear_signage': True,
            'first_violation': True,
            'meter_malfunction': True,
        }
        angles = AppealStrategyAnalyzer.analyze_situation(citation_details)
        self.assertGreater(len(angles), 1)
        self.assertIn("signage_issues", angles)
        self.assertIn("first_time_leniency", angles)

    def test_analyze_situation_default_angles(self):
        """Test default angles are provided when no specific indicators."""
        citation_details = {}
        angles = AppealStrategyAnalyzer.analyze_situation(citation_details)
        self.assertGreater(len(angles), 0)

    def test_get_angle_strength_strong(self):
        """Test angle strength evaluation - strong case."""
        # For signage_issues, we need 3 out of 4 evidence items for "strong" (>=70%)
        evidence = {
            'photos_showing_parking_spot_and_nearby_signage': True,
            'photos_of_any_obstructions_or_damaged_signs': True,
            'photos_showing_perspective_from_driver\'s_position': True,
        }
        strength = AppealStrategyAnalyzer.get_angle_strength("signage_issues", evidence)
        self.assertEqual(strength, "strong")

    def test_get_angle_strength_weak(self):
        """Test angle strength evaluation - weak case."""
        evidence = {}
        strength = AppealStrategyAnalyzer.get_angle_strength("signage_issues", evidence)
        self.assertEqual(strength, "weak")

    def test_appeal_angle_dataclass(self):
        """Test AppealAngle dataclass structure."""
        angle = AppealStrategyAnalyzer.get_angle("meter_malfunction")
        self.assertIsNotNone(angle.name)
        self.assertIsNotNone(angle.description)
        self.assertIsInstance(angle.key_questions, list)
        self.assertIsInstance(angle.strength_indicators, list)
        self.assertIsInstance(angle.required_evidence, list)


if __name__ == '__main__':
    unittest.main()
