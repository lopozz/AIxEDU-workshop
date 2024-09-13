import os
import sys
import yaml
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain.chat_models import ChatOpenAI
from src.utils import *

# Custom class to log both to console and a file
class Tee:
    def __init__(self, file_path):
        self.console = sys.stdout  # Keep reference to the original stdout
        self.file = open(file_path, 'w')  # Open a file to write the output
    
    def write(self, message):
        self.console.write(message)  # Write to console
        self.file.write(message)  # Write to file
    
    def flush(self):
        self.console.flush()
        self.file.flush()

FILE = 'tpo_26-conversation_1_1_25'
os.makedirs(f'output/{FILE}', exist_ok=True)


# Redirect stdout and stderr to capture both to console and file
sys.stdout = Tee('output.log')
sys.stderr = sys.stdout  # Also redirect stderr


os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'

agents_config = 'src/config/agents.yaml'
tasks_config = 'src/config/tasks.yaml'

with open(agents_config, 'r') as file:
    try:
        agents_config = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        print(f"Error reading YAML file: {exc}")

with open(tasks_config, 'r') as file:
    try:
        tasks_config = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        print(f"Error reading YAML file: {exc}")


# Define your agents with roles and goals
answer_analysis_expert = Agent(
    config=agents_config['answer_analysis_expert'],
    allow_delegation=False,
    verbose=True
)

student_mind_reader = Agent(
    config=agents_config['student_mind_reader'],
    allow_delegation=False,
    verbose=True
)

student_feedback_specialist = Agent(
    config=agents_config['student_feedback_specialist'],
    allow_delegation=False,
    verbose=True
)

# Create tasks for your agents
answer_analysis_task = Task(
  config=tasks_config['answer_analysis_task'],
  agent=answer_analysis_expert,
  output_file=f'output/{FILE}/1_answer_analysis_task.md'
)

student_mind_reader_task = Task(
    config=tasks_config['student_mind_reader_task'],
    agent=student_mind_reader,
    context=[answer_analysis_task],
    output_file=f'output/{FILE}/2_student_mind_reader_task.md'
)

student_feedback_task = Task(
    config=tasks_config['student_feedback_task'],
    agent=student_feedback_specialist,
    context=[student_mind_reader_task, answer_analysis_task],
    output_file=f'output/{FILE}/3_student_feedback_task.md'
)


crew = Crew(
  agents=[answer_analysis_expert, 
          student_mind_reader, 
          student_feedback_specialist],
  tasks=[answer_analysis_task, 
         student_mind_reader_task,
         student_feedback_task],
  verbose=True,
  process = Process.sequential
)

file_path = f'src/data/{FILE}'
organized_data = read_and_replace_text_file(file_path)

inputs = {
    "question" : organized_data['question'],
    "context" : organized_data['dialogue'],
    "correct_answer" : organized_data['correct_answer'],
    "incorrect_answer" : organized_data['incorrect_answer'],
    "language" : 'italian',
}

# Get your crew to work!
result = crew.kickoff(inputs=inputs)

sys.stdout.file.close()

with open('output.log', 'r', encoding='utf-8') as file:
    log_content = file.read()

result = extract_student_mind_reader_output(log_content)
add_to_markdown_file(result, f"output/{FILE}/2_student_mind_reader_task.md")

print(organized_data['dialogue'])