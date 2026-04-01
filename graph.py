from langgraph.graph import StateGraph , END 
from llm import model
from state import Sates


graph = StateGraph(Sates)

result = model.invoke('hi')
print(result.content)


