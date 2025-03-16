from goal_refine_crew import GoalRefineCrew

print("Starting test")

inputs = {
    'user_name': "Diluksha Perera",
}

GoalRefineCrew().crew().kickoff(inputs=inputs)

print("Test completed")