__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st

# try:
#     import pysqlite3 as sqlite3
#     import sys
#     sys.modules["sqlite3"] = sqlite3
# except ImportError:
#    st.error("Powered by Mila")

import os
from crewai import Agent, Task, Crew
from crewai_tools import DirectoryReadTool, FileReadTool, SerperDevTool, BaseTool

# Set up API keys (replace with your actual logic or environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not set in the environment")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# st.secrets["OPENAI_API_KEY"]

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "your_serper_api_key_here")
if SERPER_API_KEY is None:
    raise ValueError("SERPER_API_KEY not set in the environment")
os.environ["SERPER_API_KEY"] = SERPER_API_KEY

os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'


# Define agents
sales_rep_agent = Agent(
    role="Sales Representative",
    goal="Identify high-value leads that match our ideal customer profile",
    backstory=(
        "As part of CrewAI's dynamic sales team, your mission is to identify potential leads "
        "by analyzing data, trends, and interactions. Your work is crucial in driving the company's growth."
    ),
    allow_delegation=False,
    verbose=True,
)

lead_sales_rep_agent = Agent(
    role="Lead Sales Representative",
    goal="Nurture leads with personalized communications",
    backstory=(
        "You are the bridge between potential clients and CrewAI's solutions. "
        "Your role involves creating engaging messages that convert interest into action."
    ),
    allow_delegation=False,
    verbose=True,
)


# Define tools
directory_read_tool = DirectoryReadTool(directory="./instructions")
file_read_tool = FileReadTool()
search_tool = SerperDevTool()


class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = "Analyzes text sentiment for positive communication."

    def _run(self, text: str) -> str:
        return "positive"


sentiment_analysis_tool = SentimentAnalysisTool()

# Define tasks
lead_profiling_task = Task(
    description=(
        "Conduct an in-depth analysis of {lead_name}, a company in the {industry} sector. "
        "Focus on key decision-makers, recent developments, and needs aligning with our offerings."
    ),
    expected_output=(
        "A detailed report on {lead_name}, including background, key personnel, milestones, and needs. "
        "Highlight areas where our solutions provide value."
    ),
    tools=[directory_read_tool, file_read_tool, search_tool],
    agent=sales_rep_agent,
)

personalized_outreach_task = Task(
    description=(
        "Using insights from the lead profiling report on {lead_name}, craft a personalized outreach campaign "
        "for {key_decision_maker}, the {position} of {lead_name}. Address their recent {milestone} and how our solutions can help."
    ),
    expected_output=(
        "A series of personalized email drafts tailored to {lead_name}, targeting {key_decision_maker}. "
        "Ensure the tone is engaging and aligned with their corporate identity."
    ),
    tools=[sentiment_analysis_tool, search_tool],
    agent=lead_sales_rep_agent,
)

# Create Crew
crew = Crew(
    agents=[sales_rep_agent, lead_sales_rep_agent],
    tasks=[lead_profiling_task, personalized_outreach_task],
    verbose=True,
    memory=True,
)

# Streamlit UI
st.title("Outreach Multi-Agent App")

# Input fields
lead_name = st.text_input("Lead Name", value="DeepLearningAI")
industry = st.text_input("Industry", value="Online Learning Platform")
key_decision_maker = st.text_input("Key Decision Maker", value="Andrew Ng")
position = st.text_input("Position", value="CEO")
milestone = st.text_input("Milestone", value="Product Launch")

if st.button("Generate Content"):
# if lead_name:
    if lead_name and industry and key_decision_maker and position and milestone:
        inputs = {
            "lead_name": lead_name,
            "industry": industry,
            "key_decision_maker": key_decision_maker,
            "position": position,
            "milestone": milestone,
        }
        try:
            result = crew.kickoff(inputs=inputs)
            print(result.raw)
        except Exception as e:
            st.error(f"An error occurred: {e}")

        st.subheader("Generated Result:")
        st.write(result.raw)
    else:
        st.error("Please enter a topic.")