import os
import re
import time
import uuid
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

class WikipediaCrawler:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WikipediaCrawler/1.0 (https://example.com; bot@example.com)"
        })
        
        # Initialize Qdrant client with Docker service name
        self.qdrant_host = os.getenv("QDRANT_HOST", "qdrant")  # Default to Docker service name
        self.qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
        
        # Initialize with retry mechanism for Docker startup
        self._init_qdrant_client()
        
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Collection configuration
        self.collection_name = "wikipedia_places"
        self.vector_size = 384
        
        # Initialize collection if it doesn't exist
        self._init_collection()
        
        # Keywords for classification
        self.place_keywords = [
            "town", "village", "city", "county", "castle", "abbey", "monastery",
            "lough", "river", "fort", "mount", "hill", "island", "peninsula", "park"
        ]
        self.attraction_keywords = [
            "museum", "zoo", "cathedral", "tower", "heritage", "landmark", "tourism",
            "visitor centre", "aquarium", "gallery", "tourist", "monument", "historical site"
        ]
        
        # Compile regex patterns
        self.place_regex = re.compile(rf"(?i)\b({'|'.join(self.place_keywords)})\b|^List of|^Geography of")
        self.attraction_regex = re.compile(rf"(?i)\b({'|'.join(self.attraction_keywords)})\b")
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests

    def _init_qdrant_client(self, max_retries=5, retry_delay=5):
        """Initialize Qdrant client with retry mechanism."""
        retry_count = 0
        while retry_count < max_retries:
            try:
                self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
                # Test connection
                self.client.get_collections()
                print(f"Successfully connected to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
                return
            except Exception as e:
                retry_count += 1
                print(f"Failed to connect to Qdrant (attempt {retry_count}/{max_retries}): {str(e)}")
                if retry_count < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        
        raise Exception("Failed to connect to Qdrant after maximum retries")

    def _init_collection(self):
        """Initialize Qdrant collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
                    hnsw_config=models.HnswConfigDiff(
                        m=16,
                        ef_construct=100,
                        full_scan_threshold=10000
                    ),
                    optimizers_config=models.OptimizersConfigDiff(
                        memmap_threshold=10000
                    )
                )
                print(f"Created new collection: {self.collection_name}")
                
                # Create a payload index for type field
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="type",
                    field_schema=models.PayloadSchemaType.KEYWORD
                )
        except Exception as e:
            print(f"Error initializing collection: {e}")
            raise

    def get_wikipedia_url(self, title: str) -> str:
        """Convert a page title to a full Wikipedia URL."""
        return urljoin(self.base_url, f"/wiki/{title.replace(' ', '_')}")

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a Wikipedia page with error handling and rate limiting."""
        try:
            time.sleep(self.request_delay)  # Respect rate limits
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_page_info(self, html: str, url: str) -> Dict:
        """Extract information from a Wikipedia page."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title
        title = soup.find("h1", {"id": "firstHeading"}).text if soup.find("h1", {"id": "firstHeading"}) else ""
        
        # Extract main content
        content_div = soup.find("div", {"id": "mw-content-text"})
        paragraphs = [p.get_text() for p in content_div.find_all("p")] if content_div else []
        content = " ".join(paragraphs)[:2000]  # Limit content size
        
        # Determine page type
        page_type = "other"
        if self.place_regex.search(title):
            page_type = "place"
        elif self.attraction_regex.search(title):
            page_type = "attraction"
        
        return {
            "title": title,
            "url": url,
            "content": content,
            "type": page_type,
            "timestamp": int(time.time())
        }

    def extract_links(self, html: str, source_url: str) -> List[Tuple[str, str]]:
        """Extract relevant links from a Wikipedia page."""
        soup = BeautifulSoup(html, "html.parser")
        links = soup.select("a[href^='/wiki/']")
        results = []
        
        for link in links:
            href = link.get("href")
            if not href or ':' in href or href.startswith('/wiki/Main_Page'):
                continue
            
            title = href.split("/wiki/")[-1].replace("_", " ")
            full_url = urljoin(self.base_url, href)
            
            if self.place_regex.search(title) or self.attraction_regex.search(title):
                results.append((title, full_url))
        
        return results

    def store_in_qdrant(self, page_info: Dict):
        """Store page information in Qdrant with embeddings."""
        try:
            # Generate embeddings using sentence transformer
            content_for_embedding = f"{page_info['title']} {page_info['content']}"
            vector = self.model.encode(content_for_embedding).tolist()
            
            # Generate a UUID for the point ID
            point_id = str(uuid.uuid4())
            
            point = PointStruct(
                id=point_id,  # Use UUID string as ID
                vector=vector,
                payload={
                    "title": page_info["title"],
                    "url": page_info["url"],
                    "type": page_info["type"],
                    "content": page_info["content"],
                    "timestamp": page_info["timestamp"]
                }
            )
            
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                wait=True,
                points=[point]
            )
            
            return operation_info
        except Exception as e:
            print(f"Error storing in Qdrant: {e}")
            return None

    def crawl(self, start_titles: List[str], max_depth: int = 2):
        """Crawl Wikipedia starting from the given titles."""
        visited_urls = set()
        queue = [(title, 1) for title in start_titles]
        
        with tqdm(desc="Crawling Wikipedia") as pbar:
            while queue:
                current_title, depth = queue.pop(0)
                url = self.get_wikipedia_url(current_title)
                
                if url in visited_urls or depth > max_depth:
                    continue
                
                # Fetch and process the page
                html = self.fetch_page(url)
                if not html:
                    continue
                
                page_info = self.extract_page_info(html, url)
                self.store_in_qdrant(page_info)
                
                visited_urls.add(url)
                pbar.set_postfix({"depth": depth, "queue": len(queue), "visited": len(visited_urls)})
                pbar.update(1)
                
                # Process links if we're not at max depth
                if depth < max_depth:
                    links = self.extract_links(html, url)
                    for title, link_url in links:
                        if link_url not in visited_urls:
                            queue.append((title, depth + 1))

    def search_places(self, query: str, limit: int = 10):
        """Search for places in the Qdrant database."""
        try:
            # Generate query vector
            query_vector = self.model.encode(query).tolist()
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=models.Filter(
                    must=[models.FieldCondition(key="type", match=models.MatchValue(value="place"))]
                ),
                limit=limit
            )
            
            return [{"title": hit.payload["title"], "url": hit.payload["url"]} for hit in results]
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return []


if __name__ == "__main__":
    print("Initializing Wikipedia Crawler...")
    
    # List of Irish counties to start crawling from
    start_titles = [
        "County Galway", "County Leitrim", "County Mayo", "County Roscommon", "County Sligo",
        "County Carlow", "County Dublin", "County Kildare", "County Kilkenny", "County Laois",
        "County Longford", "County Louth", "County Meath", "County Offaly", "County Westmeath",
        "County Wexford", "County Wicklow", "County Clare", "County Cork", "County Kerry",
        "County Limerick", "County Tipperary", "County Waterford", "County Cavan", "County Donegal",
        "County Monaghan"
    ]
    
    try:
        crawler = WikipediaCrawler()
        print("Starting crawl process...")
        crawler.crawl(start_titles, max_depth=2)
        
        print("\nCrawl completed successfully!")
        
        # Example search
        print("\nExample search results for places:")
        results = crawler.search_places("historical places in Ireland")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']} - {result['url']}")
            
    except Exception as e:
        print(f"Error during crawl process: {e}")
        raise 