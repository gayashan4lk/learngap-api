from gap_analyse_crew import GapAnalyseCrew

print("Starting test")

inputs = {
    'persona': "app/inputs/persona.json",
    'project': "app/inputs/project.json"
}

GapAnalyseCrew().crew().kickoff(inputs=inputs)

print("Test completed")