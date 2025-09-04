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

## How It Works

### 1. **Web Scraping with Selenium**
- Uses headless Chrome to scrape website content
- Extracts clean text from multiple pages
- Handles JavaScript-heavy websites

### 2. **Semantic Search with Sentence Transformers**
- Creates vector embeddings using `all-MiniLM-L6-v2` model
- Splits content into searchable chunks
- Enables Google-like semantic search capabilities

### 3. **AI Response Generation with Gemini**
- Retrieves most relevant content chunks for user queries
- Passes context to Gemini AI for accurate answers
- Provides source references for transparency

## Key Features

✅ **Streamlit Frontend** - Clean, interactive web interface
✅ **Selenium Web Scraping** - Handles dynamic websites
✅ **Semantic Search** - Finds relevant content like Google
✅ **Gemini AI Integration** - Intelligent answer generation
✅ **Source References** - Shows which pages answers came from
✅ **In-Memory Storage** - No database required
✅ **Progress Tracking** - Visual feedback during scraping

## Usage Instructions

1. **Enter API Key**: Add your Gemini API key in the sidebar
2. **Enter Website URL**: Specify the website to scrape
3. **Set Max Pages**: Choose how many pages to scrape (1-20)
4. **Click "Scrape Website"**: Wait for content extraction and indexing
5. **Ask Questions**: Chat about the website content naturally

## Example Queries

- "What are the main services offered?"
- "How much does it cost?"
- "What is the company's contact information?"
- "Summarize the key features of their product"

## Troubleshooting

### Chrome Driver Issues
- Install ChromeDriver: `pip install chromedriver-autoinstaller`
- Or download manually and add to PATH

### API Key Problems
- Ensure `.env` file is in the same directory
- Check API key is valid at Google AI Studio
- Verify sufficient quota in your account

### Memory Issues
- Reduce max_pages if scraping large sites
- Restart the application to clear memory

## Technical Architecture

```
User Query → Semantic Search → Relevant Content → Gemini AI → Response
     ↑                                                           ↓
Website Scraping → Content Chunking → Vector Embeddings → Source References
```

## Customization Options

- **Embedding Model**: Change `all-MiniLM-L6-v2` to other sentence-transformers models
- **Chunk Size**: Modify chunk_size in SemanticSearch class (default: 500 words)
- **Search Results**: Adjust top_k parameter for more/fewer relevant chunks
- **Gemini Model**: Switch between gemini-1.5-flash, gemini-pro, etc.

## File Structure
```
project/
├── website_chatbot.py    # Main application
├── requirements.txt      # Dependencies
├── .env                  # API keys (create from template)
├── env_template.txt      # Template for .env file
└── README.md            # This guide
```

## Performance Tips

1. **Start Small**: Test with 2-3 pages first, then increase
2. **Clear Memory**: Restart app if it becomes slow
3. **Optimize Queries**: Be specific in your questions
4. **Monitor Usage**: Check Gemini API quota regularly

## Next Steps for Enhancement

- Add conversation memory
- Support multiple file formats (PDF, DOCX)
- Implement caching for faster responses
- Add user feedback system
- Deploy to cloud platform