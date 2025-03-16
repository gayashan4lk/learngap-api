from gap_analyse_crew import GapAnalyseCrew
import json

print("Starting test")

# Read JSON files as strings
with open("app/inputs/persona.json", "r") as persona_file:
    persona_json_str = persona_file.read()

with open("app/inputs/project.json", "r") as project_file:
    project_json_str = project_file.read()

# Pass the JSON strings directly
inputs = {
    'user_persona_reader': 'User Persona Reader',
    'software_domain_expert': 'Software Domain Expert',
    'gap_analyzer': 'Gap Analyzer',
    'persona_file_path': "app/inputs/persona.json",
    'project_file_path': "app/inputs/project.json"
}

print(f"Inputs: {inputs}")

GapAnalyseCrew().crew().kickoff(inputs=inputs)

print("Test completed")