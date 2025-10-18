# feedback_generator.py
"""
Badminton Form Feedback Generator using KronosLabs LLM
Provides injury risk assessment and corrective tips
"""

import json
import os
from typing import Dict, Any
from kronoslabs import KronosLabs


def generate_badminton_feedback(analysis_output: str, api_key: str = None) -> Dict[str, Any]:
    """
    Generate personalized badminton feedback using LLM
    
    Args:
        analysis_output (str): The raw analysis output from your comparison method
        api_key (str): KronosLabs API key (optional, will use env var if not provided)
    
    Returns:
        dict: Structured feedback with score, injury_risk, and tips
    """
    
    # Get API key from parameter or environment variable
    if api_key is None:
        api_key = os.getenv('KRONOS_API_KEY')
        if not api_key:
            raise ValueError("API key must be provided or set in KRONOS_API_KEY environment variable")
    
    client = KronosLabs(api_key=api_key)
    
    prompt = f"""You are an expert badminton coach and sports physiotherapist specializing in injury prevention. 
Analyze this badminton smash form comparison data and provide detailed feedback:

{analysis_output}

Based on this analysis, provide:

1. OVERALL PERFORMANCE SCORE (0-100):
   - Consider technique accuracy, injury risk, and power generation
   - Deduct points for form issues that increase injury risk
   - Award points for good mechanics

2. INJURY RISK ASSESSMENT:
   - Rate as: LOW, MODERATE, or HIGH
   - Focus especially on shoulder injury risk (most common in badminton)
   - Consider joint angles, extension, and body mechanics

3. SPECIFIC CORRECTIVE TIPS:
   - For each major issue identified, provide:
     * What's wrong and why it matters
     * How to fix it with specific drills/exercises
     * Why this correction prevents injury
   - Prioritize issues by injury risk (shoulder issues first)

4. POSITIVE REINFORCEMENT:
   - Note what they're doing well
   - Encourage continued practice

Format your response as JSON:
{{
  "overall_score": <number 0-100>,
  "injury_risk": "<LOW|MODERATE|HIGH>",
  "injury_risk_explanation": "<brief explanation of main injury concerns>",
  "critical_issues": [
    {{
      "body_part": "<shoulder/elbow/wrist/hip>",
      "problem": "<what's wrong>",
      "injury_risk": "<why this causes injury>",
      "correction": "<specific fix>",
      "drill": "<practice drill to improve>"
    }}
  ],
  "positive_feedback": "<what they're doing well>",
  "summary": "<2-3 sentence overall assessment>"
}}

Be encouraging but honest. Focus on injury prevention and safe technique improvement."""

    try:
        response = client.chat.completions.create(
            prompt=prompt,
            model="hermes",
            temperature=0.7,
            is_stream=False
        )
        
        feedback_text = response.choices[0].message.content
        
        # Try to parse JSON response
        # Extract JSON from response (in case there's additional text)
        start_idx = feedback_text.find('{')
        end_idx = feedback_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = feedback_text[start_idx:end_idx]
            feedback_data = json.loads(json_str)
        else:
            # Fallback if JSON parsing fails
            feedback_data = {
                "overall_score": 70,
                "injury_risk": "MODERATE",
                "injury_risk_explanation": "Analysis completed but formatting failed",
                "critical_issues": [],
                "positive_feedback": "Keep practicing!",
                "summary": feedback_text
            }
        
        return feedback_data
        
    except Exception as e:
        print(f"Error generating feedback: {e}")
        return {
            "overall_score": 0,
            "injury_risk": "UNKNOWN",
            "injury_risk_explanation": f"Error: {str(e)}",
            "critical_issues": [],
            "positive_feedback": "",
            "summary": "Unable to generate feedback. Please try again."
        }


def format_feedback_for_display(feedback: Dict[str, Any]) -> str:
    """
    Format the feedback dictionary into a readable string
    
    Args:
        feedback (dict): Feedback dictionary from generate_badminton_feedback
    
    Returns:
        str: Formatted feedback text
    """
    output = []
    output.append("=" * 60)
    output.append("BADMINTON FORM FEEDBACK")
    output.append("=" * 60)
    
    output.append(f"\n⭐ Overall Score: {feedback['overall_score']}/100")
    output.append(f"🏥 Injury Risk: {feedback['injury_risk']}")
    output.append(f"\n📋 Risk Explanation:\n   {feedback['injury_risk_explanation']}")
    
    output.append(f"\n📝 Summary:\n   {feedback['summary']}")
    
    if feedback['positive_feedback']:
        output.append(f"\n✅ What You're Doing Well:\n   {feedback['positive_feedback']}")
    
    if feedback['critical_issues']:
        output.append("\n" + "=" * 60)
        output.append("⚠️  AREAS FOR IMPROVEMENT")
        output.append("=" * 60)
        
        for i, issue in enumerate(feedback['critical_issues'], 1):
            output.append(f"\n{i}. {issue['body_part'].upper()}")
            output.append(f"   ❌ Problem: {issue['problem']}")
            output.append(f"   🏥 Injury Risk: {issue['injury_risk']}")
            output.append(f"   ✅ Correction: {issue['correction']}")
            output.append(f"   💪 Drill: {issue['drill']}")
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)


def save_feedback_to_file(feedback: Dict[str, Any], filename: str = "feedback_report.json"):
    """
    Save feedback to a JSON file
    
    Args:
        feedback (dict): Feedback dictionary
        filename (str): Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)
    print(f"Feedback saved to {filename}")


# Example usage and testing
if __name__ == "__main__":
    # Example analysis output (you would get this from your form analysis)
    analysis_text = """
IMPACT POINT ANALYSIS
============================================================
User impact at frame: 129.0
Reference impact at frame: 49.0

============================================================
BADMINTON SMASH FORM ANALYSIS
============================================================

📐 ELBOW ANGLE AT IMPACT:
   Your angle: 159.1°
   Reference: 174.9°
   Difference: -15.8°
   ⚠️  Your elbow is too bent. Extend more at contact for maximum reach
       and racket head speed.

💪 SHOULDER ANGLE AT IMPACT:
   Your angle: 81.3°
   Reference: 23.1°
   Difference: +58.2°
   ⚠️  Your shoulder is over-rotated. This may cause loss of control.

🎯 CONTACT POINT HEIGHT:
   Your height: -0.100
   Reference: -0.149
   Difference: -0.058
   ⚠️  Reach higher! Full arm extension maximizes racket head speed.

⭐ OVERALL FORM SCORE: 45/100
   💪 Keep practicing! Focus on the key areas mentioned above.
"""
    
    # Your API key (consider using environment variable in production)
    api_key = "kl_8de5d1021ab88d725db4426791bcd805cf189a467e0465488a0567c0647b64bb"
    
    # Or use environment variable:
    # os.environ['KRONOS_API_KEY'] = "your_api_key"
    # api_key = None  # Will use env var
    
    print("Generating feedback with KronosLabs LLM...")
    print("This may take a few seconds...\n")
    
    # Generate feedback
    feedback = generate_badminton_feedback(analysis_text, api_key)
    
    # Display formatted feedback
    formatted_output = format_feedback_for_display(feedback)
    print(formatted_output)
    
    # Save to file
    save_feedback_to_file(feedback, "badminton_feedback.json")
    
    # Also save formatted text version
    with open("badminton_feedback.txt", "w", encoding="utf-8") as f:
        f.write(formatted_output)
    print("\nFormatted feedback saved to badminton_feedback.txt")