from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os
import traceback
from pytube import YouTube # Import pytube

# LangChain & Google Generative AI imports
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.prompts import PromptTemplate
except Exception as e:
    print(f"Error importing LangChain/Google Gen AI libraries: {e}")

# Load environment variables from a .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI(title="YouTube RAG Chatbot Backend")

# Define the structure of the incoming request body
class AskRequest(BaseModel):
    video_id: str
    question: str

# --- Caching Setup ---
CACHE_DIR = os.getenv("CACHE_DIR", "vector_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# --- Core Functions ---

def fetch_transcript(video_id: str, languages=['en']) -> str | None:
    """Fetches the transcript for a given YouTube video ID."""
    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=languages)
        return " ".join(chunk.text for chunk in transcript_list)
    except Exception as e:
        print(f"Could not retrieve transcript for video ID: {video_id}. Error: {e}")
        return None

def get_vectorstore(video_id: str) -> FAISS | None:
    """Loads a vector store from cache or builds a new one if it doesn't exist."""
    save_path = os.path.join(CACHE_DIR, f"{video_id}_faiss")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Try to load from the local cache first
    if os.path.exists(save_path):
        try:
            print(f"Loading vector store from cache for video ID: {video_id}")
            return FAISS.load_local(save_path, embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"Failed to load from cache: {e}")

    # If not in cache, fetch transcript and build it
    print(f"Cache not found. Building new vector store for video ID: {video_id}")
    transcript = fetch_transcript(video_id)
    if not transcript:
        return None

    # --- NEW: Fetch metadata using pytube ---
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        video_title = yt.title
        video_author = yt.author
        metadata_text = f"Video Title: {video_title}\nChannel Name: {video_author}\n\n"
        full_text = metadata_text + transcript # Prepend metadata to the transcript
    except Exception as e:
        print(f"Could not fetch metadata with pytube: {e}")
        full_text = transcript # Fallback to just the transcript

    # Split the combined text (metadata + transcript) into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.create_documents([full_text])
    
    # Create the vector store from the document chunks
    vector_store = FAISS.from_documents(docs, embeddings)
    
    # Save the newly created vector store to the cache
    try:
        vector_store.save_local(save_path)
        print(f"Saved new vector store to cache for video ID: {video_id}")
    except Exception as e:
        print(f"Could not save vector store to cache: {e}")
        
    return vector_store

# --- AI and Prompting Setup ---

# --- NEW: Improved prompt template ---
PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions about a specific YouTube video using its transcript and metadata. 
Your capabilities are:
1. Answering questions based on the content of the video's spoken words.
2. Providing details about the video like its title and channel name.

Answer the user's question based ONLY on the following context. If the information is not in the context, say "I don't know".

CONTEXT:
{context}

QUESTION:
{question}
"""
prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

# Use a singleton pattern to initialize the LLM only once
LLM = None
def get_llm():
    """Initializes and returns the Gemini LLM instance."""
    global LLM
    if LLM is None:
        print("Initializing LLM...")
        LLM = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            convert_system_message_to_human=True
        )
    return LLM

# --- API Endpoint ---

@app.post("/ask")
async def ask(request: AskRequest):
    """Main endpoint to handle user questions about a YouTube video."""
    try:
        vector_store = get_vectorstore(request.video_id)
        if not vector_store:
            raise HTTPException(
                status_code=400, 
                detail="Could not retrieve or process the transcript for this video. Captions may be disabled."
            )
        
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        
        retrieved_docs = retriever.invoke(request.question)
        context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
        
        final_prompt = prompt.format(context=context_text, question=request.question)
        
        llm = get_llm()
        answer = llm.invoke(final_prompt)
        
        return {"answer": answer.content, "context": context_text}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print("An unexpected error occurred:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)