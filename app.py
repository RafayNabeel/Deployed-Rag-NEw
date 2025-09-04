import sys
import os
import streamlit as st
from pdf_utils import replace_text_with_style, highlight_text_in_pdf
from rag_utils import extract_text, build_rag, parse_edit_instruction

# ---------------------------
# Streamlit Cloud SQLite fix
# ---------------------------
try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except KeyError:
    pass  # Already using system sqlite3

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Intelligent PDF Editor", page_icon="📄")
st.title("📄 Intelligent PDF Editor")

uploaded_file = st.file_uploader("📄 Upload a PDF or TXT document", type=["txt", "pdf"])

if uploaded_file:
    # Save uploaded file temporarily
    temp_input_path = "temp_input.pdf" if uploaded_file.type == "application/pdf" else "temp_input.txt"
    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract text
    raw_text = extract_text(temp_input_path)
    if not raw_text.strip():
        st.error("⚠️ No text could be extracted from this file.")
        st.stop()
    st.success("✅ Document loaded successfully!")

    # Initialize RAG QA
    qa = build_rag(raw_text)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User query input
    user_query = st.chat_input("Ask about your document or request an edit...")
    if user_query:
        instruction = parse_edit_instruction(user_query)

        # Handle replace
        if instruction.get("action") == "replace":
            old = instruction.get("target")
            new = instruction.get("replacement")
            if old and new:
                st.json(instruction)  # Debug output
                replace_text_with_style(temp_input_path, "output.pdf", old, new)
                st.success(f"✅ Replaced '{old}' with '{new}'")
                with open("output.pdf", "rb") as f:
                    st.download_button("⬇️ Download Updated PDF", f, file_name="updated.pdf")
            else:
                st.error("⚠️ Could not parse old/new text from your instruction.")

        # Handle highlight
        elif instruction.get("action") == "highlight":
            old = instruction.get("target")
            if old:
                highlight_text_in_pdf(temp_input_path, "output.pdf", old)
                st.success(f"✅ Highlighted '{old}'")
                with open("output.pdf", "rb") as f:
                    st.download_button("⬇️ Download Updated PDF", f, file_name="updated.pdf")
            else:
                st.error("⚠️ Could not parse text to highlight.")

        # Handle RAG query
        else:
            result = qa.invoke({"query": user_query})
            st.session_state.chat_history.append({"user": user_query, "ai": result["result"]})

    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["user"])
        with st.chat_message("assistant"):
            st.write(chat["ai"])

    # Optional: clean up temp files
    if os.path.exists(temp_input_path):
        os.remove(temp_input_path)
    if os.path.exists("output.pdf"):
        os.remove("output.pdf")

else:
    st.info("👆 Upload a `.txt` or `.pdf` file to begin.")
