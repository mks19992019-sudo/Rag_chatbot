import atexit
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import create_react_agent
from psycopg_pool import ConnectionPool


load_dotenv()

model = ChatGroq(model="openai/gpt-oss-120b")

agent = create_react_agent(
    model=model,
    tools=[],
    prompt=(
        "You are a helpful assistant that answers questions based on the given "
        "context. If you don't know the answer, say you don't know. Always use "
        "the provided tools if they are relevant to the question."
    ),
)


def AI_agent(state: MessagesState):
    result = agent.invoke({"messages": state["messages"]})

    return {"messages": result["messages"]}


graph = StateGraph(MessagesState)

graph.add_node("AI_agent", AI_agent)
graph.add_edge(START, "AI_agent")
graph.add_edge("AI_agent", END)


DB_URI = os.getenv("DB_URI", "postgresql://postgres:postgres@localhost:5442/postgres")

connection_pool = ConnectionPool(
    conninfo=DB_URI,
    min_size=1,
    max_size=5,
    open=True,
    kwargs={"autocommit": True, "prepare_threshold": 0},
)
# for closing the conection
atexit.register(connection_pool.close)

checkpointer = PostgresSaver(connection_pool)

checkpointer.setup()

work_flow = graph.compile(checkpointer=checkpointer)












