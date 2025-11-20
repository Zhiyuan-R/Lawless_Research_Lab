# Parking Citation Appeal Assistant

An AI-powered tool that helps you generate compelling parking citation appeals using Google's Gemini API. The application analyzes your situation from multiple angles and generates professional, legally-informed appeal letters tailored to your specific jurisdiction.

## Features

- **Multi-Angle Appeal Analysis**: Identifies and pursues multiple appeal strategies including:
  - Procedural errors
  - Inadequate signage
  - Meter malfunctions
  - Emergency circumstances
  - Payment display issues
  - Time discrepancies
  - First-time leniency
  - Disability accommodations
  - Zone confusion

- **Jurisdiction-Aware**: Adapts to different cities and states with specific regulations for:
  - California (San Francisco, Los Angeles)
  - New York (New York City)
  - Texas (Houston)
  - Florida (Miami)
  - Illinois (Chicago)
  - And more...

- **AI-Powered Intelligence**:
  - Uses Gemini 2.0 Pro for sophisticated appeal generation
  - Analyzes case strength
  - Suggests follow-up questions
  - Generates both individual and comprehensive appeals

- **Interactive Workflow**:
  - Step-by-step questionnaire
  - Evidence gathering
  - Multiple appeal generation options
  - Automatic file saving

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Lawless_Research_Lab
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:

Create a `.env` file in the project root:
```bash
GOOGLE_GENERATIVE_AI_API_KEY=your_api_key_here
```

Or export it as an environment variable:
```bash
export GOOGLE_GENERATIVE_AI_API_KEY=your_api_key_here
```

## Usage

### Interactive Mode (Recommended)

Run the interactive workflow that guides you through the complete process:

```bash
python main.py
```

This will:
1. Gather citation details through an interactive questionnaire
2. Analyze your case with AI
3. Identify the strongest appeal angles
4. Ask intelligent follow-up questions
5. Generate comprehensive appeal letters
6. Save everything to files

### Web Interface (NEW!)

Launch the web application for a user-friendly browser experience:

```bash
cd web
python app.py
```

Then open your browser to `http://localhost:5000`

Features:
- Modern, responsive design
- Interactive form with real-time validation
- AI-powered appeal generation
- Copy-to-clipboard functionality
- Beautiful landing page with feature showcase

See `web/README.md` for detailed documentation.

### Quick Mode

For simple appeals or testing:

```bash
python main.py --quick --citation ABC123 --state CA --violation "expired meter"
```

### With Custom API Key

```bash
python main.py --api-key YOUR_API_KEY
```

## Workflow Overview

The application follows a clear 5-step workflow:

### Step 1: Gathering Information
- Citation details (number, date, location, violation type)
- Jurisdiction information (city, state)
- Vehicle information
- Situation details (signage, payment, emergencies)
- Available evidence

### Step 2: AI Analysis
- Analyzes overall appeal strength
- Identifies key factors supporting your case
- Highlights potential weaknesses
- Recommends next steps

### Step 3: Follow-Up Questions
- AI generates intelligent follow-up questions
- Helps uncover additional supporting details
- Strengthens specific appeal angles

### Step 4: Appeal Generation
- Generates individual appeals for each angle
- Creates a comprehensive unified appeal
- Incorporates jurisdiction-specific regulations
- References all available evidence

### Step 5: Results & Saving
- Displays generated appeals
- Saves to organized files
- Creates summary and analysis documents

## Appeal Angles Explained

### Procedural Error
Citations issued with errors in vehicle information, missing details, or improper procedures.

**Evidence needed**: Photos of citation showing errors, vehicle registration

### Inadequate Signage
Parking restrictions not clearly posted or signs were confusing/obstructed.

**Evidence needed**: Photos of parking spot and signage from multiple angles

### Meter Malfunction
Parking meter or payment system was not functioning properly.

**Evidence needed**: Photos of meter, payment receipts, transaction records

### Emergency Circumstances
Violation occurred due to medical emergency, vehicle breakdown, or safety concern.

**Evidence needed**: Medical records, police report, mechanic documentation

### Payment Display Issue
Valid payment was made but receipt was not properly displayed.

**Evidence needed**: Parking receipt, payment confirmation, timestamps

### Time Discrepancy
Citation time is incorrect or conflicts with actual events.

**Evidence needed**: Timestamped photos, receipts, GPS/location data

### First-Time Leniency
Request for reduced penalty based on clean parking record.

**Evidence needed**: Driving record, proof of good compliance history

### Disability Accommodation
Issues related to disability parking or accommodation needs.

**Evidence needed**: Disability placard documentation, medical records

### Zone Confusion
Zone boundaries or time restrictions were unclear or ambiguous.

**Evidence needed**: Photos of zone markings, signage, official parking maps

## Output Files

Appeals are saved in the `appeals/` directory with the following structure:

```
appeals/
├── ABC123_20240115_120000_comprehensive.txt    # Main unified appeal
├── ABC123_20240115_120000_procedural_error.txt # Individual angle appeals
├── ABC123_20240115_120000_signage_issues.txt
├── ABC123_20240115_120000_analysis.txt         # AI case analysis
└── ABC123_20240115_120000_summary.txt          # Case summary
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_regulations.py

# Run with coverage
python -m pytest --cov=parking_appeal tests/
```

Or using unittest:

```bash
python -m unittest discover tests
```

### Test Coverage

The application includes comprehensive tests for:
- Regulations database (jurisdiction lookups)
- Appeal strategy analysis
- Appeal generator (with mocked API calls)
- Integration tests (requires valid API key)

## Project Structure

```
Lawless_Research_Lab/
├── parking_appeal/           # Main package
│   ├── __init__.py
│   ├── regulations.py        # City/state regulations database
│   ├── appeal_strategies.py  # Appeal angle definitions
│   ├── appeal_generator.py   # AI-powered appeal generation
│   ├── questionnaire.py      # Interactive data gathering
│   └── workflow.py           # Main workflow orchestration
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_regulations.py
│   ├── test_appeal_strategies.py
│   └── test_appeal_generator.py
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
├── .env.example             # Example environment file
└── README.md                # This file
```

## API Key

This application uses Google's Gemini 2.0 Pro (preview) model. You need a valid API key from Google AI Studio:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create or sign in to your Google account
3. Generate an API key
4. Add it to your `.env` file or environment variables

**Note**: The API key provided in the requirements should only be used for this project and should be kept secure.

## Important Legal Notice

**This tool is for informational purposes only and does not constitute legal advice.**

- Always review generated appeals carefully before submitting
- Customize the content to match your personal situation and tone
- Verify all facts and claims are accurate
- Include all referenced evidence when submitting your appeal
- Check your jurisdiction's specific appeal procedures and deadlines
- Consider consulting with a legal professional for serious or complex cases

## Tips for Success

1. **Gather Evidence**: Take comprehensive photos before leaving the parking spot
2. **Act Quickly**: Note appeal deadlines (typically 21-30 days)
3. **Be Truthful**: Only claim what you can support with evidence
4. **Be Professional**: Maintain a respectful, factual tone
5. **Follow Up**: Keep records of all submissions and communications
6. **Multiple Angles**: Don't rely on just one argument - use the comprehensive appeal
7. **Proofread**: Check for accuracy before submitting

## Supported Jurisdictions

### Detailed Support
- California: San Francisco, Los Angeles
- New York: New York City
- Texas: Houston
- Florida: Miami
- Illinois: Chicago

### Basic Support
All 50 US states with general parking law principles. The app adapts to any jurisdiction but provides enhanced guidance for the detailed jurisdictions above.

## Contributing

To add support for additional cities or states:

1. Edit `parking_appeal/regulations.py`
2. Add state to `STATE_REGULATIONS` dictionary
3. Add cities to `CITY_REGULATIONS` dictionary
4. Include specific rules, appeal processes, and deadlines

## Troubleshooting

**API Key Error**: Ensure your API key is correctly set in `.env` or environment variables

**Import Errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`

**No Appeals Generated**: Check that the API key is valid and has quota available

**File Permission Errors**: Ensure the script has write permissions for the `appeals/` directory

## Future Enhancements

- [ ] Support for more cities and states
- [ ] Photo upload and analysis
- [ ] Direct integration with city appeal portals
- [ ] Success rate tracking
- [ ] Template customization
- [ ] Multi-language support

## License

This project is provided as-is for educational and informational purposes.

## Contact

For issues, questions, or contributions, please create an issue in the repository.

---

**Good luck with your parking citation appeal!**
