from typing import TypedDict ,Annotated
from langgraph.graph import add_messages
from pydantic import BaseModel
from langchain_core.messages import BaseMessage ,HumanMessage




class Sates(TypedDict):

    message : Annotated[list[BaseMessage],add_messages]