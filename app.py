import os

# Flask
from flask import Flask, request, jsonify
from flask_cors import CORS

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

# OpenAI Whisper
import whisper

# Crawl
from crawl import crawl_website

# Utils
from dotenv import load_dotenv
import requests
import tempfile

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

# Build whisper model
whisper_model = whisper.load_model("small")

# Flask
api = Flask(__name__)
CORS(api) # Enable CORS
api_key = os.getenv("API_KEY", "askrella")

def validate_api_key(req):
    authorization_header = req.headers.get("Authorization")
    bearer = "Bearer "

    if not authorization_header or not authorization_header.startswith(bearer):
        return False

    api_key_header = authorization_header[len(bearer):]

    return api_key_header == api_key

# Input { url }
# Output { urls: [] }
@api.route("/crawl", methods=['POST'])
def crawl():
    # Validate API key
    if not validate_api_key(request):
        return jsonify({ "error": "Invalid API key" })

    # Json input
    url = request.json['url']

    # Validate
    if url == None or len(url) == 0:
        return jsonify({ "error": "No url to crawl" })

    # Crawl
    urls = crawl_website(url)

    return jsonify({
        "urls": urls,
    })

# Input { web: [url], text: [text] }
@api.route("/collection/<collection>", methods=['POST'])
def create_collection(collection: str):
    # Validate API key
    if not validate_api_key(request):
        return jsonify({ "error": "Invalid API key" })

    # Json input
    ingest_text = request.json['text']
    ingest_urls = request.json['urls']
    audio_urls = request.json['audio_urls']

    # Validate
    if (ingest_text == None or len(ingest_text) == 0) and (ingest_urls == None or len(ingest_urls) == 0) and (audio_urls == None or len(audio_urls) == 0):
        return jsonify({ "error": "Nothing to ingest" })

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

    # Ingest audio urls
    if audio_urls != None and len(audio_urls) > 0:
        for audio_url in audio_urls:
            try:
                # Download audio file into temp folder
                audio_file = requests.get(audio_url, allow_redirects=True)
                temp_audio_file = tempfile.NamedTemporaryFile(delete=False)

                with open(temp_audio_file.name, 'wb') as f:
                    f.write(audio_file.content)

                # Transcribe audio file
                whisper_result = whisper_model.transcribe(temp_audio_file.name)
                whisper_result_text = whisper_result["text"]

                whisper_doc = Document(text=whisper_result_text, extra_info={
                    "audio_url": audio_url,
                })

                # Add to documents
                documents.append(whisper_doc)
            except Exception as e:
                print(f"Failed to ingest audio url: {audio_url}")
                print(e)

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

    # Check if index exists
    if not os.path.exists(collection_data_path):
        return jsonify({ "error": f"Collection {collection} does not exist" })

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
