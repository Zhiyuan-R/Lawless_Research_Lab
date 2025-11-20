#!/usr/bin/env python3
"""
Example usage of the Parking Citation Appeal Assistant.
This demonstrates how to use the API programmatically.
"""

import os
from dotenv import load_dotenv
from parking_appeal.appeal_generator import AppealGenerator
from parking_appeal.regulations import RegulationDatabase
from parking_appeal.appeal_strategies import AppealStrategyAnalyzer

# Load environment variables
load_dotenv()


def example_1_simple_appeal():
    """Example 1: Generate a simple appeal with minimal information."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Appeal Generation")
    print("="*70 + "\n")

    # Initialize the generator
    generator = AppealGenerator()

    # Basic citation details
    citation_details = {
        'citation_number': 'SF12345',
        'citation_date': '01/15/2024',
        'location': '123 Market Street, San Francisco',
        'violation_type': 'Expired Meter',
        'fine_amount': '$75',
        'first_violation': True,
    }

    # Get jurisdiction info
    location_info = RegulationDatabase.get_combined_info("San Francisco", "CA")

    # Select appeal angles
    angles = ['first_time_leniency', 'procedural_error']

    # Minimal evidence
    evidence = {
        'has_photos': False,
        'clean_record': True,
    }

    # Generate comprehensive appeal
    appeal = generator.generate_comprehensive_appeal(
        citation_details,
        {'state': location_info.get('state'), 'city': location_info.get('city')},
        angles,
        evidence
    )

    print("Generated Appeal:")
    print("-" * 70)
    print(appeal)
    print("-" * 70)


def example_2_detailed_appeal():
    """Example 2: Generate a detailed appeal with multiple angles."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Detailed Multi-Angle Appeal")
    print("="*70 + "\n")

    generator = AppealGenerator()

    # Detailed citation information
    citation_details = {
        'citation_number': 'NYC67890',
        'citation_date': '02/10/2024',
        'citation_time': '2:30 PM',
        'location': '456 Broadway, New York, NY',
        'violation_type': 'No Standing Zone',
        'fine_amount': '$115',
        'unclear_signage': True,
        'first_violation': False,
        'emergency_situation': True,
        'emergency_description': 'Medical emergency - passenger required immediate assistance',
        'time_parked': '5 minutes',
    }

    # Get NYC regulations
    location_info = RegulationDatabase.get_combined_info("New York City", "NY")

    # Multiple appeal angles
    angles = ['signage_issues', 'emergency_circumstances', 'time_discrepancy']

    # Substantial evidence
    evidence = {
        'has_photos_of_parking_location_and_signage': True,
        'photos_of_parking_location_and_signage_details': '4 photos showing no visible signage from parking position',
        'has_medical_documentation_(for_emergency)': True,
        'medical_documentation_(for_emergency)_details': 'ER admission records with timestamp',
        'has_witness_statements': True,
        'witness_statements_details': 'Passenger statement confirming medical emergency',
        'has_photos_of_the_citation_itself': True,
    }

    # Generate individual appeals for each angle
    individual_appeals = generator.generate_multi_angle_appeal(
        citation_details,
        {'state': location_info.get('state'), 'city': location_info.get('city')},
        angles,
        evidence
    )

    print("Generated Individual Appeals:")
    print("-" * 70)
    for angle_name, appeal_text in individual_appeals.items():
        print(f"\n=== {angle_name} ===\n")
        print(appeal_text)
        print("\n" + "-" * 70)


def example_3_case_analysis():
    """Example 3: Analyze appeal strength before generating."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Case Strength Analysis")
    print("="*70 + "\n")

    generator = AppealGenerator()

    citation_details = {
        'citation_number': 'LA11223',
        'citation_date': '03/05/2024',
        'location': 'Sunset Blvd, Los Angeles',
        'violation_type': 'Street Cleaning',
        'unclear_signage': True,
        'conflicting_signs': True,
        'first_violation': True,
    }

    location_info = RegulationDatabase.get_combined_info("Los Angeles", "CA")

    evidence = {
        'has_photos_of_parking_location_and_signage': True,
        'photos_of_parking_location_and_signage_details': 'Multiple photos showing two conflicting street cleaning signs',
        'has_photos_showing_perspective_from_driver\'s_position': True,
        'has_vehicle_registration_documents': True,
        'clean_record': True,
    }

    # Get AI analysis
    analysis = generator.analyze_citation_strength(
        citation_details,
        {'state': location_info.get('state'), 'city': location_info.get('city')},
        evidence
    )

    if analysis.get('success'):
        print("AI Case Analysis:")
        print("-" * 70)
        print(analysis['analysis'])
        print("-" * 70)
    else:
        print(f"Analysis error: {analysis.get('error')}")


def example_4_strategy_analysis():
    """Example 4: Use strategy analyzer to identify angles."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Strategy Analysis")
    print("="*70 + "\n")

    citation_details = {
        'unclear_signage': True,
        'meter_malfunction': True,
        'first_violation': True,
        'paid_for_parking': True,
        'payment_failed': True,
    }

    # Analyze situation
    suggested_angles = AppealStrategyAnalyzer.analyze_situation(citation_details)

    print(f"Suggested Appeal Angles ({len(suggested_angles)}):")
    print("-" * 70)

    for angle_key in suggested_angles:
        angle = AppealStrategyAnalyzer.get_angle(angle_key)
        if angle:
            print(f"\n{angle.name}")
            print(f"  Description: {angle.description}")
            print(f"  Key Questions:")
            for q in angle.key_questions[:2]:  # Show first 2 questions
                print(f"    • {q}")

    print("\n" + "-" * 70)


def example_5_jurisdiction_lookup():
    """Example 5: Look up jurisdiction-specific information."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Jurisdiction Information Lookup")
    print("="*70 + "\n")

    # Look up California state info
    ca_info = RegulationDatabase.get_state_info("CA")
    print("California State Information:")
    print("-" * 70)
    print(f"State: {ca_info['name']}")
    print(f"Appeal Deadline: {ca_info['statute_limitations_days']} days")
    print(f"\nCommon Defenses:")
    for defense in ca_info['common_defenses']:
        print(f"  • {defense}")

    # Look up San Francisco city info
    print("\n")
    sf_info = RegulationDatabase.get_city_info("San Francisco")
    print("San Francisco City Information:")
    print("-" * 70)
    print(f"Online Appeal Available: {sf_info['online_appeal']}")
    print(f"Fee Waiver Available: {sf_info['fee_waiver_available']}")
    print(f"\nCity-Specific Rules:")
    for rule in sf_info['specific_rules']:
        print(f"  • {rule}")

    print("\n" + "-" * 70)


def run_all_examples():
    """Run all examples."""
    examples = [
        example_1_simple_appeal,
        example_2_detailed_appeal,
        example_3_case_analysis,
        example_4_strategy_analysis,
        example_5_jurisdiction_lookup,
    ]

    print("\n" + "="*70)
    print("PARKING CITATION APPEAL ASSISTANT - EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates various ways to use the appeal assistant.")
    print("Each example shows different features and use cases.")

    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\n\nRunning Example {i}...")
            example_func()
        except Exception as e:
            print(f"\nError in Example {i}: {str(e)}")

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)


if __name__ == '__main__':
    # Check for API key
    if not os.getenv('GOOGLE_GENERATIVE_AI_API_KEY'):
        print("Error: GOOGLE_GENERATIVE_AI_API_KEY not set!")
        print("Please set it in your .env file or environment variables.")
        exit(1)

    # Run all examples
    run_all_examples()
