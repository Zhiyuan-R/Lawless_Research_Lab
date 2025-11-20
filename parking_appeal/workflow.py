"""
Main workflow orchestrator for the parking appeal application.
"""

import os
from datetime import datetime
from typing import Dict, Optional
from colorama import Fore, Style, init

from .questionnaire import InteractiveQuestionnaire
from .appeal_generator import AppealGenerator
from .appeal_strategies import AppealStrategyAnalyzer
from .regulations import RegulationDatabase

# Initialize colorama for cross-platform color support
init(autoreset=True)


class AppealWorkflow:
    """Orchestrates the complete parking citation appeal process."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the workflow.

        Args:
            api_key: Google Generative AI API key
        """
        self.questionnaire = InteractiveQuestionnaire()
        self.generator = AppealGenerator(api_key=api_key)
        self.all_data = {}

    def print_header(self, text: str, color=Fore.CYAN):
        """Print a formatted header."""
        print(f"\n{color}{'='*70}")
        print(f"{text.center(70)}")
        print(f"{'='*70}{Style.RESET_ALL}\n")

    def print_success(self, text: str):
        """Print success message."""
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

    def print_info(self, text: str):
        """Print info message."""
        print(f"{Fore.CYAN}ℹ {text}{Style.RESET_ALL}")

    def print_warning(self, text: str):
        """Print warning message."""
        print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

    def print_error(self, text: str):
        """Print error message."""
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

    def run_complete_workflow(self) -> Dict:
        """
        Run the complete parking appeal workflow.

        Returns:
            Dictionary containing all appeals and analysis
        """
        try:
            # Step 1: Gather information
            self.print_header("STEP 1: GATHERING INFORMATION", Fore.CYAN)
            self.all_data = self.questionnaire.run_full_questionnaire()
            self.print_success("Information gathering complete!")

            # Step 2: AI Analysis
            self.print_header("STEP 2: AI ANALYSIS", Fore.MAGENTA)
            self.print_info("Analyzing your case with AI...")

            analysis = self.generator.analyze_citation_strength(
                self.all_data['citation_details'],
                self.all_data['location_info']['regulations'],
                self.all_data['evidence']
            )

            if analysis.get('success'):
                print(f"\n{Fore.WHITE}{analysis['analysis']}{Style.RESET_ALL}")
                self.all_data['ai_analysis'] = analysis['analysis']
            else:
                self.print_warning(f"Analysis unavailable: {analysis.get('error')}")

            # Step 3: Follow-up questions (optional)
            self.print_header("STEP 3: FOLLOW-UP QUESTIONS", Fore.YELLOW)

            if self.all_data['selected_angles']:
                # Get first angle for follow-up
                first_angle_key = self.all_data['selected_angles'][0]
                first_angle = AppealStrategyAnalyzer.get_angle(first_angle_key)

                ask_followup = self.questionnaire.get_yes_no(
                    "Would you like to answer AI-generated follow-up questions to strengthen your appeal?",
                    default=True
                )

                if ask_followup and first_angle:
                    self.print_info("Generating intelligent follow-up questions...")
                    questions = self.generator.suggest_follow_up_questions(
                        self.all_data['citation_details'],
                        first_angle
                    )

                    if questions:
                        additional_info = self.questionnaire.ask_follow_up_questions(questions)
                        self.all_data['citation_details'].update(additional_info)
                        self.print_success("Follow-up questions completed!")
                    else:
                        self.print_warning("Could not generate follow-up questions.")

            # Step 4: Generate appeals
            self.print_header("STEP 4: GENERATING APPEALS", Fore.GREEN)

            generate_separate = self.questionnaire.get_yes_no(
                "Generate separate appeal letters for each angle (recommended for review)?",
                default=True
            )

            appeals = {}

            if generate_separate:
                self.print_info(f"Generating {len(self.all_data['selected_angles'])} separate appeals...")

                appeals['individual'] = self.generator.generate_multi_angle_appeal(
                    self.all_data['citation_details'],
                    self.all_data['location_info']['regulations'],
                    self.all_data['selected_angles'],
                    self.all_data['evidence']
                )

                self.print_success(f"Generated {len(appeals['individual'])} individual appeals!")

            # Always generate comprehensive appeal
            self.print_info("Generating comprehensive unified appeal...")

            appeals['comprehensive'] = self.generator.generate_comprehensive_appeal(
                self.all_data['citation_details'],
                self.all_data['location_info']['regulations'],
                self.all_data['selected_angles'],
                self.all_data['evidence']
            )

            self.print_success("Comprehensive appeal generated!")

            self.all_data['appeals'] = appeals

            # Step 5: Save and display results
            self.print_header("STEP 5: RESULTS", Fore.BLUE)

            self._display_results()
            self._save_results()

            return self.all_data

        except KeyboardInterrupt:
            self.print_warning("\n\nWorkflow interrupted by user.")
            return {}
        except Exception as e:
            self.print_error(f"An error occurred: {str(e)}")
            raise

    def _display_results(self):
        """Display the generated appeals."""
        appeals = self.all_data.get('appeals', {})

        # Display comprehensive appeal
        if 'comprehensive' in appeals:
            self.print_header("COMPREHENSIVE APPEAL LETTER", Fore.GREEN)
            print(appeals['comprehensive'])

        # Display individual appeals
        if 'individual' in appeals:
            print(f"\n{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
            self.print_info(f"Individual appeals also generated for {len(appeals['individual'])} angles")

            show_individual = self.questionnaire.get_yes_no(
                "Would you like to see the individual appeal letters?",
                default=False
            )

            if show_individual:
                for angle_name, appeal_text in appeals['individual'].items():
                    self.print_header(f"APPEAL ANGLE: {angle_name}", Fore.YELLOW)
                    print(appeal_text)

    def _save_results(self):
        """Save appeals to files."""
        save = self.questionnaire.get_yes_no(
            "\nWould you like to save the appeals to files?",
            default=True
        )

        if not save:
            return

        # Create output directory
        output_dir = "appeals"
        os.makedirs(output_dir, exist_ok=True)

        # Create filename based on citation number and date
        citation_num = self.all_data['citation_details'].get('citation_number', 'UNKNOWN')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{citation_num}_{timestamp}"

        appeals = self.all_data.get('appeals', {})

        # Save comprehensive appeal
        if 'comprehensive' in appeals:
            filename = os.path.join(output_dir, f"{base_filename}_comprehensive.txt")
            with open(filename, 'w') as f:
                f.write("PARKING CITATION APPEAL\n")
                f.write("="*70 + "\n\n")
                f.write(appeals['comprehensive'])
                f.write("\n\n" + "="*70 + "\n")
                f.write("\nGENERATED BY: Parking Citation Appeal Assistant\n")
                f.write(f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            self.print_success(f"Comprehensive appeal saved to: {filename}")

        # Save individual appeals
        if 'individual' in appeals:
            for angle_name, appeal_text in appeals['individual'].items():
                safe_angle_name = angle_name.lower().replace(" ", "_").replace("/", "_")
                filename = os.path.join(output_dir, f"{base_filename}_{safe_angle_name}.txt")

                with open(filename, 'w') as f:
                    f.write(f"PARKING CITATION APPEAL - {angle_name}\n")
                    f.write("="*70 + "\n\n")
                    f.write(appeal_text)
                    f.write("\n\n" + "="*70 + "\n")
                    f.write("\nGENERATED BY: Parking Citation Appeal Assistant\n")
                    f.write(f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            self.print_success(f"Individual appeals saved to: {output_dir}/")

        # Save analysis if available
        if 'ai_analysis' in self.all_data:
            filename = os.path.join(output_dir, f"{base_filename}_analysis.txt")
            with open(filename, 'w') as f:
                f.write("AI CASE ANALYSIS\n")
                f.write("="*70 + "\n\n")
                f.write(self.all_data['ai_analysis'])

            self.print_success(f"Case analysis saved to: {filename}")

        # Save summary
        summary_file = os.path.join(output_dir, f"{base_filename}_summary.txt")
        with open(summary_file, 'w') as f:
            f.write("APPEAL SUMMARY\n")
            f.write("="*70 + "\n\n")

            f.write("CITATION DETAILS:\n")
            for key, value in self.all_data['citation_details'].items():
                if value and not key.startswith('followup'):
                    f.write(f"  {key.replace('_', ' ').title()}: {value}\n")

            f.write("\n\nSELECTED APPEAL ANGLES:\n")
            for angle_key in self.all_data['selected_angles']:
                angle = AppealStrategyAnalyzer.get_angle(angle_key)
                if angle:
                    f.write(f"  • {angle.name}\n")

            f.write("\n\nEVIDENCE AVAILABLE:\n")
            evidence_count = sum(1 for k, v in self.all_data['evidence'].items() if v and k.startswith('has_'))
            f.write(f"  {evidence_count} types of evidence collected\n")

        self.print_success(f"Summary saved to: {summary_file}")

        self.print_info(f"\nAll files saved in the '{output_dir}' directory")

    def quick_appeal(self, citation_number: str, state: str, violation_type: str) -> str:
        """
        Generate a quick basic appeal with minimal information.

        Useful for testing or simple cases.
        """
        citation_details = {
            'citation_number': citation_number,
            'violation_type': violation_type,
            'first_violation': True,
        }

        location_info = RegulationDatabase.get_combined_info(None, state)

        # Use basic angles
        angles = ['procedural_error', 'first_time_leniency']

        appeal = self.generator.generate_comprehensive_appeal(
            citation_details,
            {'state': location_info.get('state'), 'city': None},
            angles,
            {}
        )

        return appeal
