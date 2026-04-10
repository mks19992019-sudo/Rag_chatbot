from langgraph.graph import StateGraph , END  ,START , MessagesState
from typing import TypedDict ,Annotated , Literal
from langgraph.graph import add_messages
from pydantic import BaseModel
from langchain_core.messages import BaseMessage ,HumanMessage ,AIMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
#from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent


load_dotenv()
apikey=os.getenv('OLLAMA_API_KEY')


# model 
model = ChatOpenAI(
    api_key=apikey,
    base_url='https://ollama.com/v1',
    model='minimax-m2.7',
)

agent =create_react_agent(
    model=model,
    tools=[],
    prompt='''You are a helpful assistant that answers questions based on the given context. If you don't know the answer, say you don't know. Always use the provided tools if they are relevant to the question.''',
)


# node
def AI_agent(State:MessagesState):
    q = State['messages']
    

    result  = agent.invoke({'messages':q})

    return {'messages' : result['messages']}

    


graph = StateGraph(MessagesState)

graph.add_node('AI_agent',AI_agent)

graph.add_edge(START,'AI_agent')

graph.add_edge('AI_agent',END)


checkpoint = MemorySaver()



work_flow = graph.compile(checkpointer=checkpoint)













