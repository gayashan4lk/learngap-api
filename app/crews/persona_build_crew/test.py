from persona_build_crew import PersonaBuildCrew

print("Starting test")

inputs = {
    'user_name': "Diluksha Perera",
    'email': "dilukshakaushal@gmail.com",
    'educational_background': "KDU BS in Data science",'professional_background': "data Engineer at bistec",
    'skills': "Python, SQL",
    'linkedin': "https://www.linkedin.com/in/DilukshaPerera",
    'github': "https://github.com/johndoe",
    'medium': "https://medium.com/@johndoe"
}
print(f"inputs: {inputs}")

PersonaBuildCrew().crew().kickoff(inputs=inputs)

print("Test completed")