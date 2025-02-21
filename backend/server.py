from fastapi import FastAPI
from pydantic import BaseModel

from base64 import b64decode

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

from loguru import logger
from utils import read_yaml
from dotenv import load_dotenv

load_dotenv()

def parse_docs(docs):

    b64 = []
    text = []

    for doc in docs:
        try:
            b64decode(doc)
            b64.append(doc)
        except Exception as e:
            text.append(doc)

    return {"images": b64, "texts":text} 


def build_prompt(kwargs):

    docs_by_type = kwargs["context"]
    user_question = kwargs["question"]

    context_text = ""

    if len(docs_by_type["texts"]) > 0:
        for text_element in docs_by_type["texts"]:
            context_text += text_element.page_content


    prompt_template = f"""
        
    Answer the question based only on the following context, which can text, tables and the image.
    Context: {context_text}
    Question: {user_question}
    
    """

    prompt_content = [{"type": "text", "text": prompt_template}]

    if len(docs_by_type["images"]) > 0:
        for image in docs_by_type["images"]:
            prompt_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                }
            )

    return ChatPromptTemplate.from_messages(
        [
            HumanMessage(content=prompt_content)
        ]
    )

class Survey(BaseModel):
    query: str
 
app = FastAPI()

@app.post('/survey')
def root(input:Survey):
    
    logger.info(f"Received query: {input.query}")
    
    yaml = read_yaml("../data/data.yaml")
    chromadb_path = yaml["chromadb_path"]

    logger.warning(f"ChromaDB Path: {chromadb_path}")
    
    vectorstore = Chroma(collection_name="survey_analysis_rag", persist_directory=chromadb_path, embedding_function=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()
    logger.warning(f"Retriever: {retriever}")
    
    chain = {
        "context": retriever | RunnableLambda(parse_docs),
        "question": RunnablePassthrough(),
        } | RunnablePassthrough().assign(
            response=(
                RunnableLambda(build_prompt)
                | ChatOpenAI(model="gpt-4o-mini")
                | StrOutputParser()
            )
        )
    
    response = chain.invoke(input.query)
    response = response["response"]
    
    logger.warning(f"Response: {response}")
         
    return {"answer": response}  
    
    