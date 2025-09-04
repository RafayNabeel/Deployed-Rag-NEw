# test_imports.py

def test_imports():
    try:
        import os
        import streamlit
        import dotenv
        from pypdf import PdfReader
        from langchain_groq import ChatGroq
        from langchain_community.vectorstores import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.chains import RetrievalQA
        from langchain_core.documents import Document

        print("✅ All imports loaded successfully!")
    except ImportError as e:
        print(f"❌ Import failed: {e}")

if __name__ == "__main__":
    test_imports()
