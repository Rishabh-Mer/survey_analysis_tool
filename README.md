# Survey Analysis LLM RAG Agent

This project is a Retrieval-Augmented Generation (RAG) agent designed for analyzing surveys using a Language Model (LLM). It includes a backend for processing data with FastAPI, a frontend using Streamlit for user interaction, and a vector database (ChromaDB) for efficient information retrieval.

For text and table summarization I have used ```Ollama (model: llama3.2-1b)``` and for image summarization OpenAI's ```gpt-4o-mini```.

To test the agent I have hosted the application on ```AWS``` 
Link: [Survey-Analysis-Agent](http://23.22.244.217:8501/)

---
## 📂 Project Structure
* survey_analysis_tool/
    - **`backend/`** - Contains FastAPI services and LLM model integration.
        - `main.py` - Model integration and summarization.
        - `server.py` - FastAPI server to serve the application and handling the requests.
        - `preprocessing.py` - Pdf preprocessing 
        - `utils.py` - Helper functions.
    - **`data/`** - Contain PDFs and Images
        - `images/`
    - **`database`** - ChromaDB persistent storage
    - **`frontend`** - Streamlit web application
        - `app.py` - Streamlit entry point
    - **`notebooks/`** - Jupyter notebooks for development
    **`requirements.txt`** - List of required Python packages.
    - **`README.md`** - Documentation for the project.

## RAG Approach
![RAG Approach](https://github.com/Rishabh-Mer/survey_analysis_tool/blob/main/RAG_Approach.png)

## 📌 Installation Guide

### Set Up Python Environment
Ensure you have ```Python 3.12``` installed. You can create a virtual environment as follows:

```sh
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate  # For Windows 
```
---

### Install Dependencies
```pip install -r requirements.txt```

Create ```.env file``` in root directory and add:
- ```OPENAI_API_KEY: OPENAI_KEY``` 

---

### <img src="https://cdn.brandfetch.io/idrRDmZ2_F/w/180/h/180/theme/light/logo.png?c=1dxbfHSJFAPEGdCLU4o5B" alt="Logo" width="17" height="17"> Install Ollama 
Ollama is required to run the LLM model.
* Mac: [Download Ollama](https://ollama.com/download/mac)
* Windows: [Download Ollama](https://ollama.com/download/windows)

Once installed, run the LLaMA model:
```ollama run llama3.2:1b```

---

### Install Poppler and Tesseract (For PDF & Image Processing)
* MacOS:
    ```
    brew install poppler tesseract
    ```
* Windows: 
    - [Poppler](https://github.com/oschwartz10612/poppler-windows?tab=readme-ov-file)
    - [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

    *After installation, ensure they are added to the system PATH.*

---

### Running the Application Locally
* Start the Backend
    * Navigate to the backend folder:
        ```sh
        cd backend
        python3 main.py 
        ```
    * After successfully saved the summarization in vector database, run ```FastAPI```
        ```
        python3 server.py
        ```
* Start the Frontend
    * Open **another terminal**, navigate to the frontend directory, and run:
        ```sh
        cd frontend
        streamlit run app.py
        ```
* Access the Application
After starting the frontend, open the Streamlit link displayed in the terminal in your web browser 
(http://localhost:8501).

---

### 💡 Additional Notes
* Ensure that ollama is running before starting the backend.
* The vector database (ChromaDB) is stored in the database/ directory.
* Ensure to create ```.env```
* If you encounter issues with dependencies, verify your Python version and package installations.

---
*Enjoy using the Survey Analysis LLM RAG Agent!*