# Website Content Chatbot with Gemini AI and Selenium
# Built for Streamlit frontend with semantic search capabilities

import streamlit as st
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
import torch
import requests
from urllib.parse import urljoin, urlparse
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="Website Chatbot with Gemini AI", 
    page_icon="🤖", 
    layout="wide"
)

st.title("🤖 Intelligent Website Chatbot")
st.markdown("Ask questions about any website content - powered by Gemini AI and semantic search")

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "website_content" not in st.session_state:
    st.session_state.website_content = []
if "embeddings" not in st.session_state:
    st.session_state.embeddings = None
if "encoder" not in st.session_state:
    st.session_state.encoder = None
if "last_url" not in st.session_state:
    st.session_state.last_url = ""

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
            st.error(f"Error setting up Chrome driver: {e}")
            self.driver = None
    
    def normalize_url(self, url):
        """Normalize URL by removing fragments and normalizing case"""
        parsed = urlparse(url)
        # Remove fragment and normalize
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
            
        # Skip certain file types and fragments
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.doc', '.docx']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
            
        # Skip anchor links on the same page
        if '#' in url and not parsed.path:
            return False
            
        return True
    
    def scrape_page(self, url):
        """Scrape content from a single page"""
        if not self.driver:
            return None
            
        try:
            self.driver.get(url)
            time.sleep(3)  # Allow page to load
            
            # Wait for body to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                pass
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "sidebar", "aside"]):
                script.decompose()
            
            # Extract title
            title = soup.title.string if soup.title else "No Title"
            
            # Extract main content
            content = soup.get_text()
            
            # Clean content
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Only return if we have substantial content
            if len(content.strip()) > 100:
                return {
                    'url': url,
                    'title': title.strip(),
                    'content': content[:10000]  # Increased content length limit
                }
                
        except Exception as e:
            st.error(f"Error scraping {url}: {e}")
            return None
    
    def scrape_website(self, base_url, max_pages=10):
        """Scrape multiple pages from a website"""
        scraped_content = []
        visited_urls = set()
        urls_to_visit = [self.normalize_url(base_url)]
        
        base_domain = urlparse(base_url).netloc.lower().replace('www.', '')
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        discovered_urls_text = st.empty()
        
        page_count = 0
        
        while urls_to_visit and page_count < max_pages:
            # Get the next URL to process
            current_url = urls_to_visit.pop(0)
            normalized_url = self.normalize_url(current_url)
            
            if normalized_url in visited_urls:
                continue
                
            page_count += 1
            status_text.text(f"Scraping page {page_count}/{max_pages}: {current_url}")
            progress_bar.progress(page_count / max_pages)
            
            # Show discovered URLs count
            discovered_urls_text.text(f"🔍 URLs discovered: {len(urls_to_visit) + len(visited_urls)}")
            
            page_content = self.scrape_page(current_url)
            if page_content:
                scraped_content.append(page_content)
                visited_urls.add(normalized_url)
                
                # Discover new links on this page
                try:
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    new_links_found = 0
                    
                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            if not href:
                                continue
                                
                            # Resolve relative URLs
                            absolute_url = urljoin(current_url, href)
                            normalized_new_url = self.normalize_url(absolute_url)
                            
                            # Check if it's a valid URL and same domain
                            if (self.is_valid_url(absolute_url) and 
                                self.is_same_domain(absolute_url, base_url) and
                                normalized_new_url not in visited_urls and 
                                normalized_new_url not in urls_to_visit):
                                
                                urls_to_visit.append(absolute_url)
                                new_links_found += 1
                                
                        except Exception as e:
                            continue
                            
                    # Limit the queue size to prevent memory issues
                    if len(urls_to_visit) > 100:
                        urls_to_visit = urls_to_visit[:100]
                        
                except Exception as e:
                    st.warning(f"Error extracting links from {current_url}: {e}")
            else:
                # Still mark as visited even if scraping failed
                visited_urls.add(normalized_url)
        
        progress_bar.empty()
        status_text.empty()
        discovered_urls_text.empty()
        
        # Show final statistics
        if scraped_content:
            st.info(f"✅ Successfully scraped {len(scraped_content)} pages from {base_domain}")
            st.info(f"📊 Total URLs discovered: {len(visited_urls) + len(urls_to_visit)}")
        
        return scraped_content
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

class SemanticSearch:
    def __init__(self):
        """Initialize the sentence transformer model"""
        try:
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            st.error(f"Error loading sentence transformer: {e}")
            self.encoder = None
    
    def create_embeddings(self, content_list):
        """Create embeddings for the scraped content"""
        if not self.encoder:
            return None
            
        try:
            # Prepare text chunks for embedding
            text_chunks = []
            metadata = []
            
            for item in content_list:
                # Split content into smaller chunks for better search
                content = item['content']
                chunk_size = 500
                words = content.split()
                
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i + chunk_size])
                    if len(chunk.strip()) > 50:  # Only include meaningful chunks
                        text_chunks.append(chunk)
                        metadata.append({
                            'url': item['url'],
                            'title': item['title'],
                            'chunk_index': i // chunk_size
                        })
            
            # Create embeddings
            if text_chunks:
                embeddings = self.encoder.encode(text_chunks, convert_to_tensor=True)
                return embeddings, text_chunks, metadata
            else:
                return None, None, None
                
        except Exception as e:
            st.error(f"Error creating embeddings: {e}")
            return None, None, None
    
    def search(self, query, embeddings, text_chunks, metadata, top_k=5):
        """Search for relevant content based on query"""
        if not self.encoder or embeddings is None:
            return []
            
        try:
            # Encode query
            query_embedding = self.encoder.encode(query, convert_to_tensor=True)
            
            # Calculate similarities
            hits = util.semantic_search(query_embedding, embeddings, top_k=top_k)[0]
            
            # Return relevant chunks with metadata
            results = []
            for hit in hits:
                if hit['score'] > 0.3:  # Only return results with decent similarity
                    results.append({
                        'content': text_chunks[hit['corpus_id']],
                        'score': hit['score'],
                        'metadata': metadata[hit['corpus_id']]
                    })
            
            return results
        except Exception as e:
            st.error(f"Error during search: {e}")
            return []

def generate_response_with_gemini(query, relevant_content, api_key):
    """Generate response using Gemini AI"""
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare context from relevant content
        context = ""
        for i, item in enumerate(relevant_content):
            context += f"\n\nSource {i+1} (from {item['metadata']['title']}):\n{item['content']}"
        
        # Create prompt
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
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating response: {e}"

# Main Streamlit Interface
def main():
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API Key input
        gemini_api_key = st.text_input("Gemini API Key", type="password", 
                                      help="Get your API key from Google AI Studio")
        
        # Website URL input
        website_url = st.text_input("Website URL", 
                                   help="Enter the website URL to scrape and chat about")
        
        # Max pages setting
        max_pages = st.slider("Max pages to scrape", 1, 50, 10)
        
        # Scrape button
        if st.button("🔍 Scrape Website", disabled=not (website_url and gemini_api_key)):
            if website_url != st.session_state.last_url:
                with st.spinner("Scraping website content..."):
                    # Initialize scraper
                    scraper = WebsiteScraper()
                    
                    if scraper.driver:
                        # Scrape content
                        content = scraper.scrape_website(website_url, max_pages)
                        scraper.close()
                        
                        if content:
                            st.session_state.website_content = content
                            st.session_state.last_url = website_url
                            
                            # Initialize semantic search
                            search_engine = SemanticSearch()
                            st.session_state.encoder = search_engine
                            
                            # Create embeddings
                            embeddings, text_chunks, metadata = search_engine.create_embeddings(content)
                            if embeddings is not None:
                                st.session_state.embeddings = embeddings
                                st.session_state.text_chunks = text_chunks
                                st.session_state.metadata = metadata
                                
                                st.success(f"✅ Scraped {len(content)} pages successfully!")
                                st.session_state.messages = []  # Clear previous conversation
                            else:
                                st.error("Failed to create embeddings")
                        else:
                            st.error("No content scraped. Please check the URL.")
                    else:
                        st.error("Failed to initialize web driver")
        
        # Display scraped content info
        if st.session_state.website_content:
            st.success(f"📄 {len(st.session_state.website_content)} pages loaded")
            
            with st.expander("View scraped pages"):
                for item in st.session_state.website_content:
                    st.write(f"**{item['title']}**")
                    st.caption(item['url'])
                    st.write(item['content'][:200] + "...")
                    st.divider()
    
    # Main chat interface
    st.header("Chat with Website Content")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about the website content...", 
                              disabled=not (st.session_state.website_content and gemini_api_key)):
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching and generating response..."):
                if (st.session_state.embeddings is not None and 
                    st.session_state.encoder and 
                    hasattr(st.session_state, 'text_chunks')):
                    
                    # Search for relevant content
                    relevant_content = st.session_state.encoder.search(
                        prompt, 
                        st.session_state.embeddings,
                        st.session_state.text_chunks,
                        st.session_state.metadata,
                        top_k=5
                    )
                    
                    if relevant_content:
                        # Generate response with Gemini
                        response = generate_response_with_gemini(prompt, relevant_content, gemini_api_key)
                        st.write(response)
                        
                        # Show sources
                        with st.expander("📚 Sources used"):
                            for i, item in enumerate(relevant_content):
                                st.write(f"**Source {i+1}:** {item['metadata']['title']}")
                                st.caption(f"Relevance: {item['score']:.2f} | URL: {item['metadata']['url']}")
                                st.write(item['content'][:300] + "...")
                                st.divider()
                        
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        error_msg = "No relevant content found for your query."
                        st.write(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    error_msg = "Please scrape a website first before asking questions."
                    st.write(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Instructions
    if not st.session_state.website_content:
        st.info("""
        ### 🚀 How to use this chatbot:
        
        1. **Enter your Gemini API Key** in the sidebar (get it from [Google AI Studio](https://aistudio.google.com/app/apikey))
        2. **Enter a website URL** you want to chat about
        3. **Set max pages to scrape** (recommended: 10-20 for most sites)
        4. **Click 'Scrape Website'** to extract and index the content
        5. **Start asking questions** about the website content
        
        The chatbot will automatically discover and scrape multiple pages within the same domain, then use semantic search to find relevant content and provide accurate answers.
        """)

if __name__ == "__main__":
    main()