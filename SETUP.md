# Website Content Chatbot Setup & Usage Guide

## Overview
This chatbot scrapes website content using Selenium, creates searchable embeddings using sentence-transformers, and provides intelligent answers using Google's Gemini AI - all within a Streamlit interface.

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Chrome Driver
- Download ChromeDriver from https://chromedriver.chromium.org/
- Add ChromeDriver to your PATH or place in project directory

### 3. Get Gemini API Key
- Visit https://aistudio.google.com/app/apikey
- Create a free API key
- Create `.env` file and add: `GEMINI_API_KEY=your_key_here`

### 4. Run the Application
```bash
streamlit run website_chatbot.py
```
