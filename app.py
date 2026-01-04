import streamlit as st
from ingestor import EnterpriseIngestor

# Page Configuration
st.set_page_config(page_title="Enterprise PDF Search", layout="wide")
st.title("📂 PDF Knowledge Engine")

# Initialize the ingestor (This connects to your Docker databases)
ingestor = EnterpriseIngestor()

# --- STEP 1: UPLOAD ---
st.header("1. Data Ingestion")
uploaded_file = st.file_uploader("Upload an Enterprise PDF (Manual/Policy/Report)", type="pdf")

if uploaded_file:
    # We save the file inside the container temporarily to process it
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("Index Document"):
        with st.spinner("Running OCR and Layout Analysis... this may take a moment."):
            count = ingestor.process_pdf(uploaded_file.name)
            st.success(f"Successfully processed {count} document elements!")

st.divider()

# --- STEP 2: SEARCH ---
st.header("2. Search & Retrieval")
query = st.text_input("Ask a question about your indexed documents:")
if query:
    st.subheader("Search Results:")
    results = ingestor.search(query)
    
    if not results:
        st.write("No matching information found.")
    else:
        for res in results:
            # Displays findings in a clean UI box
            st.info(res)