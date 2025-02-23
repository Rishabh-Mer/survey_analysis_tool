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

import os
from loguru import logger
from dotenv import load_dotenv
import uvicorn

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
        You are an AI assistant tasked with answering user queries using only the provided context. 
        The context may contain **text, tables, and images** extracted from documents.
        
        If user greeing is found in the query, respond with:
        **"Hello! How can I help you today?"** or **"Hi! How can I assist you today?"**

        - If the answer is **not found in the context**, respond with: 
        **"Sorry, I am not able to answer the question."**
        - Do **not** use external knowledge or assumptions.
        - Ensure numerical accuracy for table data.

        ### Context:
        {context_text}

        ### User Question:
        {user_question}

        Provide a **clear, concise, and well-structured answer** based on the context.
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
    
    chromadb_path = '../database/'
    if not os.path.exists(chromadb_path):
        os.makedirs(chromadb_path)
        
    logger.info(f"ChromaDB Path: {chromadb_path}")
    
    vectorstore = Chroma(collection_name="survey_analysis_rag", persist_directory=chromadb_path, embedding_function=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()
    
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
    
    logger.info(f"Response: {response}")
         
    return {"answer": response}  
    
    
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)