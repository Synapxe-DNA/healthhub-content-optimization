import json
import os
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
)
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tracers.context import tracing_v2_enabled
from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["HUGGINGFACEHUB_API_TOKEN"]= os.getenv("HUGGINGFACEHUB_API_TOKEN", "")



client = Client() #LangSmith

def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    functions = [format_tool_to_openai_function(t) for t in tools]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "user",
                """You are an AI assistant, collaborating with other assistants.
                 Use the provided tools to progress towards answering the question: {tool_names}.
                 If you are unable to fully answer correctly, there is no problem, another assistant with different tools 
                 will help where you left off. 
                 If you or any of the other assistants have the final answer or deliverable, use the generated json as source of data and
                 prefix your response with FINAL ANSWER so the team knows to stop.
                 Double check the answer. Do not provide incomplete answers!
                 You have access to the following tools: Use {tool_names} to gather data.\n Use {system_message} to guide you in your task."""
            ),
            ("system","{messages}"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_functions(functions)

from typing import Annotated

from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL


# Warning: This executes code locally, which can be unsafe when not sandboxed

@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )

import operator
from typing import Annotated, Sequence, TypedDict


# This defines the object that is passed between each node
# in the graph. We will create different nodes for each agent and tool
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str