"""
Interactive questionnaire for gathering citation and evidence details.
"""

from typing import Dict, List, Optional, Any
from .regulations import RegulationDatabase
from .appeal_strategies import AppealStrategyAnalyzer


class InteractiveQuestionnaire:
    """Guides users through questions to gather appeal information."""

    def __init__(self):
        self.citation_details = {}
        self.evidence = {}
        self.location_info = {}

    def get_input(self, prompt: str, required: bool = True, default: Any = None) -> str:
        """Get input from user with optional default."""
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "

        while True:
            response = input(prompt).strip()

            if response:
                return response
            elif default is not None:
                return str(default)
            elif not required:
                return ""
            else:
                print("This field is required. Please provide a value.")

    def get_yes_no(self, prompt: str, default: Optional[bool] = None) -> bool:
        """Get a yes/no response from user."""
        if default is True:
            prompt = f"{prompt} (Y/n): "
        elif default is False:
            prompt = f"{prompt} (y/N): "
        else:
            prompt = f"{prompt} (y/n): "

        while True:
            response = input(prompt).strip().lower()

            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif response == "" and default is not None:
                return default
            else:
                print("Please enter 'y' for yes or 'n' for no.")

    def select_from_list(self, prompt: str, options: List[str], allow_multiple: bool = False) -> List[str]:
        """Allow user to select from a list of options."""
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        if allow_multiple:
            print("Enter numbers separated by commas (e.g., 1,3,5) or 'all':")
        else:
            print("Enter the number of your selection:")

        while True:
            response = input("> ").strip()

            if allow_multiple and response.lower() == 'all':
                return options

            try:
                if allow_multiple:
                    indices = [int(x.strip()) - 1 for x in response.split(',')]
                else:
                    indices = [int(response) - 1]

                selected = [options[i] for i in indices if 0 <= i < len(options)]

                if selected:
                    return selected
                else:
                    print("Invalid selection. Please try again.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter valid numbers.")

    def gather_basic_citation_info(self) -> Dict:
        """Gather basic citation information."""
        print("\n" + "="*60)
        print("PARKING CITATION APPEAL - BASIC INFORMATION")
        print("="*60)

        self.citation_details['citation_number'] = self.get_input("Citation Number")
        self.citation_details['citation_date'] = self.get_input("Citation Date (MM/DD/YYYY)")
        self.citation_details['citation_time'] = self.get_input("Citation Time (HH:MM AM/PM)", required=False)
        self.citation_details['location'] = self.get_input("Location (Street Address)")
        self.citation_details['violation_type'] = self.get_input("Violation Type (e.g., 'expired meter', 'no parking zone')")
        self.citation_details['fine_amount'] = self.get_input("Fine Amount ($)", required=False)

        return self.citation_details

    def gather_location_info(self) -> Dict:
        """Gather location/jurisdiction information."""
        print("\n" + "="*60)
        print("JURISDICTION INFORMATION")
        print("="*60)

        # Get state
        available_states = RegulationDatabase.get_all_states()
        print(f"\nSupported states: {', '.join(available_states)}")
        state = self.get_input("State (2-letter code, e.g., CA, NY, TX)").upper()

        # Validate state or accept anyway
        if state not in available_states:
            print(f"Note: {state} is not in our database of detailed regulations.")
            print("We'll still help you, but may have limited jurisdiction-specific information.")

        self.location_info['state'] = state

        # Get city
        cities = RegulationDatabase.get_cities_for_state(state)
        if cities:
            print(f"\nCities with detailed information: {', '.join(cities)}")

        city = self.get_input("City", required=False)
        if city:
            self.location_info['city'] = city

        # Get combined info
        combined_info = RegulationDatabase.get_combined_info(city, state)
        self.location_info['regulations'] = combined_info

        return self.location_info

    def gather_vehicle_info(self) -> None:
        """Gather vehicle information."""
        print("\n" + "="*60)
        print("VEHICLE INFORMATION")
        print("="*60)

        self.citation_details['vehicle_make'] = self.get_input("Vehicle Make", required=False)
        self.citation_details['vehicle_model'] = self.get_input("Vehicle Model", required=False)
        self.citation_details['vehicle_color'] = self.get_input("Vehicle Color", required=False)
        self.citation_details['license_plate'] = self.get_input("License Plate", required=False)

        # Check if citation has correct vehicle info
        has_error = self.get_yes_no("Does the citation have incorrect vehicle information?", default=False)
        self.citation_details['incorrect_vehicle_info'] = has_error

    def gather_situation_details(self) -> None:
        """Gather details about the parking situation."""
        print("\n" + "="*60)
        print("SITUATION DETAILS")
        print("="*60)

        # Key yes/no questions that help identify appeal angles
        self.citation_details['first_violation'] = self.get_yes_no(
            "Is this your first parking violation in this jurisdiction?",
            default=None
        )

        self.citation_details['unclear_signage'] = self.get_yes_no(
            "Were the parking restriction signs unclear, missing, or confusing?",
            default=None
        )

        self.citation_details['paid_for_parking'] = self.get_yes_no(
            "Did you pay for parking?",
            default=None
        )

        if self.citation_details['paid_for_parking']:
            self.citation_details['payment_method'] = self.get_input(
                "Payment method (meter, app, etc.)",
                required=False
            )
            self.citation_details['paid_not_displayed'] = self.get_yes_no(
                "Was the receipt not visible/displayed properly?",
                default=False
            )

        self.citation_details['meter_malfunction'] = self.get_yes_no(
            "Was there a meter malfunction or payment system issue?",
            default=False
        )

        self.citation_details['emergency_situation'] = self.get_yes_no(
            "Was this due to an emergency situation?",
            default=False
        )

        if self.citation_details['emergency_situation']:
            self.citation_details['emergency_description'] = self.get_input(
                "Brief description of emergency",
                required=False
            )

        self.citation_details['time_incorrect'] = self.get_yes_no(
            "Is the citation time incorrect or implausible?",
            default=False
        )

        self.citation_details['has_disability_placard'] = self.get_yes_no(
            "Do you have a disability placard/plate?",
            default=False
        )

    def gather_evidence_details(self) -> Dict:
        """Gather information about available evidence."""
        print("\n" + "="*60)
        print("AVAILABLE EVIDENCE")
        print("="*60)

        print("\nWhat evidence do you have? (This helps strengthen your appeal)")

        evidence_types = [
            "Photos of parking location and signage",
            "Photos of the citation itself",
            "Parking receipt or payment confirmation",
            "Photos of meter (showing malfunction, etc.)",
            "Credit card/bank statement showing payment",
            "Medical documentation (for emergency)",
            "Police report",
            "Witness statements",
            "Vehicle registration documents",
            "GPS or location data",
            "Other documentation",
        ]

        has_evidence = self.get_yes_no("Do you have any evidence to support your appeal?", default=True)

        if has_evidence:
            selected = self.select_from_list(
                "Select all evidence you have:",
                evidence_types,
                allow_multiple=True
            )

            for evidence_type in selected:
                key = evidence_type.lower().replace(" ", "_").replace("/", "_")
                self.evidence[f"has_{key}"] = True

                # Ask for details
                details = self.get_input(
                    f"Brief description of {evidence_type.lower()}",
                    required=False
                )
                if details:
                    self.evidence[f"{key}_details"] = details

        # Additional narrative
        additional_info = self.get_input(
            "\nAny additional relevant information?",
            required=False
        )
        if additional_info:
            self.citation_details['additional_info'] = additional_info

        return self.evidence

    def identify_appeal_angles(self) -> List[str]:
        """Analyze gathered information to identify viable appeal angles."""
        print("\n" + "="*60)
        print("ANALYZING YOUR SITUATION...")
        print("="*60)

        # Use the strategy analyzer to identify relevant angles
        suggested_angles = AppealStrategyAnalyzer.analyze_situation(self.citation_details)

        print(f"\nBased on your situation, we've identified {len(suggested_angles)} potential appeal angles:")

        angle_objects = []
        for angle_key in suggested_angles:
            angle = AppealStrategyAnalyzer.get_angle(angle_key)
            if angle:
                angle_objects.append((angle_key, angle))
                strength = AppealStrategyAnalyzer.get_angle_strength(angle_key, self.evidence)
                print(f"\n  • {angle.name} ({strength.upper()} case)")
                print(f"    {angle.description}")

        # Let user select which angles to pursue
        print("\n" + "-"*60)
        use_all = self.get_yes_no(
            "Would you like to pursue all suggested angles?",
            default=True
        )

        if use_all:
            return suggested_angles
        else:
            angle_names = [angle.name for _, angle in angle_objects]
            selected_names = self.select_from_list(
                "Select which angles to pursue:",
                angle_names,
                allow_multiple=True
            )

            # Map names back to keys
            name_to_key = {angle.name: key for key, angle in angle_objects}
            return [name_to_key[name] for name in selected_names if name in name_to_key]

    def run_full_questionnaire(self) -> Dict:
        """Run the complete questionnaire and return all gathered information."""
        print("\n" + "="*70)
        print(" "*15 + "PARKING CITATION APPEAL ASSISTANT")
        print("="*70)
        print("\nThis tool will help you build a strong appeal for your parking citation.")
        print("Please answer the following questions as accurately as possible.")
        print("The more details you provide, the better we can help.")

        # Gather all information
        self.gather_basic_citation_info()
        self.gather_location_info()
        self.gather_vehicle_info()
        self.gather_situation_details()
        self.gather_evidence_details()

        # Identify angles
        selected_angles = self.identify_appeal_angles()

        # Return everything
        return {
            'citation_details': self.citation_details,
            'location_info': self.location_info,
            'evidence': self.evidence,
            'selected_angles': selected_angles,
        }

    def ask_follow_up_questions(self, questions: List[str]) -> Dict:
        """Ask AI-generated follow-up questions."""
        print("\n" + "="*60)
        print("FOLLOW-UP QUESTIONS")
        print("="*60)
        print("\nTo strengthen your appeal, please answer these additional questions:")

        additional_info = {}

        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question}")
            answer = self.get_input("Your answer", required=False)
            if answer:
                additional_info[f"followup_q{i}"] = {
                    'question': question,
                    'answer': answer
                }

        return additional_info
