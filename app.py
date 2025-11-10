# app.py
import os
import time
import re

# --- Silence TF Warnings ---
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress TF info and warnings
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
# --- End Silence ---

from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
import torch
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Load environment variables
load_dotenv()

# --- Flask App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_default_key_fallback')

# --- In-Memory Cache ---
app_cache = {
    "embeddings": None,
    "text_chunks": None,
    "metadata": None,
    "last_url": None,
    "encoder": None 
}


# --- Helper Classes & Functions (Unchanged) ---

class WebsiteScraper:
    def __init__(self):
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with optimized options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}") 
            self.driver = None
    
    def normalize_url(self, url):
        """Normalize URL by removing fragments and normalizing case"""
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized.rstrip('/')
    
    def is_same_domain(self, url1, url2):
        """Check if two URLs belong to the same domain"""
        domain1 = urlparse(url1).netloc.lower().replace('www.', '')
        domain2 = urlparse(url2).netloc.lower().replace('www.', '')
        return domain1 == domain2
    
    def is_valid_url(self, url):
        """Check if URL is valid for scraping"""
        if not url:
            return False
        
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
            
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.doc', '.docx']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
            
        if '#' in url and not parsed.path:
            return False
            
        return True
    
    def scrape_page(self, url):
        """Scrape content from a single page"""
        if not self.driver:
            return None
            
        try:
            self.driver.get(url)
            time.sleep(3) 
            
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                pass
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            for script in soup(["script", "style", "nav", "footer", "header", "sidebar", "aside"]):
                script.decompose()
            
            title = soup.title.string if soup.title else "No Title"
            content = soup.get_text()
            
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            if len(content.strip()) > 100:
                return {
                    'url': url,
                    'title': title.strip(),
                    'content': content[:10000]
                }
                
        except Exception as e:
            print(f"Error scraping {url}: {e}") 
            return None
    
    def scrape_website(self, base_url, max_pages=10):
        """Scrape multiple pages from a website"""
        scraped_content = []
        visited_urls = set()
        urls_to_visit = [self.normalize_url(base_url)]
        
        base_domain = urlparse(base_url).netloc.lower().replace('www.', '')
        page_count = 0
        
        while urls_to_visit and page_count < max_pages:
            current_url = urls_to_visit.pop(0)
            normalized_url = self.normalize_url(current_url)
            
            if normalized_url in visited_urls:
                continue
                
            page_count += 1
            print(f"Scraping page {page_count}/{max_pages}: {current_url}") 
            
            page_content = self.scrape_page(current_url)
            if page_content:
                scraped_content.append(page_content)
                visited_urls.add(normalized_url)
                
                try:
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    
                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            if not href:
                                continue
                                
                            absolute_url = urljoin(current_url, href)
                            normalized_new_url = self.normalize_url(absolute_url)
                            
                            if (self.is_valid_url(absolute_url) and 
                                self.is_same_domain(absolute_url, base_url) and
                                normalized_new_url not in visited_urls and 
                                normalized_new_url not in urls_to_visit):
                                
                                urls_to_visit.append(absolute_url)
                                
                        except Exception as e:
                            continue
                            
                    if len(urls_to_visit) > 100:
                        urls_to_visit = urls_to_visit[:100]
                        
                except Exception as e:
                    print(f"Warning: Error extracting links from {current_url}: {e}")
            else:
                visited_urls.add(normalized_url)
        
        print(f"Scraping complete. Scraped {len(scraped_content)} pages.")
        return scraped_content
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

class SemanticSearch:
    def __init__(self):
        """Initialize the sentence transformer model"""
        try:
            # Check if encoder is already loaded in cache
            if app_cache.get("encoder"):
                self.encoder = app_cache["encoder"]
            else:
                self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
                app_cache["encoder"] = self.encoder # Store it
        except Exception as e:
            print(f"Error loading sentence transformer: {e}")
            self.encoder = None
    
    def create_embeddings(self, content_list):
        """Create embeddings for the scraped content"""
        if not self.encoder:
            return None
            
        try:
            text_chunks = []
            metadata = []
            
            for item in content_list:
                content = item['content']
                chunk_size = 500
                words = content.split()
                
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i + chunk_size])
                    if len(chunk.strip()) > 50:
                        text_chunks.append(chunk)
                        metadata.append({
                            'url': item['url'],
                            'title': item['title'],
                            'chunk_index': i // chunk_size
                        })
            
            if text_chunks:
                embeddings = self.encoder.encode(text_chunks, convert_to_tensor=True)
                return embeddings, text_chunks, metadata
            else:
                return None, None, None
                
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return None, None, None
    
    def search(self, query, embeddings, text_chunks, metadata, top_k=5):
        """Search for relevant content based on query"""
        if not self.encoder or embeddings is None:
            return []
            
        try:
            query_embedding = self.encoder.encode(query, convert_to_tensor=True)
            hits = util.semantic_search(query_embedding, embeddings, top_k=top_k)[0]
            
            results = []
            for hit in hits:
                if hit['score'] > 0.3:
                    results.append({
                        'content': text_chunks[hit['corpus_id']],
                        'score': hit['score'],
                        'metadata': metadata[hit['corpus_id']]
                    })
            
            return results
        except Exception as e:
            print(f"Error during search: {e}")
            return []

def generate_response_with_gemini(query, relevant_content, api_key):
    """Generate response using Gemini AI"""
    try:
        genai.configure(api_key=api_key)
        
        # ******** THE FIX IS HERE ********
        # Switched to the more stable 'gemini-2.5-flash' model
        model = genai.GenerativeModel('gemini-2.5-flash')
        # ******** END OF FIX ********

        context = ""
        for i, item in enumerate(relevant_content):
            context += f"\n\nSource {i+1} (from {item['metadata']['title']}):\n{item['content']}"
        
        prompt = f"""Based on the following website content, please answer the user's question accurately and helpfully.

Website Content:
{context}

User Question: {query}

Instructions:
1. Answer based only on the provided website content
2. If the information isn't available in the content, say so
3. Include relevant source references when possible
4. Be concise but comprehensive
5. If you reference specific information, mention which source it came from

Answer:"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"Error generating response: {e}"

# --- Flask API Endpoints ---

@app.route("/")
def index():
    """Serve the main HTML page"""
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape():
    """
    Scrape the website and store content and embeddings in the global app_cache
    """
    data = request.json
    website_url = data.get("url")
    max_pages = int(data.get("max_pages", 10))
    api_key = data.get("api_key")

    if not website_url or not api_key:
        return jsonify({"error": "URL and API Key are required"}), 400

    # Store API key in session (this is small, so it's fine)
    session["gemini_api_key"] = api_key

    # Check cache
    if app_cache.get("last_url") == website_url and app_cache.get("embeddings") is not None:
        return jsonify({
            "message": f"Content from {website_url} is already loaded",
            "pages_scraped": len(app_cache.get("metadata", [])) 
        })

    scraper = WebsiteScraper()
    if not scraper.driver:
        return jsonify({"error": "Failed to initialize web driver"}), 500
        
    content = scraper.scrape_website(website_url, max_pages)
    scraper.close()

    if not content:
        return jsonify({"error": "No content scraped. Please check the URL."}), 400
    
    # Create and store in server-side cache
    search_engine = SemanticSearch() # This will load/get the encoder
    embeddings, text_chunks, metadata = search_engine.create_embeddings(content)
    
    if embeddings is None:
        return jsonify({"error": "Failed to create embeddings from content"}), 500

    # Store data in our server-side cache
    app_cache["last_url"] = website_url
    app_cache["text_chunks"] = text_chunks
    app_cache["metadata"] = metadata
    app_cache["embeddings"] = embeddings # Store the actual tensor
    
    return jsonify({
        "message": f"Successfully scraped {len(content)} pages",
        "pages_scraped": len(content)
    })

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle a chat message, perform search, and get Gemini response
    """
    data = request.json
    query = data.get("query")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Check if content is loaded in our global cache
    if (app_cache.get("embeddings") is None or 
        app_cache.get("text_chunks") is None or
        app_cache.get("encoder") is None): # Check if encoder was loaded
        return jsonify({"error": "Please scrape a website first"}), 400
        
    api_key = session.get("gemini_api_key") # Get API key from the small session
    if not api_key:
        return jsonify({"error": "API Key not found. Please scrape the website again."}), 400

    # --- Perform Semantic Search ---
    
    # 1. Create an instance of our SemanticSearch class.
    search_engine = SemanticSearch()

    # 2. Get the rest of the data from the cache
    embeddings_tensor = app_cache["embeddings"]
    text_chunks = app_cache["text_chunks"]
    metadata = app_cache["metadata"]
    
    # 3. Now, call the .search() method on the SemanticSearch instance
    relevant_content = search_engine.search(
        query, 
        embeddings_tensor, 
        text_chunks, 
        metadata, 
        top_k=5
    )

    if not relevant_content:
        response = "I couldn't find any relevant content on the website to answer your question."
        sources = []
    else:
        # Generate response with Gemini
        response = generate_response_with_gemini(query, relevant_content, api_key)
        # Prepare sources to send back to frontend
        sources = [
            {
                "title": item['metadata']['title'],
                "url": item['metadata']['url'],
                "score": item['score'],
                "content": item['content'][:200] + "..." # Snippet
            } for item in relevant_content
        ]

    return jsonify({
        "response": response,
        "sources": sources
    })

# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True)