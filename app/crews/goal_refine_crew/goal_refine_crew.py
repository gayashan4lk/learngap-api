from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class Proj():
	"""Proj crew"""

	def create_agents(self):
		"""Create the agents for the crew"""
		input_agent = Agent(
			role="User Input Collector",
			goal="Gather the raw textual description or wordings provided by the user.",
			backstory="You're the first point of interaction, responsible for capturing clear and complete descriptions, whether they are job postings, project outlines, or subject topics.",
			verbose=True
		)

		refining_agent = Agent(
			role="Textual Input Refiner",
			goal="Refine the textual input provided by the user, to make it clear, clean and more precise and to the point",
			backstory="You have an eye for detail and a passion for clarity. You remove spelling errors, repetitive content, and ambiguous language to produce polished input.",
			verbose=True
		)

		analysis_agent = Agent(
			role="Skill Analysis Agent",
			goal="Identify the technical and non-technical skills required from the refined textual input provided by the user.",
			backstory="With deep knowledge of the software domain, you specialize in recognizing essential tools, frameworks, methodologies, and soft skills.",
			verbose=True
		)

		validation_agent = Agent(
			role="Skill Validation Agent",
			goal="Validate the skills identified by the analysis agent, to make sure they are relevant to the user's input and requirements.",
			backstory="You meticulously cross-check the identified skills, ensuring nothing vital is missing and that all listed skills are relevant and accurate.",
			verbose=True
		)

		output_agent = Agent(
			role="Output Agent",
			goal="Generate a structured JSON output based on the validated skills, ensuring it follows the required JSON schema exactly without markdown or formatting.",
			backstory="You are a precise data formatter specializing in creating machine-readable JSON outputs that adhere strictly to the required schema. You never include markdown code block markers or other formatting in your JSON.",
			verbose=True
		)

		return [input_agent, refining_agent, analysis_agent, validation_agent, output_agent]

	def create_tasks(self, agents, description):
		"""Create the tasks for the crew"""
		input_task = Task(
			description=f"Collect and process the raw textual description provided by the user: '{description}'",
			expected_output="The complete raw description with any clarifications or structured formatting that might help in further analysis.",
			agent=agents[0]
		)

		refinement_task = Task(
			description=f"Clean and standardize the following input description: '{description}'",
			expected_output="A polished, well-structured, and refined description with clear points and organized sections.",
			agent=agents[1],
			context=[input_task]
		)

		analysis_task = Task(
			description="Identify both technical and non-technical skills from the refined description.",
			expected_output="A detailed and categorized list of all required skills, competencies, and expertise with clear organization.",
			agent=agents[2],
			context=[refinement_task]
		)

		validation_task = Task(
			description="Cross-check the extracted skills against the original description. Assign confidence ratings to each skill on a scale of 1-5, with 5 being the highest confidence.",
			expected_output="A validated, accurate, and comprehensive list of skills with confidence ratings and justification.",
			agent=agents[3],
			context=[analysis_task, refinement_task]
		)

		output_task = Task(
			description="""Format and present the validated list of skills in a valid JSON structure.
IMPORTANT: Output ONLY the raw JSON directly, with NO markdown formatting, code blocks, or backticks.
Do NOT wrap your output in ```json or ``` markers!

Use exactly this JSON schema:
{
  "position": "[Extract the position/job title from the description]",
  "description": "[Use the refined description]",
  "required_skills": {
    "technical": {
      "[category_name]": {
        "skills": [
          {
            "name": "[skill name]",
            "confidence_rating": [1-5 rating],
            "justification": "[brief justification for this skill]"
          },
          ...
        ]
      },
      ...
    },
    "non_technical": {
      "[category_name]": {
        "skills": [
          {
            "name": "[skill name]",
            "confidence_rating": [1-5 rating],
            "justification": "[brief justification for this skill]"
          },
          ...
        ]
      },
      ...
    }
  }
}

Group technical skills into logical categories (e.g., programming_languages, frameworks, databases, etc.) and similarly group non-technical skills into categories (e.g., communication_skills, project_management, etc.)

REMEMBER: Your output must be valid JSON with no additional text or formatting. Do not include markdown syntax, backticks, or code block markers.
""",
			expected_output="A perfectly formatted raw JSON object (no markdown) containing the position, description, and categorized skills with confidence ratings and justifications.",
			agent=agents[4],
			context=[validation_task, analysis_task],
			output_file='skill_analysis_result.json'
		)

		return [input_task, refinement_task, analysis_task, validation_task, output_task]

	def crew(self, inputs=None):
		"""Creates the Proj crew"""
		description = inputs.get('description', '')
		agents = self.create_agents()
		tasks = self.create_tasks(agents, description)
		
		return Crew(
			agents=agents,
			tasks=tasks,
			process=Process.sequential,
			verbose=True,
		)
