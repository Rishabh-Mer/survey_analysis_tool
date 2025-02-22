from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.storage import InMemoryStore
from langchain.schema.document import Document
from langchain.retrievers.multi_vector import MultiVectorRetriever


import os
import uuid
from dotenv import load_dotenv
from huggingface_hub import login, whoami
from loguru import logger


from utils import get_all_files, read_yaml
from preprocessing import pdf_partitions, extract_elements, images_to_base64
load_dotenv()

def get_text_table_summarization_prompt():
    
    return """ 
    You are an assistant tasked with summarizing tables and text.
    Give a brief summary of the table or text.

    Respond only with the summary, no additional comment.
    Do not start your sentence by saying "Here is a summary" or anything like that.
    Just give the summary as it is.

    for context the content is from 2 documents which is proxy statement of year 2024 and AIM (Analyst and investor meeting)of year 2023 
    of ConocoPhillips which is one of the world’s largest independent E&P companies 
    based on production and proved reserves.

    Table or text chunk: {element}"""
    
def create_summarization_chain(model_name="llama3.2:1b"):
    """
    Create a summarization chain
    """
    prompt_text = get_text_table_summarization_prompt()
    prompt = ChatPromptTemplate.from_template(prompt_text)
    model = OllamaLLM(model=model_name)
    return prompt | model | StrOutputParser()

def get_image_prompt():
    return """

    Describe the image in detail. For context,
    the image is part of two documents The ConocoPhillips 2024 Proxy Statement and 2023 Analyst & Investor Meeting Presentation outline the company's strategy, portfolio, financial plan, and sustainability goals. 
    Key topics include board elections, executive compensation, financial performance, and stockholder engagement. 
    The company emphasizes a disciplined, returns-focused strategy, strong financial discipline, and progress on its net-zero energy transition plan. It also highlights operational milestones, LNG expansion, and emissions reduction targets, reinforcing its commitment to long-term value creation for stockholders.

    ### Instructions:
    - Provide a **detailed description** of the image.
    - If the image contains **graphs (e.g., bar charts, line graphs, pie charts)**, describe:
    - The **type of chart** (bar, line, scatter, etc.).
    - **Key trends, labels, and numerical values** visible.
    - **Comparisons or significant insights** from the data.
    - If the image contains **tables or figures**, summarize their key takeaways.

    Focus on **clarity, accuracy, and relevance** while ensuring a structured and comprehensive response.

    """

def create_image_summarization_chain():
    prompt_template_image = get_image_prompt()
    messages = [
        ("user", [
            {"type": "text", "text": prompt_template_image},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,{image}"}}
        ])
    ]
    image_prompt = ChatPromptTemplate.from_messages(messages)
    image_model = ChatOpenAI(model="gpt-4o-mini")
    return image_prompt | image_model | StrOutputParser()

# Function to process tables and text summaries in batches
def process_text_and_tables(texts, tables):
    summarize_chain = create_summarization_chain()
    tables_html = [table.metadata.text_as_html for table in tables]
    
    text_summaries = summarize_chain.batch(texts, {"max_concurrency": 3})
    table_summaries = summarize_chain.batch(tables_html, {"max_concurrency": 3})
    
    logger.success("Text and Table Summarization Completed")

    return text_summaries, table_summaries

# Function to process images in batches
def process_images(images):
    image_summarize_chain = create_image_summarization_chain()
    image_summaries = image_summarize_chain.batch(images)

    logger.success("Image Summarization Completed")
    
    return image_summaries

# Function to store data in vector store
def store_summaries_in_vectorstore(texts, tables, images):
    vectorstore = Chroma(collection_name="survey_analysis_rag", embedding_function=OpenAIEmbeddings(), persist_directory="../database/")
    store = InMemoryStore()
    id_key = "doc_id"

    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )

    # Text
    doc_ids = [str(uuid.uuid4()) for _ in texts]
    summary_texts = [
        Document(page_content=summary, metadata={id_key: doc_ids[i]}) for i, summary in enumerate(texts)
    ]
    retriever.vectorstore.add_documents(summary_texts)
    retriever.docstore.mset(list(zip(doc_ids, texts)))

    # Tables
    table_ids = [str(uuid.uuid4()) for _ in tables]
    summary_tables = [
        Document(page_content=summary, metadata={id_key: table_ids[i]}) for i, summary in enumerate(tables)
    ]
    retriever.vectorstore.add_documents(summary_tables)
    retriever.docstore.mset(list(zip(table_ids, tables)))

    # Images
    img_ids = [str(uuid.uuid4()) for _ in images]
    summary_img = [
        Document(page_content=summary, metadata={id_key: img_ids[i]}) for i, summary in enumerate(images)
    ]
    retriever.vectorstore.add_documents(summary_img)
    retriever.docstore.mset(list(zip(img_ids, images)))
        
    logger.success("Summaries and Documents stored in Vector Store")


# Main Execution Function
def main(texts, tables, images):
    text_summaries, table_summaries = process_text_and_tables(texts, tables)
    image_summaries = process_images(images)
    store_summaries_in_vectorstore(text_summaries, table_summaries, image_summaries)
    
    logger.success("Preprocessing and Summarization Completed")
    

if __name__ == "__main__":
    
    yaml = read_yaml("../data/data.yaml")
    
    pdf_files = get_all_files("../data/", "pdf")
    logger.info(f"Found {len(pdf_files)} pdf files")
    
    final_texts, final_tables = [], []

    for pdf_file in pdf_files:
        
        pdf_chunks = pdf_partitions(pdf_file)
        texts, tables = extract_elements(pdf_chunks)
        
        final_texts.extend(texts)
        final_tables.extend(tables)
        
    logger.info(f"Total Texts: {len(final_texts)}")
    logger.info(f"Total Tables: {len(final_tables)}")
    
    final_images = images_to_base64(yaml["images_folder_path"])
    
    main(final_texts, final_tables, final_images)
    
    
    
    
    
    



    


