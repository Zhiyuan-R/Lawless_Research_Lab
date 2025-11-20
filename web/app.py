"""
Flask web application for the Parking Citation Appeal Assistant.
"""

import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parking_appeal.appeal_generator import AppealGenerator
from parking_appeal.regulations import RegulationDatabase
from parking_appeal.appeal_strategies import AppealStrategyAnalyzer

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@app.route('/api/states')
def get_states():
    """Get list of supported states."""
    states = RegulationDatabase.get_all_states()
    state_info = {}
    for state_code in states:
        info = RegulationDatabase.get_state_info(state_code)
        state_info[state_code] = {
            'code': state_code,
            'name': info['name']
        }
    return jsonify(state_info)


@app.route('/api/cities/<state>')
def get_cities(state):
    """Get cities for a specific state."""
    cities = RegulationDatabase.get_cities_for_state(state)
    return jsonify(cities)


@app.route('/api/appeal-angles')
def get_appeal_angles():
    """Get all available appeal angles."""
    angles = AppealStrategyAnalyzer.get_all_angles()
    angle_list = []
    for key, angle in angles.items():
        angle_list.append({
            'key': key,
            'name': angle.name,
            'description': angle.description
        })
    return jsonify(angle_list)


@app.route('/api/analyze', methods=['POST'])
def analyze_citation():
    """Analyze citation and suggest appeal angles."""
    data = request.json

    citation_details = {
        'citation_number': data.get('citation_number'),
        'violation_type': data.get('violation_type'),
        'unclear_signage': data.get('unclear_signage', False),
        'meter_malfunction': data.get('meter_malfunction', False),
        'emergency_situation': data.get('emergency_situation', False),
        'paid_for_parking': data.get('paid_for_parking', False),
        'paid_not_displayed': data.get('paid_not_displayed', False),
        'first_violation': data.get('first_violation', False),
        'time_incorrect': data.get('time_incorrect', False),
        'has_disability_placard': data.get('has_disability_placard', False),
        'incorrect_vehicle_info': data.get('incorrect_vehicle_info', False),
    }

    # Analyze situation
    suggested_angles = AppealStrategyAnalyzer.analyze_situation(citation_details)

    # Get details for each angle
    angle_details = []
    for angle_key in suggested_angles:
        angle = AppealStrategyAnalyzer.get_angle(angle_key)
        if angle:
            angle_details.append({
                'key': angle_key,
                'name': angle.name,
                'description': angle.description,
                'questions': angle.key_questions[:3]
            })

    return jsonify({
        'success': True,
        'suggested_angles': angle_details
    })


@app.route('/api/generate-appeal', methods=['POST'])
def generate_appeal():
    """Generate parking citation appeal."""
    try:
        data = request.json

        # Check for API key
        api_key = os.getenv('GOOGLE_GENERATIVE_AI_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 400

        # Create generator
        generator = AppealGenerator(api_key=api_key)

        # Build citation details
        citation_details = {
            'citation_number': data.get('citation_number'),
            'citation_date': data.get('citation_date'),
            'citation_time': data.get('citation_time'),
            'location': data.get('location'),
            'violation_type': data.get('violation_type'),
            'fine_amount': data.get('fine_amount'),
            'first_violation': data.get('first_violation', False),
            'unclear_signage': data.get('unclear_signage', False),
            'meter_malfunction': data.get('meter_malfunction', False),
            'emergency_situation': data.get('emergency_situation', False),
            'emergency_description': data.get('emergency_description'),
            'paid_for_parking': data.get('paid_for_parking', False),
            'paid_not_displayed': data.get('paid_not_displayed', False),
            'time_incorrect': data.get('time_incorrect', False),
            'has_disability_placard': data.get('has_disability_placard', False),
            'additional_info': data.get('additional_info'),
        }

        # Get jurisdiction info
        state = data.get('state')
        city = data.get('city')
        location_info = RegulationDatabase.get_combined_info(city, state)

        # Get selected angles or analyze
        selected_angles = data.get('selected_angles')
        if not selected_angles:
            selected_angles = AppealStrategyAnalyzer.analyze_situation(citation_details)

        # Build evidence dict
        evidence = {}
        evidence_items = data.get('evidence', [])
        for item in evidence_items:
            evidence[f'has_{item.lower().replace(" ", "_")}'] = True

        # Add evidence descriptions
        if data.get('evidence_description'):
            evidence['general_description'] = data.get('evidence_description')

        # Generate comprehensive appeal
        appeal_text = generator.generate_comprehensive_appeal(
            citation_details,
            {'state': location_info.get('state'), 'city': location_info.get('city')},
            selected_angles,
            evidence
        )

        # Get AI analysis if requested
        analysis_text = None
        if data.get('include_analysis', True):
            analysis = generator.analyze_citation_strength(
                citation_details,
                location_info,
                evidence
            )
            if analysis.get('success'):
                analysis_text = analysis['analysis']

        return jsonify({
            'success': True,
            'appeal': appeal_text,
            'analysis': analysis_text,
            'angles_used': [
                AppealStrategyAnalyzer.get_angle(key).name
                for key in selected_angles
                if AppealStrategyAnalyzer.get_angle(key)
            ]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/form')
def appeal_form():
    """Appeal form page."""
    return render_template('form.html')


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


if __name__ == '__main__':
    # Check for API key
    if not os.getenv('GOOGLE_GENERATIVE_AI_API_KEY'):
        print("WARNING: GOOGLE_GENERATIVE_AI_API_KEY not set!")
        print("The app will run but appeal generation will fail.")

    app.run(debug=True, host='0.0.0.0', port=5000)
