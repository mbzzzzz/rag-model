from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
import uuid
import tempfile
from anthropic import Anthropic
import PyPDF2
from docx import Document
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except UnicodeDecodeError:
    # Skip loading .env file if there are encoding issues
    pass

# Set environment variable to disable multiprocessing in serverless environment
os.environ['JOBLIB_MULTIPROCESSING'] = '0'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Initialize Claude client with the most cost-effective model
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Simple in-memory storage for documents
documents_storage = []

class RAGSystem:
    def __init__(self):
        self.documents = []
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.tfidf_matrix = None
        
    def process_document(self, file_path, file_type):
        """Process uploaded document and create text chunks"""
        try:
            if file_type == 'pdf':
                text = self.extract_pdf_text(file_path)
            elif file_type == 'docx':
                text = self.extract_docx_text(file_path)
            else:
                text = self.extract_txt_text(file_path)
            
            # Split text into chunks
            chunks = self.split_text_into_chunks(text)
            
            # Store chunks
            for i, chunk in enumerate(chunks):
                self.documents.append({
                    'text': chunk,
                    'source': file_path,
                    'chunk_id': i
                })
            
            # Update TF-IDF matrix
            if self.documents:
                texts = [doc['text'] for doc in self.documents]
                self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            
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
        """Retrieve relevant chunks based on query using TF-IDF"""
        if not self.documents or self.tfidf_matrix is None:
            return [], []
        
        # Transform query using the same vectorizer
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top-k most similar documents
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        chunks = []
        metadata = []
        for idx in top_indices:
            chunks.append(self.documents[idx]['text'])
            metadata.append({
                'source': self.documents[idx]['source'],
                'chunk_id': self.documents[idx]['chunk_id']
            })
        
        return chunks, metadata
    
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
    
    files = request.files.getlist('file')
    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No files selected'}), 400
    
    processed_files = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
            
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            file.save(temp_file.name)
            temp_filename = temp_file.name
        
        try:
            # Process document
            file_type = file.filename.split('.')[-1].lower()
            success, message = rag_system.process_document(temp_filename, file_type)
            
            if success:
                processed_files.append(file.filename)
            else:
                errors.append(f"{file.filename}: {message}")
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_filename)
            except:
                pass
    
    if processed_files:
        success_message = f"Successfully processed {len(processed_files)} file(s): {', '.join(processed_files)}"
        if errors:
            success_message += f" Errors: {'; '.join(errors)}"
        return jsonify({'message': success_message})
    else:
        return jsonify({'error': f"Failed to process any files. Errors: {'; '.join(errors)}"}), 500

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

# Vercel handler - this is the entry point for Vercel
# The app variable is already the Flask WSGI application

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
