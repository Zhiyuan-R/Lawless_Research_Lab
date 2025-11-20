#!/usr/bin/env python3
"""
Demo script that shows the app functionality without requiring API calls.
This demonstrates the structure, workflow, and logic of the application.
"""

from parking_appeal.regulations import RegulationDatabase
from parking_appeal.appeal_strategies import AppealStrategyAnalyzer

print("\n" + "="*70)
print(" "*15 + "PARKING CITATION APPEAL ASSISTANT DEMO")
print("="*70)
print("\nThis demo showcases the application's features without API calls.\n")

# Demo 1: Jurisdiction Database
print("\n" + "="*70)
print("DEMO 1: Jurisdiction-Specific Regulations")
print("="*70 + "\n")

print("Supported states:", ", ".join(RegulationDatabase.get_all_states()))

ca_info = RegulationDatabase.get_state_info("CA")
print(f"\nCalifornia Information:")
print(f"  • Appeal deadline: {ca_info['statute_limitations_days']} days")
print(f"  • Common defenses:")
for defense in ca_info['common_defenses']:
    print(f"    - {defense}")

sf_info = RegulationDatabase.get_city_info("San Francisco")
print(f"\nSan Francisco Specific:")
print(f"  • Online appeal available: {sf_info['online_appeal']}")
for rule in sf_info['specific_rules'][:2]:
    print(f"  • {rule}")

# Demo 2: Appeal Strategy Analysis
print("\n" + "="*70)
print("DEMO 2: Intelligent Appeal Angle Identification")
print("="*70 + "\n")

citation_scenario = {
    'unclear_signage': True,
    'first_violation': True,
    'meter_malfunction': True,
    'paid_for_parking': True,
}

print("Citation Scenario:")
for key, value in citation_scenario.items():
    if value:
        print(f"  • {key.replace('_', ' ').title()}: Yes")

suggested_angles = AppealStrategyAnalyzer.analyze_situation(citation_scenario)
print(f"\nIdentified {len(suggested_angles)} potential appeal angles:")

for angle_key in suggested_angles:
    angle = AppealStrategyAnalyzer.get_angle(angle_key)
    if angle:
        print(f"\n  ✓ {angle.name}")
        print(f"    Description: {angle.description}")
        print(f"    Top key questions:")
        for q in angle.key_questions[:2]:
            print(f"      - {q}")

# Demo 3: Appeal Angle Details
print("\n" + "="*70)
print("DEMO 3: Detailed Appeal Angle Information")
print("="*70 + "\n")

signage_angle = AppealStrategyAnalyzer.get_angle("signage_issues")
print(f"Appeal Angle: {signage_angle.name}")
print(f"\nDescription: {signage_angle.description}")
print(f"\nStrength Indicators:")
for indicator in signage_angle.strength_indicators[:3]:
    print(f"  • {indicator}")
print(f"\nRequired Evidence:")
for evidence in signage_angle.required_evidence:
    print(f"  • {evidence}")

# Demo 4: Evidence Strength Evaluation
print("\n" + "="*70)
print("DEMO 4: Case Strength Evaluation")
print("="*70 + "\n")

print("Testing different evidence scenarios:\n")

# Weak case
weak_evidence = {}
weak_strength = AppealStrategyAnalyzer.get_angle_strength("signage_issues", weak_evidence)
print(f"No evidence: {weak_strength.upper()} case")

# Moderate case
moderate_evidence = {
    'photos_showing_parking_spot_and_nearby_signage': True,
    'photos_of_any_obstructions_or_damaged_signs': True,
}
moderate_strength = AppealStrategyAnalyzer.get_angle_strength("signage_issues", moderate_evidence)
print(f"Some evidence (2/4): {moderate_strength.upper()} case")

# Strong case
strong_evidence = {
    'photos_showing_parking_spot_and_nearby_signage': True,
    'photos_of_any_obstructions_or_damaged_signs': True,
    'photos_showing_perspective_from_driver\'s_position': True,
}
strong_strength = AppealStrategyAnalyzer.get_angle_strength("signage_issues", strong_evidence)
print(f"Substantial evidence (3/4): {strong_strength.upper()} case")

# Demo 5: Multi-Jurisdiction Support
print("\n" + "="*70)
print("DEMO 5: Multi-Jurisdiction Support")
print("="*70 + "\n")

cities_demo = [
    ("San Francisco", "CA"),
    ("New York City", "NY"),
    ("Chicago", "IL"),
]

for city, state in cities_demo:
    info = RegulationDatabase.get_combined_info(city, state)
    state_info = info['state']
    city_info = info['city']

    print(f"\n{city}, {state}:")
    print(f"  • Appeal deadline: {state_info['statute_limitations_days']} days")
    print(f"  • Online appeals: {city_info['online_appeal']}")
    print(f"  • City-specific rules: {len(city_info['specific_rules'])} rules defined")

# Demo 6: All Available Appeal Angles
print("\n" + "="*70)
print("DEMO 6: Complete Appeal Angle Catalog")
print("="*70 + "\n")

all_angles = AppealStrategyAnalyzer.get_all_angles()
print(f"Total available appeal angles: {len(all_angles)}\n")

for i, (key, angle) in enumerate(all_angles.items(), 1):
    print(f"{i}. {angle.name}")
    print(f"   {angle.description}")

# Summary
print("\n" + "="*70)
print("APPLICATION STRUCTURE SUMMARY")
print("="*70 + "\n")

print("The Parking Citation Appeal Assistant includes:")
print("  ✓ Comprehensive jurisdiction database (50 states, major cities)")
print("  ✓ 9 distinct appeal angles with detailed strategies")
print("  ✓ Intelligent situation analysis")
print("  ✓ Evidence strength evaluation")
print("  ✓ Interactive questionnaire system")
print("  ✓ AI-powered appeal generation (using Gemini 2.0 Pro)")
print("  ✓ Multi-angle appeal support")
print("  ✓ Automated file saving and organization")
print("  ✓ Comprehensive test suite")
print()
print("File Structure:")
print("  • parking_appeal/regulations.py - Jurisdiction database")
print("  • parking_appeal/appeal_strategies.py - Appeal angle definitions")
print("  • parking_appeal/appeal_generator.py - AI appeal generation")
print("  • parking_appeal/questionnaire.py - Interactive user input")
print("  • parking_appeal/workflow.py - Main orchestration")
print("  • main.py - CLI entry point")
print("  • tests/ - Comprehensive test suite (18 tests)")
print()
print("Usage:")
print("  Interactive mode: python main.py")
print("  Quick mode: python main.py --quick --citation NUM --state ST --violation TYPE")
print("  Examples: python example_usage.py")
print("  Tests: python -m unittest discover tests")

print("\n" + "="*70)
print("DEMO COMPLETE")
print("="*70 + "\n")
