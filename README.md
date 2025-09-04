# 🤖 Scrapy-AI: Intelligent Website Chatbot  

Scrapy-AI is a **Streamlit-based chatbot** that lets you interact with and query website content in real time.  
It combines **Selenium web scraping**, **semantic search with Sentence Transformers**, and **Gemini AI** to provide accurate, reference-backed answers from any website.  

---

## 🚀 How It Works  

### 1. **Web Scraping with Selenium**  
- Scrapes multiple pages with headless Chrome  
- Extracts clean, text-only content  
- Handles dynamic, JavaScript-heavy sites  

### 2. **Semantic Search with Sentence Transformers**  
- Uses `all-MiniLM-L6-v2` for embeddings  
- Splits text into 500-word chunks  
- Enables Google-like semantic relevance search  

### 3. **AI Response Generation with Gemini**  
- Retrieves relevant content chunks for each query  
- Generates concise, reference-backed answers  
- Displays source pages for transparency  

---

## ✨ Key Features  

✅ **Streamlit UI** – clean, interactive interface  
✅ **Selenium Scraper** – works on dynamic websites  
✅ **Semantic Search** – fast, accurate content discovery  
✅ **Gemini AI Integration** – intelligent response generation  
✅ **Source References** – see exactly where answers came from  
✅ **No Database Needed** – in-memory embeddings  
✅ **Progress Tracking** – shows scraping progress  

---

## 📸 Screenshots  

### Website Example (Quiddity Engineering)  
![Website Example](assets/website.png)  <img width="1308" height="534" alt="image" src="https://github.com/user-attachments/assets/adc90f25-b06c-4973-a427-da6c5279ba41" />


### Scrapy-AI in Action  
![Chatbot Example](assets/chatbot.png)  <img width="1344" height="557" alt="image" src="https://github.com/user-attachments/assets/5f6b334c-8436-4e28-adaa-52802f12cf6f" />


---

## 💬 Example Queries  

- "What are the main services offered?"  
- "Summarize the pricing information."  
- "What is the company’s contact information?"  
- "Explain the featured projects."  

---

## 🏗️ Technical Architecture  

### Block Diagram  
![Technical Architecture](assets/architecture.png)  

### Data Flow  
1. **Website Scraping (Selenium + BeautifulSoup)**  
   - Headless Chrome loads pages  
   - Extracts cleaned text (removes scripts, nav, etc.)  
   - Discovers and crawls multiple internal links  

2. **Content Processing & Indexing**  
   - Text split into 500-word chunks  
   - Sentence Transformers (`all-MiniLM-L6-v2`) generate embeddings  
   - Stored in memory for fast semantic search  

3. **Query Handling**  
   - User inputs query in Streamlit chat  
   - Query embedding compared against content embeddings  
   - Most relevant chunks retrieved  

4. **AI Answer Generation**  
   - Relevant chunks passed to **Gemini AI**  
   - Gemini generates accurate, reference-backed response  
   - Sources displayed for transparency  

---

## ⚙️ Customization  

- **Embedding Model** → switch from `all-MiniLM-L6-v2` to other [Sentence Transformers](https://www.sbert.net/docs/pretrained_models.html)  
- **Chunk Size** → adjust (default 500 words) for finer-grained search  
- **Top-k Results** → increase/decrease retrieved chunks  
- **Gemini Model** → choose `gemini-2.0-flash`, `gemini-pro`, etc.  

---

## 📂 Project Structure  

```
project/
├── website_chatbot.py    # Main Streamlit app
├── requirements.txt      # Dependencies
├── .env                  # API key file (ignored in git)
├── env_template.txt      # Template for .env
├── assets/               # Folder for screenshots & diagrams
│   ├── website.png
│   ├── chatbot.png
│   └── architecture.png
└── README.md             # Project guide
```

---

## 📈 Roadmap  

- [ ] Add conversation memory  
- [ ] Support PDF, DOCX, and other formats  
- [ ] Implement caching for faster queries  
- [ ] Add user feedback system  
- [ ] Deploy to Streamlit Cloud or Docker  

---

## 📜 License  

MIT License. Free to use and modify.  
