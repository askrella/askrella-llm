import os

# Flask
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

# Langchain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

# Llama index
from llama_index import (
    ServiceContext, StorageContext, VectorStoreIndex,
    LLMPredictor, LangchainEmbedding, Document,
    load_index_from_storage
)

# OpenAI Whisper
import whisper

# Crawl
from crawl import crawl_website

# Utils
from dotenv import load_dotenv
import tempfile
import shutil

# Constants
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

# Build whisper model
print("Preparing OpenAI whisper...")
whisper_model = whisper.load_model("small")

# Flask
api = Flask(__name__)
CORS(api, origins=["http://localhost:5173"])  # Enable CORS
api_key = os.getenv("API_KEY", "askrella")

@api.before_request
def check_api_key():
    authorization_header = request.headers.get("Authorization")
    bearer = "Bearer "

    if not authorization_header or not authorization_header.startswith(bearer):
        return jsonify({"error": "Invalid API key"}), 401

    api_key_header = authorization_header[len(bearer):]

    if api_key_header != api_key:
        return jsonify({"error": "Invalid API key"}), 401

# Input { url }
# Output { urls: [] }
@cross_origin()
@api.route("/crawl", methods=['POST'])
def crawl():
    # Json input
    url = request.json.get('url')

    # Validate
    if url is None or len(url) == 0:
        return jsonify({"error": "No URL to crawl"}), 400

    # Crawl
    urls = crawl_website(url)

    return jsonify({
        "urls": urls,
    })

@cross_origin()
@api.route("/collection/<collection>/ingest", methods=['POST'])
def ingest_collection(collection: str):
    # Form file input
    ingest_file = request.files.get('file')

    # Validate
    if ingest_file is None:
        return jsonify({"error": "No file to ingest"}), 400

    # Check if index exists
    collection_data_path = os.path.join(VECTOR_DATA_PATH, collection)

    if not os.path.exists(collection_data_path):
        return jsonify({"error": f"Collection {collection} does not exist"}), 404

    # Build StorageContext
    storage_ctx = StorageContext.from_defaults(
        persist_dir=collection_data_path
    )

    # Load index
    index: VectorStoreIndex = load_index_from_storage(
        storage_context=storage_ctx,
        service_context=service_context
    )

    # Depending on the type of extension, ingest
    ingest_file_ext = ingest_file.filename.split(".")[-1]

    if ingest_file_ext == "txt":
        # Read text from file
        content = ingest_file.read().decode("utf-8")

        # Build document
        document = Document(text=content)
        index.insert(document)
    elif ingest_file_ext in ["mp3", "wav", "ogg", "audio"]:
        # Download audio file into a temporary folder
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False)

        # Write ingest file to temp file
        ingest_file.save(temp_audio_file.name)

        # Transcribe audio file
        whisper_result = whisper_model.transcribe(temp_audio_file.name)
        whisper_result_text = whisper_result["text"]

        # Build document
        document = Document(text=whisper_result_text)
        index.insert(document)

        # Delete temp file
        os.unlink(temp_audio_file.name)
    else:
        return jsonify({"error": "Invalid file type"}), 400

    # Delete old index
    shutil.rmtree(collection_data_path)

    # Save index
    index.storage_context.persist(
        os.path.join(VECTOR_DATA_PATH, collection)
    )

    return jsonify({
        "success": True,
    })

# Input { }
@cross_origin()
@api.route("/collection/<collection>", methods=['POST'])
def create_collection(collection: str):
    # Build documents
    documents = []

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

# Delete collection
@cross_origin()
@api.route("/collection/<collection>", methods=['DELETE'])
def delete_collection(collection: str):
    # Delete collection
    collection_data_path = os.path.join(VECTOR_DATA_PATH, collection)

    # Check if index exists
    if not os.path.exists(collection_data_path):
        return jsonify({"error": f"Collection {collection} does not exist"}), 404

    # Delete collection
    shutil.rmtree(collection_data_path)

    return jsonify({
        "success": True,
    })

# Input { prompt }
@api.route("/collection/<collection>/query", methods=['POST'])
def query_collection(collection: str):
    # Json input
    prompt = request.json.get('prompt')

    # Validate
    if prompt is None or len(prompt) == 0:
        return jsonify({"error": "No prompt to query"}), 400

    # Load index
    collection_data_path = os.path.join(VECTOR_DATA_PATH, collection)

    # Check if index exists
    if not os.path.exists(collection_data_path):
        return jsonify({"error": f"Collection {collection} does not exist"}), 404

    print(f"Loading index from {collection_data_path}...")

    # Build StorageContext
    storage_ctx = StorageContext.from_defaults(
        persist_dir=collection_data_path
    )

    # Load index
    index: VectorStoreIndex = load_index_from_storage(
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
    }), 200

if __name__ == '__main__':
    api_port = os.getenv("PORT", 8080)

    print(f"Starting API on port {api_port}...")
    api.run(port=api_port)
