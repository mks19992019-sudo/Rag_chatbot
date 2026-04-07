from langgraph.graph import StateGraph , END  ,START
from typing import TypedDict ,Annotated , Literal
from langgraph.graph import add_messages
from pydantic import BaseModel
from langchain_core.messages import BaseMessage ,HumanMessage ,AIMessage

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from langgraph.checkpoint.memory import MemorySaver

load_dotenv()
apikey=os.getenv('OLLAMA_API_KEY')


# model 
model = ChatOpenAI(
    api_key=apikey,
    base_url='https://ollama.com/v1',
    model='minimax-m2.7',
)


class Sates(TypedDict):
    msg : Annotated[list[BaseMessage],add_messages] 

    
    



def AI_agent(State:Sates):
    q = State['msg']


    prompt =f'''
    anser the given question -> {q}'''

    result  = model.invoke(prompt).content



    return {'msg' : [AIMessage(content=result)]}

    
   




graph = StateGraph(Sates)


graph.add_node('AI_agent',AI_agent)

graph.add_edge(START,'AI_agent')
graph.add_edge('AI_agent',END)



checkpoint = MemorySaver()

work_flow = graph.compile(checkpointer=checkpoint)



while True:

    user = input('user:')
    if user.lower() in ['bye','quit']:
        break


    inital_state={
     'msg':[HumanMessage(content=user)]
     
}
    conf1 ={"configurable":{'thread_id':'2'}}
    

    # ans is bsically our final state
    ans=work_flow.invoke(inital_state,config=conf1)
    

    print(f'AI:{ans['msg'][-1].content}')












