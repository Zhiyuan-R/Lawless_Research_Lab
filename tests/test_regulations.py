"""
Tests for the regulations module.
"""

import unittest
from parking_appeal.regulations import RegulationDatabase


class TestRegulationDatabase(unittest.TestCase):
    """Test the RegulationDatabase class."""

    def test_get_state_info(self):
        """Test retrieving state information."""
        ca_info = RegulationDatabase.get_state_info("CA")
        self.assertIsNotNone(ca_info)
        self.assertEqual(ca_info['name'], "California")
        self.assertIn('statute_limitations_days', ca_info)

    def test_get_state_info_case_insensitive(self):
        """Test state lookup is case insensitive."""
        ca_lower = RegulationDatabase.get_state_info("ca")
        ca_upper = RegulationDatabase.get_state_info("CA")
        self.assertEqual(ca_lower, ca_upper)

    def test_get_city_info(self):
        """Test retrieving city information."""
        sf_info = RegulationDatabase.get_city_info("San Francisco")
        self.assertIsNotNone(sf_info)
        self.assertEqual(sf_info['state'], "CA")
        self.assertIn('specific_rules', sf_info)

    def test_get_combined_info(self):
        """Test getting combined city and state info."""
        info = RegulationDatabase.get_combined_info("San Francisco", "CA")
        self.assertIsNotNone(info['state'])
        self.assertIsNotNone(info['city'])
        self.assertEqual(info['state']['name'], "California")

    def test_get_combined_info_state_only(self):
        """Test getting state info without city."""
        info = RegulationDatabase.get_combined_info(None, "TX")
        self.assertIsNotNone(info['state'])
        self.assertIsNone(info['city'])

    def test_get_all_states(self):
        """Test getting all supported states."""
        states = RegulationDatabase.get_all_states()
        self.assertIsInstance(states, list)
        self.assertIn("CA", states)
        self.assertIn("NY", states)

    def test_get_cities_for_state(self):
        """Test getting cities for a specific state."""
        ca_cities = RegulationDatabase.get_cities_for_state("CA")
        self.assertIsInstance(ca_cities, list)
        self.assertIn("San Francisco", ca_cities)
        self.assertIn("Los Angeles", ca_cities)

    def test_common_appeal_grounds(self):
        """Test common appeal grounds are defined."""
        grounds = RegulationDatabase.COMMON_APPEAL_GROUNDS
        self.assertIsInstance(grounds, list)
        self.assertGreater(len(grounds), 0)
        self.assertIn("unclear_signage", grounds)
        self.assertIn("emergency_circumstances", grounds)


if __name__ == '__main__':
    unittest.main()
