import base64
import yaml

from glob import glob
from IPython.display import Image, display

def get_all_files(file:str, extension:str) -> list:
    """
    Get all the files with same extension in the directory
    
    file: 
        str: file_path directory
    extension: 
        str: file extension
    """

    return glob(file + '*.' + extension, recursive=True)


def display_images(encoded_image:str):
    
    """
    Display images in the notebook
    
    encoded_image: 
        str: encoded image
    """
    
    display(Image(data=base64.b64decode(encoded_image)))
    

def read_yaml(file:str) -> dict:
    """
    Read yaml file
    
    file: 
        str: file_path directory
    """
    
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)