# Backend for YT RAG Chatbot

This backend exposes a FastAPI endpoint `/ask` that accepts JSON `{video_id, question}` and returns an answer using the pipeline:
- fetch transcript with `youtube-transcript-api`
- split into chunks with `RecursiveCharacterTextSplitter`
- create embeddings using `GoogleGenerativeAIEmbeddings`
- build a FAISS vectorstore and retrieve top-k documents
- call `ChatGoogleGenerativeAI` with prompt that restricts answers to the transcript context
