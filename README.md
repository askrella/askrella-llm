# Askrella LLM: Custom Data Q&A

[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Askrella LLM is a Flask-based project that leverages [Langchain](https://github.com/hwchase17/langchain) and [LlamaIndex](https://github.com/jerryjliu/llama_index) to create a REST API powered by LLM's. This API allows you to ingest your own data from raw text or URLs and perform question-answering (Q&A) against it.

## Key Features

- Ingest your own data from raw text or URLs
- Perform Q&A against your ingested data
- Uses a local sentence transformer for generating embeddings, making it cost-effective

## Info about Models

- LLM: GPT-3.5 by OpenAI
- Embed Model: sentence-transformers/all-mpnet-base-v2

## Installation

To run the Askrella LLM project, follow these steps:

```bash
# Clone the repository
git clone https://github.com/askrella/askrella-llm

# Install the required dependencies
pip install -r requirements.txt

# Before starting, make sure to set the required environment variables
# (see Configuration section below)
python app.py
```

## Configuration

The Askrella LLM project requires the following environment variables to be set. You can set them in a `.env` file in the root directory of the project.

```bash
# REST API Port
PORT=8080

# REST API - API KEY, default: "askrella"
API_KEY=<rest_api_key>

# OpenAI API key
OPENAI_API_KEY=<openai_api_key>
```

## Authorization

All requests to the Askrella LLM REST API require an API key to be set in the `Authorization` header.

Only the ingest endpoint is protected by the API key. The query endpoint is not protected by the API key.

Example:
```
Authorization: Bearer <rest_api_key>
```

## Ingesting Documents

Create a new collection of documents. The collection name is used to identify the collection in future requests.

For ingesting audio files, you have to install ffmpeg. Follow the instructions [here](https://github.com/openai/whisper#setup)

**POST** `/collection/<collection>`

Request:

```json
{
    "text": [
        "This is some example text",
        "And this is more example text"
    ],
    "urls": [
        "https://askrella.de/",
        "https://en.wikipedia.org/wiki/OpenAI",
        "https://pastebin.com/raw/stzZ6S1J"
    ],
    "audio_urls": [
        "https://audio-samples.github.io/samples/mp3/blizzard_biased/sample-0.mp3"
    ]
}
```

Response:

```json
{
    "success": true
}
```

## Querying Documents

Ask questions against your ingested data.

**POST** `/collection/<collection>/query`

Request:

```json
{
    "prompt": "Who is Askrella?"
}
```

Response:

```json
{
    "response": "Askrella is a software agency that specializes in planning and developing cloud projects, offering tailored solutions and captivating web design using React.js, Node.js, Flutter, and Golang. They focus on the leading cloud platform, Amazon AWS, to ensure robust and scalable solutions for their clients. Askrella was founded in December 2022 by Steven Hornbogen, Stanislav Hetzel, and Paul Seebach. Their team of skilled professionals provides comprehensive support throughout the entire project lifecycle, including project planning, wireframe and mockup creation, quality assurance testing, deployment, and ongoing maintenance."
}
```

## Crawl website url's

Crawl a website and get all url's from it.

**POST** `/crawl`

Request:

```json
{
    "url": "https://example.com"
}
```

Response:
```json
{
    "urls": [
        "https://www.iana.org/domains/example"
    ]
}
```

## License
This Software is AGPL v3 licensed. Checkout [here](LICENSE)
