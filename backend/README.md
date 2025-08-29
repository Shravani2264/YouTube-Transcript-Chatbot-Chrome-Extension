# Backend for YT RAG Chatbot

This backend exposes a FastAPI endpoint `/ask` that accepts JSON `{video_id, question}` and returns an answer using the pipeline:
- fetch transcript with `youtube-transcript-api`
- split into chunks with `RecursiveCharacterTextSplitter`
- create embeddings using `GoogleGenerativeAIEmbeddings`
- build a FAISS vectorstore and retrieve top-k documents
- call `ChatGoogleGenerativeAI` with prompt that restricts answers to the transcript context

Setup:
1. Create a virtualenv and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set `GOOGLE_API_KEY`.
3. Run the backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

Notes:
- This mirrors your notebook code. The project requires access to Google Generative APIs and LangChain Google bindings.
- The code tries to save/load FAISS vectorstores to `CACHE_DIR` to avoid recomputing embeddings repeatedly.
