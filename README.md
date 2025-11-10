# 🤖 Scrapy-AI: Intelligent Website Chatbot  

**Scrapy-AI** is an advanced **Flask-based AI chatbot** that allows users to interact with and query website content in real time.  
It integrates **Selenium for web scraping**, **Sentence Transformers for semantic search**, and **Gemini AI** for intelligent, reference-backed responses — all wrapped in a sleek **HTML, CSS, and JavaScript frontend**.  

🌐 **Live Demo:** [Scrapy-AI App](https://scrapy-ai-5tsbwye2gyggfqhcflegqn.streamlit.app/)

---

## 🚀 How It Works  

### 1. **Web Scraping with Selenium**  
- Uses headless Chrome to scrape content from multiple pages  
- Handles JavaScript-heavy and dynamic websites  
- Cleans and extracts only relevant text  

### 2. **Semantic Search with Sentence Transformers**  
- Uses the `all-MiniLM-L6-v2` model to embed website text  
- Splits text into 500-word chunks for better context  
- Performs efficient similarity matching for relevant information  

### 3. **AI-Powered Responses with Gemini**  
- Retrieves the most relevant website chunks  
- Generates human-like, reference-backed answers using Gemini  
- Displays exact source links for transparency  

---

## ✨ Key Features  

✅ **Flask Backend** – lightweight, fast, and scalable  
✅ **HTML, CSS, JS Frontend** – clean, responsive chatbot interface  
✅ **Selenium Scraper** – handles dynamic and interactive web pages  
✅ **Semantic Search** – powered by Sentence Transformers  
✅ **Gemini AI Integration** – generates accurate responses  
✅ **Source References** – see where answers came from  
✅ **No Database Needed** – runs completely in memory  

---

## 💻 Frontend Overview  

Built using:
- **HTML5** → chatbot structure and layout  
- **CSS3** → modern responsive design  
- **Vanilla JavaScript** → handles message interactivity and API calls  

**UI Features:**
- Real-time chatbot messages  
- Loading animation while fetching responses  
- Smooth scrolling chat window  
- Works on both desktop and mobile  

---

## 💬 Example Queries  

- “What are the main services offered?”  
- “Summarize the pricing information.”  
- “What is the company’s contact info?”  
- “Explain the featured projects.”  

---

## 🏗️ Technical Architecture  

### 🔹 System Workflow  

1. **Frontend (HTML/CSS/JS)**  
   - Displays chatbot UI  
   - Sends queries to the Flask backend via REST API  

2. **Backend (Flask + Python)**  
   - Uses **Selenium + BeautifulSoup** to scrape website data  
   - Generates text embeddings using **Sentence Transformers**  
   - Performs semantic search to find relevant text chunks  

3. **AI Integration (Gemini API)**  
   - Sends relevant chunks to **Gemini**  
   - Returns summarized and contextual responses with source links  

---

## ⚙️ Customization  

| Component | Description | Example |
|------------|--------------|---------|
| **Embedding Model** | Choose a different Sentence Transformer | `paraphrase-MiniLM-L12-v2` |
| **Chunk Size** | Adjust how much text is processed per chunk | Default: 500 words |
| **Top-k Results** | Change how many chunks are retrieved | Default: 5 |
| **Gemini Model** | Switch to other Gemini versions | `gemini-2.0-flash`, `gemini-pro` |
| **Frontend Style** | Customize chatbot look and feel | Edit `static/style.css` |

---

## 📂 Project Structure  

```
/your-project-folder/
├── app.py                 # The main Flask application and backend logic
├── .env                   # Environment variables (Flask secret key, API keys)
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # The main HTML frontend
└── static/
    ├── style.css          # The CSS for styling
    └── script.js          # The JavaScript for interactivity
```

---

## ⚙️ Setup & Run Instructions  

### 1. Clone the Repository  
```bash
git clone https://github.com/yourusername/scrapy-ai.git
cd scrapy-ai
```

### 2. Create a Virtual Environment  
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies  
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables  
Create a `.env` file in your project root:  
```
FLASK_SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Run the Flask App  
```bash
python app.py
```

Then open your browser at:  
👉 **http://localhost:5000**

---

## 📈 Roadmap  

- [ ] Add chat memory and context retention  
- [ ] Support PDF, DOCX, and text file inputs  
- [ ] Implement caching for faster responses  
- [ ] Add user feedback and ratings  
- [ ] Add dark/light mode switch  
- [ ] Docker + Vercel deployment support  

---

## 📜 License  

**MIT License**  
Free to use, modify, and distribute.

---

## 📞 Contact  

For issues or suggestions:  
📧 **jejjari.vinay@gmail.com**  
💬 Open a GitHub issue for feature requests or bug reports.
