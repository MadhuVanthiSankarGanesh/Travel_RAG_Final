import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Set, Tuple, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import hashlib
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Initialize Qdrant client and embedding model
client = QdrantClient("localhost", port=6333)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Constants
BASE_WIKI_URL = "https://en.wikipedia.org"
COLLECTION_NAME = "ireland_places"
MAX_DEPTH = 2

START_TITLES = [
    # Counties
    "County Galway", "County Leitrim", "County Mayo", "County Roscommon", "County Sligo",
    "County Carlow", "County Dublin", "County Kildare", "County Kilkenny", "County Laois",
    "County Longford", "County Louth", "County Meath", "County Offaly", "County Westmeath",
    "County Wexford", "County Wicklow", "County Clare", "County Cork", "County Kerry",
    "County Limerick", "County Tipperary", "County Waterford", "County Cavan", "County Donegal",
    "County Monaghan",
    
    # Major Cities and Towns
    "Dublin", "Cork (city)", "Galway", "Limerick (city)", "Waterford (city)",
    "Kilkenny (city)", "Sligo (town)", "Killarney", "Dingle", "Westport", "Bundoran",
    
    # Famous Tourist Regions
    "Wild Atlantic Way", "Ring of Kerry", "Connemara", "The Burren",
    "Cliffs of Moher", "Giant's Causeway", "Skellig Islands",
    
    # Historical Sites
    "Rock of Cashel", "Newgrange", "Hill of Tara", "Glendalough",
    "Bunratty Castle", "Blarney Castle", "Dublin Castle", "Kilmainham Gaol",
    
    # Natural Attractions
    "Killarney National Park", "Connemara National Park", "Wicklow Mountains",
    "Glenveagh National Park", "Lakes of Killarney", "River Shannon",
    
    # Cultural Topics
    "Irish culture", "Traditional Irish music", "Irish cuisine",
    "Irish pub culture", "Irish dance", "Celtic culture",
    
    # Modern Attractions
    "Guinness Storehouse", "Titanic Belfast", "Trinity College, Dublin",
    "St Patrick's Cathedral, Dublin", "Phoenix Park",
    
    # Islands
    "Aran Islands", "Achill Island", "Skellig Michael", "Valentia Island",
    
    # Historic Routes
    "Ireland's Ancient East", "Causeway Coastal Route", "Slea Head Drive",
    
    # Gardens
    "Powerscourt Gardens", "National Botanic Gardens (Ireland)", "Muckross House"
]

PLACE_KEYWORDS = [
    # Existing keywords
    "town", "village", "city", "county", "castle", "abbey", "monastery",
    "lough", "river", "fort", "mount", "hill", "island", "peninsula", "park",
    
    # Additional location types
    "beach", "cliff", "bay", "harbour", "glen", "valley", "garden",
    "forest", "woods", "lake", "waterfall", "cave", "strand",
    
    # Historical places
    "ruins", "tower house", "round tower", "dolmen", "ring fort",
    "stone circle", "holy well", "ancient site",
    
    # Modern places
    "resort", "marina", "pier", "promenade", "viewpoint",
    "trail", "walking route", "golf course"
]

ATTRACTION_KEYWORDS = [
    # Existing keywords
    "museum", "zoo", "cathedral", "tower", "heritage", "landmark", "tourism",
    "visitor centre", "aquarium", "gallery", "tourist", "monument", "historical site",
    
    # Cultural attractions
    "festival", "music venue", "theatre", "arts centre", "cultural center",
    "craft center", "brewery", "distillery", "folk park",
    
    # Activities
    "surfing", "hiking", "climbing", "fishing", "sailing", "kayaking",
    "horse riding", "cycling route", "walking tour",
    
    # Entertainment
    "entertainment", "nightlife", "shopping district", "market",
    "food hall", "concert venue",
    
    # Accommodation
    "historic hotel", "castle hotel", "manor house", "country house",
    
    # Religious sites
    "church", "friary", "religious site", "pilgrimage",
    
    # Transportation heritage
    "railway station", "historic port", "lighthouse", "bridge",
    
    # Sports venues
    "stadium", "race course", "sports venue"
]

# Additional filter to identify tourism-related content
TOURISM_KEYWORDS = [
    "tourism", "tourist", "visit", "attraction", "guide",
    "heritage", "historic", "sightseeing", "tour", "travel",
    "accommodation", "hotel", "restaurant", "pub", "café",
    "festival", "event", "experience", "activity", "adventure"
]

PLACE_REGEX = re.compile(rf"(?i)\b({'|'.join(PLACE_KEYWORDS)})\b|^List of|^Geography of")
ATTRACTION_REGEX = re.compile(rf"(?i)\b({'|'.join(ATTRACTION_KEYWORDS)})\b")
TOURISM_REGEX = re.compile(rf"(?i)\b({'|'.join(TOURISM_KEYWORDS)})\b")

class LocationType(str, Enum):
    COUNTY = "county"
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    NATURAL = "natural"
    HISTORICAL = "historical"
    CULTURAL = "cultural"
    ENTERTAINMENT = "entertainment"
    ACCOMMODATION = "accommodation"
    UNKNOWN = "unknown"

class AttractionCategory(str, Enum):
    HERITAGE = "heritage"
    NATURE = "nature"
    CULTURE = "culture"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    FOOD_DRINK = "food_drink"
    SHOPPING = "shopping"
    ACCOMMODATION = "accommodation"
    TRANSPORT = "transport"
    UNKNOWN = "unknown"

@dataclass
class LocationMetadata:
    name: str
    type: LocationType
    county: Optional[str] = None
    region: Optional[str] = None
    coordinates: Optional[Tuple[float, float]] = None

@dataclass
class AttractionMetadata:
    name: str
    category: AttractionCategory
    location: LocationMetadata
    features: List[str]
    price_range: Optional[str] = None
    opening_hours: Optional[str] = None
    accessibility: Optional[str] = None

def setup_qdrant():
    """Initialize Qdrant collection with payload indexes"""
    collections = client.get_collections().collections
    if not any(collection.name == COLLECTION_NAME for collection in collections):
        # Create collection with vector configuration
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            )
        )
        
        # Create payload indexes for efficient filtering and searching
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="type",
            field_schema="keyword"
        )
        
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="location_type",
            field_schema="keyword"
        )
        
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="attraction_category",
            field_schema="keyword"
        )
        
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="county",
            field_schema="keyword"
        )
        
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="region",
            field_schema="keyword"
        )
        
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="features",
            field_schema="keyword"
        )
        
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="tourism_related",
            field_schema="bool"
        )
        
        print(f"Created new collection: {COLLECTION_NAME} with payload indexes")

def get_wikipedia_url(title: str) -> str:
    """Convert title to Wikipedia URL"""
    return f"{BASE_WIKI_URL}/wiki/{title.replace(' ', '_')}"

def generate_point_id(url: str) -> int:
    """Generate a consistent hash ID for a URL"""
    return int(hashlib.sha256(url.encode()).hexdigest()[:16], 16)

def determine_location_type(title: str, content: str) -> LocationType:
    """Determine the type of location based on title and content"""
    title_lower = title.lower()
    if "county" in title_lower:
        return LocationType.COUNTY
    elif "city" in title_lower or any(city.lower() in title_lower for city in ["Dublin", "Cork", "Galway", "Limerick", "Waterford"]):
        return LocationType.CITY
    elif "town" in title_lower or any(keyword in content.lower() for keyword in ["market town", "town centre", "town hall"]):
        return LocationType.TOWN
    elif "village" in title_lower:
        return LocationType.VILLAGE
    elif any(keyword in title_lower for keyword in ["park", "mountain", "beach", "lake", "river", "forest", "island"]):
        return LocationType.NATURAL
    elif any(keyword in title_lower for keyword in ["castle", "fort", "abbey", "monument", "ruins"]):
        return LocationType.HISTORICAL
    elif any(keyword in title_lower for keyword in ["museum", "theatre", "gallery", "cultural"]):
        return LocationType.CULTURAL
    elif any(keyword in title_lower for keyword in ["pub", "restaurant", "shopping", "entertainment"]):
        return LocationType.ENTERTAINMENT
    elif any(keyword in title_lower for keyword in ["hotel", "hostel", "accommodation", "resort"]):
        return LocationType.ACCOMMODATION
    return LocationType.UNKNOWN

def determine_attraction_category(title: str, content: str) -> AttractionCategory:
    """Determine the category of attraction based on title and content"""
    title_lower = title.lower()
    content_lower = content.lower()
    
    if any(keyword in title_lower or keyword in content_lower for keyword in ["heritage", "historic", "castle", "monument"]):
        return AttractionCategory.HERITAGE
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["park", "garden", "beach", "mountain", "nature"]):
        return AttractionCategory.NATURE
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["museum", "gallery", "theatre", "cultural"]):
        return AttractionCategory.CULTURE
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["pub", "nightclub", "cinema", "entertainment"]):
        return AttractionCategory.ENTERTAINMENT
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["sport", "golf", "swimming", "fitness"]):
        return AttractionCategory.SPORTS
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["restaurant", "café", "pub", "brewery"]):
        return AttractionCategory.FOOD_DRINK
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["shop", "shopping", "market", "store"]):
        return AttractionCategory.SHOPPING
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["hotel", "hostel", "accommodation"]):
        return AttractionCategory.ACCOMMODATION
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["station", "airport", "port", "transport"]):
        return AttractionCategory.TRANSPORT
    return AttractionCategory.UNKNOWN

def extract_features(content: str) -> List[str]:
    """Extract relevant features from content"""
    features = []
    feature_patterns = {
        "wheelchair_accessible": r"wheelchair|accessible",
        "family_friendly": r"family|children|kids",
        "guided_tours": r"guided tour|guide|tour",
        "parking_available": r"parking|car park",
        "food_available": r"restaurant|café|food|dining",
        "gift_shop": r"shop|souvenir|gift",
        "scenic_views": r"scenic|view|panoramic",
        "historical": r"historic|ancient|heritage",
        "outdoor_activities": r"outdoor|hiking|walking|cycling",
        "indoor_activities": r"indoor|museum|gallery",
        "free_entry": r"free entry|free admission",
        "paid_entry": r"ticket|admission|fee",
    }
    
    for feature, pattern in feature_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            features.append(feature)
    
    return features

def extract_price_range(content: str) -> Optional[str]:
    """Extract price range information from content"""
    if re.search(r"free entry|free admission", content, re.IGNORECASE):
        return "free"
    elif re.search(r"€\d+", content):
        prices = re.findall(r'€(\d+)', content)
        if prices:
            min_price = min(map(int, prices))
            max_price = max(map(int, prices))
            if min_price == max_price:
                return f"€{min_price}"
            return f"€{min_price}-€{max_price}"
    return None

def extract_opening_hours(content: str) -> Optional[str]:
    """Extract opening hours information from content"""
    hours_pattern = r"(?:open|hours|opening times?):?\s*([^.]*)"
    match = re.search(hours_pattern, content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_links(wiki_url: str) -> Set[Tuple[str, str, str, str]]:
    """Extract relevant links from Wikipedia page with enhanced metadata"""
    try:
        response = requests.get(wiki_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract page content
        content_div = soup.select_one("#mw-content-text")
        content = content_div.get_text()[:2000] if content_div else ""  # Increased to 2000 chars
        
        # Create embedding for the content
        embedding = model.encode(content).tolist()
        
        # Determine location type and other metadata
        title = wiki_url.split("/")[-1].replace("_", " ")
        location_type = determine_location_type(title, content)
        
        # Extract county and region information
        county_match = re.search(r"County\s+([A-Za-z\s]+)", content)
        county = county_match.group(1) if county_match else None
        
        # Determine region (rough geographical location)
        regions = {
            "West": ["Galway", "Mayo", "Roscommon"],
            "Northwest": ["Sligo", "Leitrim", "Donegal"],
            "Southwest": ["Kerry", "Cork", "Clare"],
            "Southeast": ["Waterford", "Wexford", "Kilkenny"],
            "East": ["Dublin", "Wicklow", "Meath"],
            "Midlands": ["Laois", "Offaly", "Westmeath", "Longford"],
            "Border": ["Cavan", "Monaghan", "Louth"]
        }
        region = next((reg for reg, counties in regions.items() 
                      if county and any(c in county for c in counties)), None)
        
        # Store the page in Qdrant with enhanced metadata
        point_id = generate_point_id(wiki_url)
        
        # Extract additional metadata
        features = extract_features(content)
        price_range = extract_price_range(content)
        opening_hours = extract_opening_hours(content)
        
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "url": wiki_url,
                    "title": title,
                    "content": content,
                    "type": "origin",
                    "location_type": location_type.value,
                    "county": county,
                    "region": region,
                    "features": features,
                    "price_range": price_range,
                    "opening_hours": opening_hours,
                    "tourism_related": bool(TOURISM_REGEX.search(content)),
                    "last_updated": datetime.now().isoformat(),
                }
            )]
        )
        
        # Extract links with enhanced metadata
        links = soup.select("a[href^='/wiki/']")
        results = set()

        for link in links:
            href = link.get("href")
            if not href or ':' in href or href.startswith('/wiki/Main_Page'):
                continue

            link_title = href.split("/wiki/")[-1].replace("_", " ")
            full_url = BASE_WIKI_URL + href
            
            # Get the link's context
            parent_p = link.find_parent('p')
            context = parent_p.get_text()[:200] if parent_p else link.get_text()
            
            # Determine link type and category
            link_type = None
            if PLACE_REGEX.search(link_title):
                link_type = "place"
            elif ATTRACTION_REGEX.search(link_title):
                link_type = "attraction"
            
            if link_type:
                results.add((link_title, full_url, link_type, context))

        return results
    except Exception as e:
        print(f"Error fetching {wiki_url}: {e}")
        return set()

def is_url_visited(url: str) -> bool:
    """Check if URL has been processed by looking it up in Qdrant"""
    point_id = generate_point_id(url)
    try:
        result = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[point_id]
        )
        return len(result) > 0
    except Exception:
        return False

def crawl_wikipedia(start_titles: List[str], max_depth: int):
    """Crawl Wikipedia pages and store in Qdrant"""
    setup_qdrant()
    queue = [(title, 1) for title in start_titles]

    while queue:
        current_title, depth = queue.pop(0)
        url = get_wikipedia_url(current_title)

        if is_url_visited(url) or depth > max_depth:
            continue

        print(f"\n🔍 Depth {depth}: {current_title} => {url}")

        if depth < max_depth:
            links = extract_links(url)
            for title, link_url, link_type, context in links:
                if not is_url_visited(link_url):
                    # Create embedding for the title
                    embedding = model.encode(title).tolist()
                    
                    # Store in Qdrant
                    point_id = generate_point_id(link_url)
                    client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=[models.PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload={
                                "url": link_url,
                                "title": title,
                                "type": link_type,
                                "context": context
                            }
                        )]
                    )
                    queue.append((title, depth + 1))

        time.sleep(2)  # Reduced sleep time since we're doing more processing

def search_similar_places(
    query: str,
    limit: int = 5,
    filter_type: Optional[str] = None,
    location_type: Optional[LocationType] = None,
    attraction_category: Optional[AttractionCategory] = None,
    region: Optional[str] = None,
    county: Optional[str] = None,
    features: Optional[List[str]] = None,
    price_range: Optional[str] = None,
    must_have_hours: bool = False
) -> List[Dict[str, Any]]:
    """
    Enhanced search for places with multiple filtering options
    """
    query_vector = model.encode(query).tolist()
    
    # Build filter conditions
    must_conditions = []
    
    if filter_type:
        must_conditions.append(
            models.FieldCondition(key="type", match=models.MatchValue(value=filter_type))
        )
    
    if location_type:
        must_conditions.append(
            models.FieldCondition(key="location_type", match=models.MatchValue(value=location_type.value))
        )
    
    if attraction_category:
        must_conditions.append(
            models.FieldCondition(key="attraction_category", match=models.MatchValue(value=attraction_category.value))
        )
    
    if region:
        must_conditions.append(
            models.FieldCondition(key="region", match=models.MatchValue(value=region))
        )
    
    if county:
        must_conditions.append(
            models.FieldCondition(key="county", match=models.MatchValue(value=county))
        )
    
    if features:
        for feature in features:
            must_conditions.append(
                models.FieldCondition(
                    key="features",
                    match=models.MatchValue(value=feature)
                )
            )
    
    if price_range:
        must_conditions.append(
            models.FieldCondition(key="price_range", match=models.MatchValue(value=price_range))
        )
    
    if must_have_hours:
        must_conditions.append(
            models.FieldCondition(
                key="opening_hours",
                match=models.MatchAny(any=[models.MatchValue(value=x) for x in ["*"]])  # Match any non-null value
            )
        )
    
    search_params = {
        "collection_name": COLLECTION_NAME,
        "query_vector": query_vector,
        "limit": limit
    }
    
    if must_conditions:
        search_params["query_filter"] = models.Filter(
            must=must_conditions
        )
    
    results = client.search(**search_params)
    
    return [
        {
            "title": hit.payload.get("title", ""),
            "url": hit.payload["url"],
            "type": hit.payload["type"],
            "location_type": hit.payload.get("location_type"),
            "county": hit.payload.get("county"),
            "region": hit.payload.get("region"),
            "features": hit.payload.get("features", []),
            "price_range": hit.payload.get("price_range"),
            "opening_hours": hit.payload.get("opening_hours"),
            "score": hit.score,
            "tourism_related": hit.payload.get("tourism_related", False),
            "context": hit.payload.get("context", ""),
            "last_updated": hit.payload.get("last_updated")
        }
        for hit in results
    ]

if __name__ == "__main__":
    # First crawl the data
    print("Starting crawler with depth 2...")
    MAX_DEPTH = 2  # Ensure depth is set to 2
    crawl_wikipedia(START_TITLES, MAX_DEPTH)
    print("\n✅ Crawling complete. Data stored in Qdrant.")
    
    # Example searches demonstrating different filtering options
    print("\nTesting search functionality...")
    
    try:
        # Example 1: Basic search for castles
        print("\nSearching for castles in Ireland:")
        results = search_similar_places(
            "castles",
            limit=5,
            features=["historical"]
        )
        for result in results:
            print(f"- {result['title']}")
            if result.get('county'):
                print(f"  County: {result['county']}")
            print(f"  URL: {result['url']}")
        
        # Example 2: Search for attractions in Dublin
        print("\nSearching for attractions in Dublin:")
        results = search_similar_places(
            "tourist attractions",
            county="Dublin",
            limit=5
        )
        for result in results:
            print(f"- {result['title']}")
            if result.get('features'):
                print(f"  Features: {', '.join(result['features'])}")
            print(f"  URL: {result['url']}")
        
        # Example 3: Search for natural attractions
        print("\nSearching for natural attractions:")
        results = search_similar_places(
            "scenic natural attractions",
            location_type=LocationType.NATURAL,
            limit=5
        )
        for result in results:
            print(f"- {result['title']}")
            if result.get('region'):
                print(f"  Region: {result['region']}")
            print(f"  URL: {result['url']}")
            
    except Exception as e:
        print(f"Error during search: {str(e)}")
        print("Please ensure the Qdrant service is running and the collection has been properly initialized.") 