from fastapi import FastAPI
from langchain_core.messages import BaseMessage ,HumanMessage ,AIMessage
from graph import work_flow


app = FastAPI()

@app.post("/chat")
def chat(user:str,thread_id:str):
    inital_state={
        'messages':[HumanMessage(content=user)]

    }
    conf1 ={"configurable":{'thread_id':thread_id}}

    ans = work_flow.invoke(inital_state,config=conf1)

    return {'response':ans['messages'][-1].content}

    