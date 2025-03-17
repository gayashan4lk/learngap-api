import sys
import warnings
import json
import os
from datetime import datetime
from pathlib import Path

from curriculum_build_crew import CurriculumBuilderCrew

print("Starting test")

def ensure_input_dir():
    """
    Ensure the input directory exists.
    """
    input_dir = Path("../inputs")
    input_dir.mkdir(exist_ok=True)
    return input_dir

def save_json_input(json_data, filename="skill_input.json"):
    """
    Save input JSON data to a file in the input directory.
    """
    input_dir = ensure_input_dir()
    input_file = input_dir / filename
    
    with open(input_file, "w") as f:
        json.dump(json_data, f, indent=2)
    
    return input_file

def get_skill_from_json(json_data):
    """
    Extract the primary skill to focus on from the JSON data.
    """
    # Check for high priority missing technical skills first
    missing_technical = json_data.get("skill_gaps", {}).get("missing", {}).get("Technical", [])
    if missing_technical:
        # Get the first high priority skill
        for skill_item in missing_technical:
            if skill_item.get("priority") == "High":
                return skill_item.get("skill")
    
    # If no high priority missing technical skills, check other categories
    return "Web3 Development"  # Default fallback if no clear primary skill is found

json_file_path = Path("paste.txt")

if json_file_path.exists():
    try:
        with open(json_file_path, "r") as f:
            content = f.read()
            # Try to parse as JSON first
            try:
                json_data = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, check if it's the output curriculum
                if "Curriculum" in content and "Level" in content:
                    print("Found curriculum output in paste.txt. This should be used as output, not input.")
                    # Use default sample data
                    json_data = {
                        "skill_gaps": {
                            "missing": {
                                "Technical": [
                                    {
                                        "skill": "Web3 Development",
                                        "priority": "High",
                                        "justification": "Critical for developing decentralized applications",
                                        "learning_recommendations": "Enroll in online courses"
                                    }
                                ]
                            }
                        }
                    }
                else:
                    print("Could not parse paste.txt as JSON. Using default sample data.")
                    json_data = {
                        "skill_gaps": {
                            "missing": {
                                "Technical": [
                                    {
                                        "skill": "Web3 Development",
                                        "priority": "High",
                                        "justification": "Critical for developing decentralized applications",
                                        "learning_recommendations": "Enroll in online courses"
                                    }
                                ]
                            }
                        }
                    }
    except Exception as e:
        print(f"Error reading paste.txt: {e}")
        json_data = {
            "skill_gaps": {
                "missing": {
                    "Technical": [
                        {
                            "skill": "Web3 Development",
                            "priority": "High",
                            "justification": "Critical for developing decentralized applications",
                            "learning_recommendations": "Enroll in online courses"
                        }
                    ]
                }
            }
        }
else:
    # Sample data if paste.txt doesn't exist
    json_data = {
        "skill_gaps": {
            "missing": {
                "Technical": [
                    {
                        "skill": "Web3 Development",
                        "priority": "High",
                        "justification": "Critical for developing decentralized applications",
                        "learning_recommendations": "Enroll in online courses"
                    }
                ]
            }
        }
    }

# Save the input data to a file
input_file = save_json_input(json_data)
    
# Extract the primary skill to focus on
primary_skill = get_skill_from_json(json_data)

inputs = {
    'skill': primary_skill,
    'skill_data': json_data,
    'current_year': str(datetime.now().year),
    'input_file_path': str(input_file),
    'output_format': 'json'  # Specify JSON output format
}

print(f"inputs: {inputs}")

CurriculumBuilderCrew().crew().kickoff(inputs=inputs)

print("Test completed")