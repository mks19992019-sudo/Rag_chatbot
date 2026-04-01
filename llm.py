from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
apikey=os.getenv('OLLAMA_API_KEY')


# model 
model = ChatOpenAI(
    api_key=apikey,
    base_url='https://ollama.com/v1',
    model='minimax-m2.7',
    

)