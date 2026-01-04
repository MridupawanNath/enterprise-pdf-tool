import os
from unstructured.partition.pdf import partition_pdf
from pymongo import MongoClient
import chromadb

class EnterpriseIngestor:
    def __init__(self):
        # Connect to MongoDB (NoSQL) using the service name defined in docker-compose
        self.mongo_client = MongoClient("mongodb://mongodb:27017/")
        self.db = self.mongo_client.knowledge_base
        
        # Connect to ChromaDB (Vector) using the service name defined in docker-compose
        self.chroma_client = chromadb.HttpClient(host='chroma', port=8000)
        self.collection = self.chroma_client.get_or_create_collection("pdf_docs")

    def process_pdf(self, file_path):
        # hi_res strategy uses OCR for scans and Layout models for structure
        elements = partition_pdf(
            filename=file_path,
            strategy="hi_res", 
            infer_table_structure=True,
            chunking_strategy="by_title"
        )

        for i, el in enumerate(elements):
            if el.category == "Table":
                # Store Table in NoSQL for precise retrieval
                table_html = getattr(el.metadata, 'text_as_html', el.text)
                self.db.tables.insert_one({
                    "source": file_path,
                    "content": table_html
                })
            else:
                # Store Text in Vector DB for semantic search
                self.collection.add(
                    documents=[el.text],
                    metadatas=[{"source": file_path}],
                    ids=[f"{file_path}_{i}"]
                )
        return len(elements)

    def search(self, query):
        # Semantic search retrieves based on 'meaning' rather than just keywords
        results = self.collection.query(query_texts=[query], n_results=3)
        return results['documents'][0] if results['documents'] else []