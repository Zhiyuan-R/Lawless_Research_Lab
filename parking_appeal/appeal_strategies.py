"""
Different appeal strategies and angles for parking citations.
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class AppealAngle:
    """Represents a specific angle or strategy for appealing a citation."""
    name: str
    description: str
    key_questions: List[str]
    strength_indicators: List[str]
    required_evidence: List[str]


class AppealStrategyAnalyzer:
    """Analyzes citation details to identify viable appeal angles."""

    APPEAL_ANGLES = {
        "procedural_error": AppealAngle(
            name="Procedural Error",
            description="Citation was issued incorrectly or does not follow proper procedures",
            key_questions=[
                "Was the citation securely attached to your vehicle?",
                "Are all details on the citation accurate (date, time, location, vehicle info)?",
                "Did the officer follow proper procedures?",
                "Is the citation number valid and legible?",
            ],
            strength_indicators=[
                "Incorrect vehicle information",
                "Wrong date or time",
                "Citation not properly attached",
                "Missing required information",
                "Officer signature missing",
            ],
            required_evidence=[
                "Photos of the citation showing errors",
                "Vehicle registration showing correct information",
                "Photos showing improper attachment if applicable",
            ],
        ),
        "signage_issues": AppealAngle(
            name="Inadequate or Confusing Signage",
            description="Parking restrictions were not clearly posted or signs were confusing",
            key_questions=[
                "Were there clear signs indicating the parking restriction?",
                "Were the signs visible and unobstructed?",
                "Were there conflicting signs in the area?",
                "Was the sign text legible and in compliance with local standards?",
            ],
            strength_indicators=[
                "No sign visible from parking spot",
                "Sign obstructed by trees/objects",
                "Conflicting information from multiple signs",
                "Faded or illegible signs",
                "Sign not meeting MUTCD standards",
            ],
            required_evidence=[
                "Photos showing parking spot and nearby signage",
                "Photos of any obstructions or damaged signs",
                "Photos showing perspective from driver's position",
                "Multiple angles showing sign placement",
            ],
        ),
        "meter_malfunction": AppealAngle(
            name="Meter or Payment System Malfunction",
            description="The parking meter or payment system was not working properly",
            key_questions=[
                "Did you attempt to pay for parking?",
                "Was the meter displaying any error messages?",
                "Did you report the malfunction?",
                "Do you have proof of attempted payment?",
            ],
            strength_indicators=[
                "Meter displayed 'out of order'",
                "Payment transaction failed but money charged",
                "Receipt showing payment attempt",
                "Multiple users reporting same issue",
            ],
            required_evidence=[
                "Photos of meter showing malfunction",
                "Payment receipts or transaction records",
                "Credit card statement showing charge",
                "Report filed about meter malfunction",
            ],
        ),
        "emergency_circumstances": AppealAngle(
            name="Emergency or Extenuating Circumstances",
            description="Parking violation occurred due to an emergency situation",
            key_questions=[
                "What was the nature of the emergency?",
                "Do you have documentation of the emergency?",
                "Was this your first parking violation?",
                "How long was the vehicle parked?",
            ],
            strength_indicators=[
                "Medical emergency",
                "Vehicle breakdown",
                "Avoiding accident",
                "Personal safety concern",
                "Family emergency",
            ],
            required_evidence=[
                "Medical records or doctor's note",
                "Police report if applicable",
                "Tow truck receipt or mechanic report",
                "Photos showing vehicle condition",
                "Witness statements if available",
            ],
        ),
        "payment_display_issue": AppealAngle(
            name="Valid Payment Not Displayed",
            description="Payment was made but receipt was not properly displayed",
            key_questions=[
                "Did you pay for parking before the citation was issued?",
                "Do you have the parking receipt?",
                "Why was the receipt not displayed?",
                "What time was payment made vs. citation issued?",
            ],
            strength_indicators=[
                "Receipt timestamp before citation time",
                "Payment for correct zone/meter",
                "Receipt fell inside vehicle",
                "Wind blew receipt away",
            ],
            required_evidence=[
                "Original parking receipt",
                "Credit card or app payment confirmation",
                "Photos of receipt with timestamp",
                "Transaction records from parking app",
            ],
        ),
        "zone_confusion": AppealAngle(
            name="Unclear Zone or Time Restrictions",
            description="Zone boundaries or time restrictions were unclear or ambiguous",
            key_questions=[
                "Were zone boundaries clearly marked?",
                "Were time restrictions clearly posted?",
                "Were there multiple overlapping zones?",
                "Was the zone map accurate?",
            ],
            strength_indicators=[
                "No clear zone boundary markings",
                "Conflicting zone signs",
                "Time restriction periods unclear",
                "Street cleaning schedule ambiguous",
            ],
            required_evidence=[
                "Photos showing zone markings (or lack thereof)",
                "Photos of relevant signage",
                "Screenshot of official parking map if applicable",
                "Photos showing perspective of parking location",
            ],
        ),
        "first_time_leniency": AppealAngle(
            name="First-Time Violation / Good Record",
            description="Request for leniency based on clean parking record",
            key_questions=[
                "Is this your first parking violation in this jurisdiction?",
                "How long have you been parking in this area?",
                "Do you have a generally good compliance record?",
                "Was this an honest mistake?",
            ],
            strength_indicators=[
                "No prior parking citations",
                "Long-time resident or worker in area",
                "Regular parker with good history",
                "Simple misunderstanding of rules",
            ],
            required_evidence=[
                "Driving record or DMV printout",
                "Statement of good parking history",
                "Proof of residency or employment in area",
                "Character reference if applicable",
            ],
        ),
        "disability_accommodation": AppealAngle(
            name="Disability-Related Accommodation",
            description="Citation related to disability parking or accommodation needs",
            key_questions=[
                "Do you have a valid disability placard or license plate?",
                "Was the placard properly displayed?",
                "Was the accessible parking space properly marked?",
                "Were you denied reasonable accommodation?",
            ],
            strength_indicators=[
                "Valid disability placard not recognized",
                "Accessible space markings faded or unclear",
                "No accessible parking available",
                "Time limit insufficient for disability needs",
            ],
            required_evidence=[
                "Copy of disability placard documentation",
                "Photos showing placard displayed",
                "Photos of parking space markings",
                "Medical documentation if relevant",
            ],
        ),
        "time_discrepancy": AppealAngle(
            name="Time Discrepancy or Error",
            description="Citation time is incorrect or conflicts with actual circumstances",
            key_questions=[
                "What time did you park?",
                "What time did you leave?",
                "Do you have proof of your timeline?",
                "What time does the citation show?",
            ],
            strength_indicators=[
                "Citation time impossible or implausible",
                "Proof of being elsewhere at citation time",
                "Multiple citations same time different locations",
                "Meter time conflicts with citation time",
            ],
            required_evidence=[
                "Timestamped photos or videos",
                "Receipt or parking payment with timestamp",
                "GPS or phone location data",
                "Witness statements",
                "Business receipts showing location at citation time",
            ],
        ),
    }

    @classmethod
    def get_all_angles(cls) -> Dict[str, AppealAngle]:
        """Get all available appeal angles."""
        return cls.APPEAL_ANGLES

    @classmethod
    def get_angle(cls, angle_key: str) -> AppealAngle:
        """Get a specific appeal angle."""
        return cls.APPEAL_ANGLES.get(angle_key)

    @classmethod
    def analyze_situation(cls, citation_details: Dict) -> List[str]:
        """
        Analyze citation details to suggest relevant appeal angles.

        Args:
            citation_details: Dictionary containing citation information

        Returns:
            List of relevant appeal angle keys
        """
        relevant_angles = []

        # Check for procedural errors
        if (citation_details.get("has_errors") or
            citation_details.get("missing_info") or
            citation_details.get("incorrect_vehicle_info")):
            relevant_angles.append("procedural_error")

        # Check for signage issues
        if (citation_details.get("unclear_signage") or
            citation_details.get("no_visible_signs") or
            citation_details.get("conflicting_signs")):
            relevant_angles.append("signage_issues")

        # Check for meter issues
        if (citation_details.get("meter_malfunction") or
            citation_details.get("payment_failed") or
            citation_details.get("paid_but_cited")):
            relevant_angles.append("meter_malfunction")

        # Check for emergency
        if citation_details.get("emergency_situation"):
            relevant_angles.append("emergency_circumstances")

        # Check for payment display issue
        if (citation_details.get("paid_not_displayed") or
            citation_details.get("receipt_not_visible")):
            relevant_angles.append("payment_display_issue")

        # Check for zone confusion
        if (citation_details.get("unclear_zone") or
            citation_details.get("zone_boundary_unclear")):
            relevant_angles.append("zone_confusion")

        # Check for first-time situation
        if citation_details.get("first_violation"):
            relevant_angles.append("first_time_leniency")

        # Check for disability-related
        if (citation_details.get("disability_related") or
            citation_details.get("has_disability_placard")):
            relevant_angles.append("disability_accommodation")

        # Check for time issues
        if (citation_details.get("time_incorrect") or
            citation_details.get("timeline_conflicts")):
            relevant_angles.append("time_discrepancy")

        # If no specific angles identified, return a default set
        if not relevant_angles:
            relevant_angles = ["procedural_error", "signage_issues", "first_time_leniency"]

        return relevant_angles

    @classmethod
    def get_angle_strength(cls, angle_key: str, evidence: Dict) -> str:
        """
        Evaluate the strength of a particular appeal angle given evidence.

        Returns: "strong", "moderate", or "weak"
        """
        angle = cls.get_angle(angle_key)
        if not angle:
            return "weak"

        evidence_count = 0
        indicator_matches = 0

        # Check if evidence items are present
        for evidence_item in angle.required_evidence:
            if evidence.get(evidence_item.lower().replace(" ", "_")):
                evidence_count += 1

        # Simple strength calculation
        evidence_ratio = evidence_count / len(angle.required_evidence) if angle.required_evidence else 0

        if evidence_ratio >= 0.7:
            return "strong"
        elif evidence_ratio >= 0.4:
            return "moderate"
        else:
            return "weak"
