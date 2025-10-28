from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
import uuid
import tempfile
from anthropic import Anthropic
import chromadb
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Initialize Claude client with the most cost-effective model
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Initialize ChromaDB for vector storage (in-memory for serverless)
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="documents")

# Initialize sentence transformer for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

class RAGSystem:
    def __init__(self):
        self.collection = collection
        self.embedding_model = model
        
    def process_document(self, file_path, file_type):
        """Process uploaded document and create embeddings"""
        try:
            if file_type == 'pdf':
                text = self.extract_pdf_text(file_path)
            elif file_type == 'docx':
                text = self.extract_docx_text(file_path)
            else:
                text = self.extract_txt_text(file_path)
            
            # Split text into chunks
            chunks = self.split_text_into_chunks(text)
            
            # Create embeddings and store in ChromaDB
            for i, chunk in enumerate(chunks):
                embedding = self.embedding_model.encode(chunk).tolist()
                doc_id = f"{file_path}_{i}"
                self.collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    ids=[doc_id],
                    metadatas=[{"source": file_path, "chunk_id": i}]
                )
            
            return True, f"Processed {len(chunks)} chunks from {file_path}"
        except Exception as e:
            return False, str(e)
    
    def extract_pdf_text(self, file_path):
        """Extract text from PDF file"""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def extract_docx_text(self, file_path):
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def extract_txt_text(self, file_path):
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def split_text_into_chunks(self, text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def retrieve_relevant_chunks(self, query, top_k=3):
        """Retrieve relevant chunks based on query"""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return results['documents'][0], results['metadatas'][0]
    
    def generate_response(self, query, context_chunks):
        """Generate response using Claude with retrieved context"""
        context = "\n\n".join(context_chunks)
        
        prompt = f"""Based on the following context, please answer the user's question. If the answer cannot be found in the context, please say so.

Context:
{context}

Question: {query}

Answer:"""

        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",  # Most cost-effective Claude model
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"

# Initialize RAG system
rag_system = RAGSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'RAG Chat Assistant is running!'})

@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
        file.save(temp_file.name)
        temp_filename = temp_file.name
    
    try:
        # Process document
        file_type = file.filename.split('.')[-1].lower()
        success, message = rag_system.process_document(temp_filename, file_type)
        
        if success:
            return jsonify({'message': message})
        else:
            return jsonify({'error': message}), 500
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_filename)
        except:
            pass

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    query = data.get('message', '')
    
    if not query:
        return jsonify({'error': 'No message provided'}), 400
    
    # Retrieve relevant chunks
    chunks, metadata = rag_system.retrieve_relevant_chunks(query)
    
    # Generate response
    response = rag_system.generate_response(query, chunks)
    
    return jsonify({
        'response': response,
        'sources': metadata
    })

# Vercel handler
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
