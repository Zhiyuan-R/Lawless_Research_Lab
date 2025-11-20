"""
City and state-specific parking regulations and common appeal grounds.
"""

from typing import Dict, List, Optional


class RegulationDatabase:
    """Database of parking regulations by city and state."""

    # Common appeal grounds that apply across jurisdictions
    COMMON_APPEAL_GROUNDS = [
        "unclear_signage",
        "emergency_circumstances",
        "vehicle_malfunction",
        "medical_emergency",
        "incorrect_citation_details",
        "meter_malfunction",
        "conflicting_signs",
        "first_time_offense",
        "extenuating_circumstances",
        "procedural_errors",
        "incorrect_vehicle_info",
        "paid_but_not_displayed",
        "time_discrepancy",
        "zone_confusion",
        "disability_accommodation",
    ]

    # State-specific regulations and common defenses
    STATE_REGULATIONS = {
        "CA": {
            "name": "California",
            "statute_limitations_days": 21,
            "common_defenses": [
                "CVC 22507.8 - Disabled parking violations require proper investigation",
                "CVC 40215 - Notice of parking violation must be securely attached",
                "Signage must comply with Manual on Uniform Traffic Control Devices (MUTCD)",
            ],
            "appeal_address_format": "City parking authority or designated appeals board",
        },
        "NY": {
            "name": "New York",
            "statute_limitations_days": 30,
            "common_defenses": [
                "NYC Traffic Rules require clear and visible signage",
                "Broken meters - proof required within 7 days",
                "Emergency vehicles - documentation required",
            ],
            "appeal_address_format": "Department of Finance, Parking Violations Bureau",
        },
        "TX": {
            "name": "Texas",
            "statute_limitations_days": 21,
            "common_defenses": [
                "Transportation Code 681.0101 - Proper notice requirements",
                "Sign visibility and compliance with state standards",
                "Meter malfunction - immediate reporting helps case",
            ],
            "appeal_address_format": "Municipal court or designated hearing officer",
        },
        "FL": {
            "name": "Florida",
            "statute_limitations_days": 30,
            "common_defenses": [
                "F.S. 316.1967 - Parking regulations must be clearly posted",
                "Meter violations - malfunction must be documented",
                "Emergency circumstances with supporting documentation",
            ],
            "appeal_address_format": "City clerk or parking violations bureau",
        },
        "IL": {
            "name": "Illinois",
            "statute_limitations_days": 21,
            "common_defenses": [
                "Chicago Municipal Code - signage requirements",
                "Meter payment issues - transaction records",
                "Medical emergency documentation",
            ],
            "appeal_address_format": "Department of Administrative Hearings",
        },
    }

    # City-specific regulations (can override state defaults)
    CITY_REGULATIONS = {
        "San Francisco": {
            "state": "CA",
            "specific_rules": [
                "SFMTA requires photos of signage for signage-related appeals",
                "Street cleaning violations - check SFMTA calendar",
                "Residential permit zones - proof of residency required",
            ],
            "online_appeal": True,
            "fee_waiver_available": True,
        },
        "Los Angeles": {
            "state": "CA",
            "specific_rules": [
                "LADOT handles parking enforcement",
                "First-time violators may get reduced fines",
                "Photo evidence highly recommended",
            ],
            "online_appeal": True,
            "fee_waiver_available": False,
        },
        "New York City": {
            "state": "NY",
            "specific_rules": [
                "Online appeals through NYC.gov required for most violations",
                "Hearing requests must be filed within 30 days",
                "Evidence upload system available online",
            ],
            "online_appeal": True,
            "fee_waiver_available": False,
        },
        "Chicago": {
            "state": "IL",
            "specific_rules": [
                "City of Chicago parking ticket portal",
                "Early payment discount available (not applicable if appealing)",
                "Administrative hearing process",
            ],
            "online_appeal": True,
            "fee_waiver_available": False,
        },
        "Houston": {
            "state": "TX",
            "specific_rules": [
                "Houston Municipal Courts handle appeals",
                "Written statement required for appeal",
                "Court appearance may be required for some violations",
            ],
            "online_appeal": False,
            "fee_waiver_available": True,
        },
        "Miami": {
            "state": "FL",
            "specific_rules": [
                "Miami Parking Authority handles enforcement",
                "Online contest system available",
                "Supporting documents must be uploaded or mailed",
            ],
            "online_appeal": True,
            "fee_waiver_available": False,
        },
    }

    @classmethod
    def get_state_info(cls, state_code: str) -> Optional[Dict]:
        """Get regulation information for a specific state."""
        return cls.STATE_REGULATIONS.get(state_code.upper())

    @classmethod
    def get_city_info(cls, city_name: str) -> Optional[Dict]:
        """Get regulation information for a specific city."""
        return cls.CITY_REGULATIONS.get(city_name)

    @classmethod
    def get_combined_info(cls, city_name: Optional[str], state_code: str) -> Dict:
        """Get combined regulation info for city and state."""
        info = {
            "state": cls.get_state_info(state_code),
            "city": None,
            "available_grounds": cls.COMMON_APPEAL_GROUNDS,
        }

        if city_name:
            city_info = cls.get_city_info(city_name)
            if city_info and city_info.get("state") == state_code.upper():
                info["city"] = city_info

        return info

    @classmethod
    def get_all_states(cls) -> List[str]:
        """Get list of all supported states."""
        return list(cls.STATE_REGULATIONS.keys())

    @classmethod
    def get_cities_for_state(cls, state_code: str) -> List[str]:
        """Get list of cities for a specific state."""
        state_code = state_code.upper()
        return [
            city for city, info in cls.CITY_REGULATIONS.items()
            if info.get("state") == state_code
        ]
