# DevOps Interns – AI Data Extraction and Analysis Suite

## Overview
This repository contains two Python-based automation modules developed as part of the DevOps Internship tasks.  
Both focus on intelligent data extraction, analysis, and insight generation using Regex, Machine Learning, OCR, and Generative AI.

---

## Modules

### Task 1 – Transaction Value Extractor

This module processes raw transaction logs, PDFs, or images to automatically extract transaction data such as type, amount, ID, and currency.  
It applies machine learning for anomaly detection and provides analytical visualization through an interactive Gradio interface.

#### Key Features
- Extracts transaction details using Regex pattern matching  
- Supports text, PDF, and image input formats  
- OCR integration for scanned files using Tesseract  
- Anomaly detection using Isolation Forest  
- Interactive data visualization with summary metrics  

## To Execute: python task1.py
---

### Task 2 – Bank Statement Parser

This component extracts and structures data from bank statements (PDF or image) and generates concise financial insights using the Gemini AI model.  
It returns a structured JSON output with account details, transaction summaries, and AI-generated insights.

#### Key Features
- Extracts structured data using Gemini (Google Generative AI)  
- Supports both PDF and image-based statements  
- OCR fallback for scanned or non-text PDFs  
- Automatic masking of sensitive account numbers  
- Generates summarized insights and metadata for quality assessment  

### To Execute: python task2.py <path_to_statement.pdf> --test
---

## Tech Stack
- **Programming Language:** Python 3.10+  
- **Libraries:**  
  - Regular Expressions (re)  
  - pandas, matplotlib, seaborn  
  - scikit-learn (IsolationForest)  
  - pdfplumber, PyPDF2  
  - pytesseract, Pillow  
  - gradio  
  - google-generativeai  

