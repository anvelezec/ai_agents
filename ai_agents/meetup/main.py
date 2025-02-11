import panel as pn  # GUI
pn.extension()
import panel as pn
import param

from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents import initialize_agent, AgentType
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser, JsonKeyOutputFunctionsParser
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.utilities import SerpAPIWrapper
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
from langchain.tools import Tool
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.schema.runnable import RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser



from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

import requests
import datetime
import pytz
import math
# Load environment variables from .env file
load_dotenv()


# Define a simple calculator tool
def calculate(expression: str) -> str:
    """Evaluates a mathematical expression safely."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {"sqrt": math.sqrt}))
    except Exception as e:
        return f"Error: {str(e)}"

# Define a web search tool (Requires SerpAPI Key)
#search_tool = SerpAPIWrapper()
search_tool2 = TavilySearchResults()

# Create LangChain tools
tools = [
    Tool(name="Calculator", func=calculate, description="Performs mathematical calculations."),
    #Tool(name="Web Search", func=search_tool.run, description="Fetches the latest information from the web."),
    Tool(name="Tavily Search", func=search_tool2.run, description="Searches for the latest information on the web."),
]


import panel as pn  # GUI
pn.extension()
import panel as pn
import param

class cbfs(param.Parameterized):
    
    def __init__(self, tools, **params):
        super(cbfs, self).__init__( **params)
        self.panels = []
        self.functions = [format_tool_to_openai_function(f) for f in tools]
        self.model = ChatOpenAI(model="gpt-4o", temperature=0)
        self.qa = initialize_agent(
                                tools=tools,
                                llm=self.model,
                                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                verbose=True,
                            )

    def convchain(self, query):
        if not query:
            return
        inp.value = ''
        result = self.qa.invoke({"input": query})
        self.answer = result['output'] 
        self.panels.extend([
            pn.Row('User:', pn.pane.Markdown(query, width=450)),
            pn.Row('ChatBot:', pn.pane.Markdown(self.answer, width=450, styles={'background-color': '#F6F6F6'}))
        ])
        return pn.WidgetBox(*self.panels, scroll=True)


    def clr_history(self,count=0):
        self.chat_history = []
        return 
    

if __name__ == "__main__":
    # https://python.langchain.com/docs/versions/migrating_memory/

    cb = cbfs(tools)

    inp = pn.widgets.TextInput( placeholder='Enter text here…')

    conversation = pn.bind(cb.convchain, inp)

    tab1 = pn.Column(
        pn.Row(inp),
        pn.layout.Divider(),
        pn.panel(conversation,  loading_indicator=True, height=400),
        pn.layout.Divider(),
    )

    dashboard = pn.Column(
        pn.Row(pn.pane.Markdown('# QnA_Bot')),
        pn.Tabs(('Conversation', tab1))
    )
    dashboard.show()