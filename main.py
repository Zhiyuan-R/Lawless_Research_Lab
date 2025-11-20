#!/usr/bin/env python3
"""
Parking Citation Appeal Assistant
Main entry point for the application.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

from parking_appeal.workflow import AppealWorkflow


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Parking Citation Appeal Assistant - AI-powered appeal generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run interactive workflow
  python main.py

  # Run with custom API key
  python main.py --api-key YOUR_API_KEY

  # Quick appeal for testing
  python main.py --quick --citation ABC123 --state CA --violation "expired meter"

Environment Variables:
  GOOGLE_GENERATIVE_AI_API_KEY    Google Generative AI API key
        """
    )

    parser.add_argument(
        '--api-key',
        help='Google Generative AI API key (or set GOOGLE_GENERATIVE_AI_API_KEY env var)'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Generate a quick basic appeal (requires --citation, --state, --violation)'
    )

    parser.add_argument(
        '--citation',
        help='Citation number (for quick mode)'
    )

    parser.add_argument(
        '--state',
        help='State code (for quick mode, e.g., CA, NY)'
    )

    parser.add_argument(
        '--violation',
        help='Violation type (for quick mode)'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = args.api_key or os.getenv('GOOGLE_GENERATIVE_AI_API_KEY')

    if not api_key:
        print("Error: API key required!")
        print("Set GOOGLE_GENERATIVE_AI_API_KEY environment variable or use --api-key")
        sys.exit(1)

    try:
        workflow = AppealWorkflow(api_key=api_key)

        if args.quick:
            # Quick mode
            if not all([args.citation, args.state, args.violation]):
                print("Error: Quick mode requires --citation, --state, and --violation")
                sys.exit(1)

            print("\n" + "="*70)
            print("QUICK APPEAL MODE")
            print("="*70 + "\n")

            appeal = workflow.quick_appeal(args.citation, args.state, args.violation)
            print(appeal)

        else:
            # Interactive mode
            workflow.run_complete_workflow()

        print("\n" + "="*70)
        print("APPEAL GENERATION COMPLETE")
        print("="*70)
        print("\nThank you for using the Parking Citation Appeal Assistant!")
        print("\nIMPORTANT NOTES:")
        print("• Review the generated appeal carefully before submitting")
        print("• Customize it with your personal details and tone")
        print("• Include all referenced evidence when submitting")
        print("• Check your jurisdiction's appeal deadline")
        print("• Keep copies of everything you submit")
        print("\nGood luck with your appeal!")

    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
