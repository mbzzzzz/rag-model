# RAG Chat Assistant

A beautiful, cost-effective RAG (Retrieval-Augmented Generation) system powered by Claude's most affordable model (Claude-3-Haiku) with a stunning seafoam green, white, and black color scheme.

## Features

- 🤖 **Claude-3-Haiku Integration**: Uses the most cost-effective Claude model for optimal performance within budget
- 📄 **Multi-format Document Support**: Upload and process PDF, DOCX, and TXT files
- 🔍 **Vector Search**: ChromaDB-powered semantic search for relevant document chunks
- 💬 **Beautiful Chat Interface**: Modern, responsive design with seafoam green theme
- 🎨 **Drag & Drop Upload**: Intuitive file upload with visual feedback
- ⚡ **Real-time Chat**: Instant responses with typing indicators

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Anthropic API Key**:
   - Get your API key from [Anthropic Console](https://console.anthropic.com/)
   - Create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the Interface**:
   - Open your browser and go to `http://localhost:5000`
   - Upload documents and start chatting!

## Cost Optimization

This RAG system is designed to be budget-friendly:

- **Claude-3-Haiku**: The most cost-effective Claude model ($0.25 per 1M input tokens, $1.25 per 1M output tokens)
- **Efficient Chunking**: Smart text chunking with overlap to minimize API calls
- **Local Embeddings**: Uses local sentence transformers to avoid embedding API costs
- **Local Vector Storage**: ChromaDB runs locally without cloud storage fees

## Architecture

- **Backend**: Flask with CORS support
- **AI Model**: Claude-3-Haiku via Anthropic API
- **Vector Database**: ChromaDB for local storage
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Frontend**: Pure HTML/CSS/JavaScript with beautiful responsive design

## File Structure

```
rag-model/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Beautiful chat interface
└── uploads/              # Uploaded documents (created automatically)
```

## Usage Tips

1. **Upload Documents**: Drag and drop or click to upload PDF, DOCX, or TXT files
2. **Ask Questions**: Type questions about your uploaded documents
3. **Get Contextual Answers**: The AI will search through your documents and provide relevant answers
4. **Cost Monitoring**: Monitor your Anthropic usage in the console dashboard

## Troubleshooting

- **API Key Issues**: Ensure your `.env` file contains a valid Anthropic API key
- **File Upload Errors**: Check file format (only PDF, DOCX, TXT supported)
- **Memory Issues**: For large documents, consider splitting them into smaller files

## License

This project is open source and available under the MIT License.
