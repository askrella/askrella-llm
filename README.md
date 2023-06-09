# Askrella LLM: Custom Data Q&A

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Askrella LLM is a Flask-based API project that leverages [Langchain](https://github.com/hwchase17/langchain) and [LlamaIndex](https://github.com/jerryjliu/llama_index) to create a chat application powered by Language Model (LLM). This project allows you to ingest your own data from raw text or URLs and perform question-answering (Q&A) against it.

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

# OpenAI API key
OPENAI_API_KEY=<api_key>
```

## Ingesting Documents

Create a new collection of documents. The collection name is used to identify the collection in future requests.

**POST** `/collection/<collection>`

Request payload example:

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

Request payload example:

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

## License

Askrella LLM is licensed under the MIT License (MIT)

Copyright (c) 2023 Askrella Software Agency UG (haftungsbeschränkt)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.