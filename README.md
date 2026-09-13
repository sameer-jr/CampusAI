# CampusAI

CampusAI is a multilingual, retrieval-based AI student support assistant for higher-education institutions. It uses Google Gemini to generate answers from selected campus records instead of relying on general web knowledge.

## Features

- English, Tamil, and Sinhala support
- Retrieval before generation
- Source-aware answers
- Hallucination protection for unsupported questions
- Modular JSON knowledge base
- Streamlit chat interface
- Gemini API integration

## How it works

```text
Student question
      |
      v
CampusAI Retriever
      |
      v
Relevant campus records
      |
      v
Google Gemini
      |
      v
Grounded multilingual answer + source
