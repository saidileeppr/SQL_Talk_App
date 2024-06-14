from crewai import Agent,Task,Crew,Process
from crewai_tools import tool
from langchain_google_vertexai import ChatVertexAI
from google.cloud import bigquery

#user_prompt="What is the average salary of the employee?"
client = bigquery.Client()
@tool("list_tables_tool")
def list_tables_tool():
    """Gets the list of tables and its description from BigQuery."""
    # Function logic here
    #return ["Employees","Students"]
    return [{"table_name":"DS1.Employees","description":"Contain primary details of the Employees"},
    {"table_name":"DS1.Students","description":"Contain primary details of the Students"}]

@tool("list_table_columns_tool")
def list_table_columns_tool(table_names):
    """Gets the schema,ID and other details of each table from BigQuery."""
    out=[]
    for i in table_names:
      print(table_names)
      out.append(client.get_table(i).to_api_repr())
    return out

@tool("write_query_tool")
def write_query_tool(query):
    """Get the output of the input query."""
    job_config = bigquery.QueryJobConfig(
                        maximum_bytes_billed=100000000
                    )
    query_job = client.query(query, job_config=job_config)
    api_response = query_job.result()
    api_response = str([dict(row) for row in api_response])
    api_response = api_response.replace("\\", "").replace("\n", "")
    print(api_response)
    return api_response

table_picker_agent = Agent(
  role='Query Creator',
  goal='Write a query that can help to anser the user prompt.User Prompt:{user_prompt}',
  backstory="""You are a Query Creator that takes tables and their description to provide output required by user.""",
  tools=[list_tables_tool],  # Optional, defaults to an empty list
  llm=ChatVertexAI(model="gemini-1.5-pro-001"),
  max_iter=3,  # Optional
  verbose=True,  # Optional
  allow_delegation=True,  # Optional
)

table_picker_task = Task(
  description='Find the tables that contain data needed by user Prompt. User Prompt :{user_prompt}.',
  expected_output='A list of tables that may contain data that user wants.',
  agent=table_picker_agent,
  tools=[list_tables_tool]
)

column_picker_task = Task(
  description='Find the columns that contain data needed by user Prompt. User Prompt :{user_prompt}.',
  expected_output='A BigQuery query that gives the data that user wants',
  agent=table_picker_agent,
  tools=[list_table_columns_tool]
)
query_writer_task = Task(
  description='Format the data into a reponse that user can understand. User Prompt :{user_prompt}.',
  expected_output='Final output that user expects.',
  agent=table_picker_agent,
  tools=[write_query_tool]
)
crew=Crew(agents=[
    table_picker_agent
  ],
  tasks=[
    table_picker_task,
    column_picker_task,
    query_writer_task
  ]
)

while(user_prompt:=input("Prompt: ")):
  print(crew.kickoff({"user_prompt":user_prompt}))