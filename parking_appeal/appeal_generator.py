"""
Core appeal generator using Google Gemini API.
"""

import os
from typing import Dict, List, Optional
import google.generativeai as genai
from .regulations import RegulationDatabase
from .appeal_strategies import AppealStrategyAnalyzer, AppealAngle


class AppealGenerator:
    """Generates parking citation appeals using AI analysis."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the appeal generator.

        Args:
            api_key: Google Generative AI API key. If not provided, will look for
                    GOOGLE_GENERATIVE_AI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set GOOGLE_GENERATIVE_AI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-exp-1206')  # Using Gemini 2.0 Pro preview

    def generate_multi_angle_appeal(
        self,
        citation_details: Dict,
        location_info: Dict,
        selected_angles: List[str],
        evidence: Dict,
    ) -> Dict[str, str]:
        """
        Generate appeals from multiple angles.

        Args:
            citation_details: Details about the citation
            location_info: City and state regulation information
            selected_angles: List of appeal angle keys to pursue
            evidence: Evidence available for the appeal

        Returns:
            Dictionary mapping angle names to generated appeal text
        """
        appeals = {}

        for angle_key in selected_angles:
            angle = AppealStrategyAnalyzer.get_angle(angle_key)
            if angle:
                appeal_text = self._generate_single_angle_appeal(
                    citation_details, location_info, angle, evidence
                )
                appeals[angle.name] = appeal_text

        return appeals

    def _generate_single_angle_appeal(
        self,
        citation_details: Dict,
        location_info: Dict,
        angle: AppealAngle,
        evidence: Dict,
    ) -> str:
        """Generate an appeal for a single angle."""

        # Build context for the AI
        prompt = self._build_appeal_prompt(citation_details, location_info, angle, evidence)

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating appeal: {str(e)}"

    def _build_appeal_prompt(
        self,
        citation_details: Dict,
        location_info: Dict,
        angle: AppealAngle,
        evidence: Dict,
    ) -> str:
        """Build the prompt for the AI model."""

        state_info = location_info.get("state", {})
        city_info = location_info.get("city", {})

        prompt = f"""You are an expert legal assistant specializing in parking citation appeals.
Your task is to write a compelling, professional, and legally sound appeal letter.

APPEAL STRATEGY: {angle.name}
STRATEGY DESCRIPTION: {angle.description}

CITATION DETAILS:
"""

        # Add citation information
        for key, value in citation_details.items():
            if value:
                prompt += f"- {key.replace('_', ' ').title()}: {value}\n"

        prompt += "\n\nJURISDICTION INFORMATION:\n"

        # Add jurisdiction info
        if state_info:
            prompt += f"State: {state_info.get('name', 'Unknown')}\n"
            prompt += f"Appeal Deadline: {state_info.get('statute_limitations_days', 'Unknown')} days from citation\n"
            if state_info.get('common_defenses'):
                prompt += "\nRelevant State Regulations:\n"
                for defense in state_info['common_defenses']:
                    prompt += f"- {defense}\n"

        if city_info:
            prompt += f"\nCity-Specific Information:\n"
            if city_info.get('specific_rules'):
                for rule in city_info['specific_rules']:
                    prompt += f"- {rule}\n"
            prompt += f"Online Appeal Available: {city_info.get('online_appeal', 'Unknown')}\n"

        prompt += "\n\nAVAILABLE EVIDENCE:\n"

        # Add evidence
        for key, value in evidence.items():
            if value:
                prompt += f"- {key.replace('_', ' ').title()}: {value}\n"

        prompt += f"\n\nKEY POINTS FOR THIS APPEAL ANGLE:\n"
        for point in angle.strength_indicators:
            prompt += f"- {point}\n"

        prompt += f"""

REQUIRED STRUCTURE:
1. Opening: Brief, professional greeting and statement of purpose
2. Citation Information: Reference the citation number, date, location
3. Main Argument: Present the {angle.name} case clearly and persuasively
4. Supporting Evidence: Reference all available evidence that supports this angle
5. Legal/Regulatory Basis: Cite relevant regulations from the jurisdiction
6. Conclusion: Respectful request for dismissal or reduction
7. Closing: Professional sign-off

TONE REQUIREMENTS:
- Professional and respectful
- Factual and objective
- Confident but not aggressive
- Empathetic where appropriate
- Legally informed

IMPORTANT GUIDELINES:
- Do NOT fabricate facts or evidence not provided
- Cite specific regulations when applicable
- Keep the letter concise (300-500 words ideal)
- Use formal business letter format
- Be specific about dates, times, and locations
- Request specific relief (dismissal or reduction of fine)

Generate the appeal letter now:"""

        return prompt

    def analyze_citation_strength(
        self,
        citation_details: Dict,
        location_info: Dict,
        evidence: Dict,
    ) -> Dict:
        """
        Use AI to analyze the overall strength of a potential appeal.

        Returns:
            Dictionary with analysis results
        """
        prompt = f"""You are a parking citation appeal expert. Analyze this situation and provide
a brief assessment of the likelihood of a successful appeal.

CITATION DETAILS:
{self._format_dict(citation_details)}

JURISDICTION:
{self._format_dict(location_info.get('state', {}))}

AVAILABLE EVIDENCE:
{self._format_dict(evidence)}

Provide a concise analysis including:
1. Overall appeal strength (Strong/Moderate/Weak)
2. Best appeal angles to pursue (top 2-3)
3. Key factors supporting the appeal
4. Potential weaknesses to address
5. Recommended next steps

Keep the analysis under 300 words."""

        try:
            response = self.model.generate_content(prompt)
            return {
                "success": True,
                "analysis": response.text,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def suggest_follow_up_questions(
        self,
        citation_details: Dict,
        angle: AppealAngle,
    ) -> List[str]:
        """
        Use AI to suggest additional questions that could strengthen the appeal.

        Returns:
            List of suggested questions
        """
        prompt = f"""Based on this parking citation appeal case, suggest 3-5 specific questions
that would help gather additional information to strengthen the appeal.

APPEAL ANGLE: {angle.name}
CURRENT INFORMATION:
{self._format_dict(citation_details)}

STANDARD QUESTIONS FOR THIS ANGLE:
{chr(10).join(f"- {q}" for q in angle.key_questions)}

Generate additional specific questions that:
1. Are directly relevant to this specific situation
2. Would uncover helpful evidence or details
3. Are clear and easy to answer
4. Haven't already been covered

Format: Return only the questions, one per line, numbered."""

        try:
            response = self.model.generate_content(prompt)
            # Parse the response into a list
            questions = [
                line.strip().lstrip("0123456789.-) ").strip()
                for line in response.text.split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]
            return questions[:5]  # Limit to 5 questions
        except Exception as e:
            return [f"Error generating questions: {str(e)}"]

    def _format_dict(self, data: Dict) -> str:
        """Format a dictionary for inclusion in prompts."""
        if not data:
            return "None provided"

        formatted = ""
        for key, value in data.items():
            if value:
                formatted += f"- {key.replace('_', ' ').title()}: {value}\n"
        return formatted or "None provided"

    def generate_comprehensive_appeal(
        self,
        citation_details: Dict,
        location_info: Dict,
        all_angles: List[str],
        evidence: Dict,
    ) -> str:
        """
        Generate a comprehensive appeal that incorporates multiple angles.

        This creates a single unified appeal letter that strategically combines
        the strongest arguments from multiple angles.
        """
        state_info = location_info.get("state", {})
        city_info = location_info.get("city", {})

        # Get angle details
        angle_details = [
            AppealStrategyAnalyzer.get_angle(angle_key)
            for angle_key in all_angles
            if AppealStrategyAnalyzer.get_angle(angle_key)
        ]

        prompt = f"""You are an expert legal assistant specializing in parking citation appeals.
Write a single, comprehensive appeal letter that strategically incorporates multiple strong arguments.

CITATION DETAILS:
{self._format_dict(citation_details)}

JURISDICTION:
State: {state_info.get('name', 'Unknown')}
Appeal Deadline: {state_info.get('statute_limitations_days', 'Unknown')} days
"""

        if state_info.get('common_defenses'):
            prompt += "\nRelevant Regulations:\n"
            for defense in state_info['common_defenses']:
                prompt += f"- {defense}\n"

        if city_info and city_info.get('specific_rules'):
            prompt += "\nCity-Specific Rules:\n"
            for rule in city_info['specific_rules']:
                prompt += f"- {rule}\n"

        prompt += f"\n\nAVAILABLE EVIDENCE:\n{self._format_dict(evidence)}"

        prompt += "\n\nAPPEAL ANGLES TO INCORPORATE:\n"
        for angle in angle_details:
            prompt += f"\n{angle.name}:\n"
            prompt += f"Description: {angle.description}\n"
            prompt += "Key points:\n"
            for point in angle.strength_indicators[:3]:  # Top 3 points per angle
                prompt += f"  - {point}\n"

        prompt += """

Create a single, unified appeal letter that:
1. Opens professionally with citation reference
2. Presents the strongest arguments from the available angles
3. Weaves multiple points together coherently (don't list angles separately)
4. Cites relevant regulations and laws
5. References all supporting evidence naturally
6. Maintains a respectful, professional tone throughout
7. Concludes with a clear request for relief

The letter should read as a cohesive whole, not as separate sections for each angle.
Aim for 400-600 words. Use formal business letter format."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating comprehensive appeal: {str(e)}"
