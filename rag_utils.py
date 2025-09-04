# rag_utils.py

import os
import sys
from dotenv import load_dotenv
import fitz  # PyMuPDF
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
from langchain_groq import ChatGroq

# --- SQLite patch for Chroma in Streamlit Cloud ---
try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

# --- Load environment ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

# --- Initialize LLM & Embeddings ---
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0
)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


# --- Functions ---

def extract_text(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    """
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def parse_edit_instruction(instruction: str) -> dict:
    """
    Parse a text editing instruction and return structured info.
    Example output: {"action": "replace", "target": "old_text", "replacement": "new_text"}
    """
    # Simple placeholder logic — adapt to your needs
    parts = instruction.lower().split("replace")
    if len(parts) == 2:
        target_replacement = parts[1].strip().split("with")
        if len(target_replacement) == 2:
            return {
                "action": "replace",
                "target": target_replacement[0].strip(),
                "replacement": target_replacement[1].strip()
            }
    return {"action": "unknown"}


def build_rag(raw_text: str):
    """
    Build a Retrieval-Augmented Generation (RAG) pipeline from input text.
    """
    docs = [Document(page_content=raw_text)]
    chunks = splitter.split_documents(docs)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    retriever = vector_store.as_retriever()

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True
    )
