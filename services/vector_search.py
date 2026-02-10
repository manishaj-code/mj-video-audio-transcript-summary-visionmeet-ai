import chromadb
from sentence_transformers import SentenceTransformer

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def initialize_chroma():
    """Initialize Chroma DB"""
    return chromadb.Client()

def embed_and_search(data, meeting_name: str, chroma_client, search_mode: bool = False):
    """Embed transcript chunks and store or search"""
    
    collection = chroma_client.get_or_create_collection(
        name=meeting_name.replace(".", "_").replace(" ", "_")[:50]
    )
    
    if not search_mode:
        # Store mode: embed and store transcript chunks
        for chunk in data:
            text = chunk.get("text", "")
            if text:
                embedding = embedding_model.encode(text)
                collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    ids=[f"{meeting_name}_{chunk.get('start', 0)}"],
                    metadatas=[{"timestamp": chunk.get("timestamp", "")}]
                )
    else:
        # Search mode: find relevant chunks
        query_embedding = embedding_model.encode(data)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        return results.get("documents", [[]])[0] if results.get("documents") else []