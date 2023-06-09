import os

# Flask
from flask import Flask, request, jsonify

# Langchain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

# Llama index
from llama_index import (
    ServiceContext, StorageContext, VectorStoreIndex,
    BeautifulSoupWebReader, LLMPredictor,
    LangchainEmbedding, Document,
    load_index_from_storage
)

# Utils
from dotenv import load_dotenv

# Contants
VECTOR_DATA_PATH = "./data"

# Load .env
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Build service context
print("Building service context...")

llm = ChatOpenAI()
llm_predictor = LLMPredictor(llm=llm)
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
)

service_context = ServiceContext.from_defaults(
    llm_predictor=llm_predictor,
    embed_model=embed_model
)

# Chroma DB
api = Flask(__name__)

# Input { web: [url], text: [text] }
@api.route("/collection/<collection>", methods=['POST'])
def create_collection(collection: str):
    # Json input
    ingest_text = request.json['text']
    ingest_urls = request.json['urls']

    # Validate
    if (ingest_text == None or len(ingest_text) == 0) and (ingest_urls == None or len(ingest_urls) == 0):
        return jsonify({ "error": "No text or web urls to ingest" })

    # Build documents
    documents = []

    # Ingest web urls
    if len(ingest_urls) > 0:
        web_documents = BeautifulSoupWebReader().load_data(ingest_urls)
        documents.extend(web_documents)

    # Ingest raw text
    if ingest_text != None and len(ingest_text) > 0:
        raw_text_docs = [Document(text=text) for text in ingest_text]
        documents.extend(raw_text_docs)

    # Create index and save index
    index = VectorStoreIndex.from_documents(
        documents=documents,
        service_context=service_context
    )

    # Save index
    index.storage_context.persist(
        os.path.join(VECTOR_DATA_PATH, collection)
    )

    return jsonify({
        "success": True,
    })

# Input { prompt }
@api.route("/collection/<collection>/query", methods=['POST'])
def query_collection(collection: str):
    # Json input
    prompt = request.json['prompt']

    # Validate
    if prompt == None or len(prompt) == 0:
        return jsonify({ "error": "No prompt to query" })
    
    # Load index
    collection_data_path = os.path.join(VECTOR_DATA_PATH, collection)
    print(f"Loading index from {collection_data_path}...")

    # Build StorageContext
    storage_ctx = StorageContext.from_defaults(
        persist_dir=collection_data_path
    )

    # Load index
    index = load_index_from_storage(
        storage_context=storage_ctx,
        service_context=service_context
    )

    # Query
    print(f"Querying index with prompt: {prompt}")
    query_engine = index.as_query_engine(service_context=service_context)
    response = query_engine.query(prompt)

    print(f"Response: {response.response}")

    return jsonify({
        "response": response.response,
    })

if __name__ == '__main__':
    api_port = os.getenv("PORT", 8080)
    
    print(f"Starting API on port {api_port}...")
    api.run(port=api_port)
