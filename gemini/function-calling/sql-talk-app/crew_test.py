from crewai import Agent,Task,Crew
from crewai_tools import tool
from langchain_google_vertexai import ChatVertexAI

user_prompt="What is the average salary of the employee?"


@tool("list_tables_tool")
def list_tables_tool():
    """Gets the list of tables and its description from BigQuery."""
    # Function logic here
    #return ["Employees","Students"]
    return [{"table_name":"Employees","description":"Contain primary details of the Employees"},
    {"table_name":"Students","description":"Contain primary details of the Students"}]

table_picker_agent = Agent(
  role='Table Picker',
  goal='Extract tables that are helful to get data required for user Prompt.',
  backstory="""You are a table picker that takes tables and their description to decide which tables are useful to get data required by user.""",
  tools=[list_tables_tool],  # Optional, defaults to an empty list
  llm=ChatVertexAI(model="gemini-1.5-pro-001"),
  max_iter=15,  # Optional
  verbose=True,  # Optional
  allow_delegation=True,  # Optional
  cache=True  # Optional
)

table_picker_task = Task(
  description='Find the tables that contain data needed by user Prompt. User Prompt :"'+user_prompt+'".',
  expected_output='A list of tables that contain data that user wants.',
  agent=table_picker_agent,
  tools=[list_tables_tool]
)

crew=Crew(agents=[
		table_picker_agent
	],
	tasks=[
		table_picker_task
	]
)

print(crew.kickoff())