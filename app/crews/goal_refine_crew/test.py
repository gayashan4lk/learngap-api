from goal_refine_crew import GoalRefineCrew

print("Starting test")

inputs = {
    'description': "I want to be a software solutions architect in Artificial Intelligence"
}

GoalRefineCrew().crew().kickoff(inputs=inputs)

print("Test completed")