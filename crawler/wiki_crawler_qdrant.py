import os
from time import sleep
from qdrant_client import QdrantClient

# Get Qdrant connection details from environment variables
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# Initialize Qdrant client with Docker service name
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

if __name__ == "__main__":
    # Wait for Qdrant to be ready
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Test connection
            client.get_collections()
            print("Successfully connected to Qdrant")
            break
        except Exception as e:
            print(f"Failed to connect to Qdrant (attempt {retry_count + 1}/{max_retries}): {str(e)}")
            retry_count += 1
            sleep(5)
    
    if retry_count == max_retries:
        print("Failed to connect to Qdrant after maximum retries")
        exit(1)

    # First crawl the data
    print("Starting crawler with depth 2...")
    MAX_DEPTH = 2  # Ensure depth is set to 2
    crawl_wikipedia(START_TITLES, MAX_DEPTH)
    print("\n✅ Crawling complete. Data stored in Qdrant.")
    
    # Example searches demonstrating different filtering options
    print("\nTesting search functionality...")
    
    try:
        # ... rest of the existing code ... 