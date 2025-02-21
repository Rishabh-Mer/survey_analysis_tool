import os
import base64
from base64 import b64decode
from unstructured.partition.pdf import partition_pdf

from loguru import logger
from typing import List
from utils import get_all_files

def pdf_partitions(file_path:str) -> list:
    
    """
    Get all the partitions of the pdf file
    
    file: 
        str: file_path directory
        
    Returns:
        list: list of partitions
    
    """
    
    image_folder = "../data/images/"
    
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
        
    if "2024" in file_path:
        
        logger.info(f"Processing file: {file_path}")
        
        pdf_chunks = partition_pdf(
            filename=file_path,
            infer_table_structure=True,
            strategy="hi_res",
            extract_image_block_types=["Image", "Table"],
            extract_image_block_output_dir=image_folder,
            extract_image_block_to_payload=False,
            
            chunking_strategy="by_title",
            max_characters=15000,
            combine_text_under_n_chars=5000,
            new_after_n_chars=10000
        )
        logger.success(f"File processed successfully: {file_path}")
        
    else:
        
        logger.info(f"Processing file: {file_path}")
        
        pdf_chunks = partition_pdf(
            filename=file_path,
            infer_table_structure=True,
            strategy="hi_res",
            extract_image_block_types=["Image", "Table"],
            extract_image_block_output_dir=image_folder,
            extract_image_block_to_payload=False,
            chunking_strategy="by_title"
        )
        
        logger.success(f"File processed successfully: {file_path}")
        
    return pdf_chunks


def extract_elements(elements: List) -> list[list, list]:
    
    """
    Extract elements from the list
    
    elements:
        List: list of elements
        
    Returns:
        [list, list]: list of text and tables elements
    
    """
    
    texts, tables = [], []
    
    for element in elements:
        if "CompositeElement" in str(type(element)):
            texts.append(element) 
            
        if "Table" in str(type(element)):
            tables.append(element)
            
    
    return texts, tables


def images_to_base64(image_folder_path:str) -> List[str]:
    
    """
    Convert images to base64 and return the list
    
    image_path:
        str: image path
        
    Returns:
        List of base64 encoded images
    
    """
    
    images = []
    
    list_images = get_all_files(image_folder_path, "jpg")
    
    count = 0
    
    for image in list_images:
        with open(image, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            count = count + 1
            images.append(encoded_string)
    
    logger.info(f"Total images converted: {count}")
        
    return images




    
    



    

