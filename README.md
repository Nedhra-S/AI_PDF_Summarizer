# AI PDF Summarizer

An AI-powered PDF summarization application built with Python, Streamlit, Ollama, and Qwen 2.5.

The application allows users to upload PDF documents, automatically identify the document type, extract important information, and generate an AI-powered summary and separate key points.

## Overview

Reading and understanding long PDF documents can be time-consuming. This project provides a simple web-based application that helps users quickly understand the important information contained in a PDF.

The application:

- Accepts PDF documents through a web interface
- Extracts text from the uploaded document
- Detects the type of document
- Processes the complete document
- Identifies important information
- Generates an AI-powered summary
- Generates separate key points
- Allows users to download the generated results
- Uses Ollama for local AI processing

## Features

### User Authentication

A simple login system provides access to the application.

### PDF Upload

Users can upload PDF documents directly through the Streamlit interface.

### Document Type Detection

The application automatically identifies the type of uploaded document.

Supported document categories include:

- Lecture Notes
- Resume / CV
- Guidelines / Instructions
- Research Paper
- Report
- Study Material
- Article
- Business Document
- Other

### AI-Powered Summarization

The application analyzes the uploaded document and generates a concise summary containing the most important information.

### Key Point Extraction

Important information is presented separately as key points to make the document easier to review.

### Local AI Processing

The application uses Ollama with the Qwen 2.5 3B model for local AI processing.

No external AI API key is required.

### Download Results

Users can download:

- Summary
- Key Points

### Session Management

The application includes login and logout functionality.

When a user logs out, the current PDF and generated results are cleared from the application session.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web application framework |
| PyPDF | PDF text extraction |
| Ollama | Local AI model execution |
| Qwen 2.5 3B | AI text analysis and summarization |
| Git | Version control |
| GitHub | Source code hosting |

## System Workflow

```text
PDF Upload
    |
    v
Text Extraction
    |
    v
Document Type Detection
    |
    v
Document Processing
    |
    v
Important Information Extraction
    |
    v
AI Analysis using Qwen 2.5
    |
    +----------------------+
    |                      |
    v                      v
Summary                Key Points
    |                      |
    +----------+-----------+
               |
               v
       Download Results