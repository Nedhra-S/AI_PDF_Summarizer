# 🤖 AI PDF Summarizer

An AI-powered PDF summarization application built using **Python, Streamlit, Ollama, and Qwen 2.5**.

The application allows users to upload a PDF document, automatically identify the type of document, extract important information, and generate a concise summary and separate key points using a locally running AI model.

---

## 📌 Project Overview

Reading and understanding long PDF documents can be time-consuming.

The **AI PDF Summarizer** simplifies this process by automatically processing the uploaded document and generating:

- 📄 A complete document summary
- 🔑 Important key points
- 📂 Automatic document type detection
- ⬇️ Downloadable summary
- ⬇️ Downloadable key points

The application uses **Ollama with the Qwen 2.5 3B model**, allowing AI processing to run locally on the user's computer.

---

## ✨ Features

### 🔐 Login System
A simple login system protects access to the application.

### 📄 PDF Upload
Users can upload PDF documents directly through the Streamlit interface.

### 📚 Full-Document Processing
The application extracts text from the uploaded PDF and processes the document section by section.

### 📂 Document Type Detection
The application automatically identifies the document type, such as:

- Lecture Notes
- Resume / CV
- Guidelines / Instructions
- Research Paper
- Report
- Study Material
- Article
- Business Document
- Other

### 📝 AI Summary
Generates a concise summary based on the important information found throughout the document.

### 🔑 Separate Key Points
Generates distinct key points separately from the summary to make important information easier to review.

### 🤖 Local AI Processing
Uses **Ollama and Qwen 2.5 3B** for local AI processing.

### ⬇️ Download Results
Users can download:

- Summary
- Key Points

### 🚪 Logout
The logout function clears the current document and generated results so that a new session starts without displaying previous PDF information.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web application interface |
| PyPDF | PDF text extraction |
| Ollama | Local AI model execution |
| Qwen 2.5 3B | AI text analysis and summarization |
| Git & GitHub | Version control and project hosting |

---

## 🔄 How It Works

```text
                PDF Upload
                    ↓
             Text Extraction
                    ↓
          Document Type Detection
                    ↓
            Document Processing
                    ↓
       Important Information Extraction
                    ↓
          AI Analysis with Qwen
                    ↓
          ┌─────────┴─────────┐
          ↓                   ↓
       Summary           Key Points
          ↓                   ↓
          └─────────┬─────────┘
                    ↓
              Download Results