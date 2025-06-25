# Travel RAG: Ireland Travel Planner (Dockerized)

A full-stack AI-powered travel planning application for Ireland, containerized for easy deployment with Docker and Docker Compose.

---

## Features
- Generate detailed, day-by-day Ireland itineraries using LLMs (Ollama/Mistral)
- Real-time hotel and flight search via Booking.com RapidAPI
- Chat interface for follow-up questions about your trip
- Qdrant vector database for semantic search and RAG
- Modern React frontend
- Fully containerized: run everything with Docker Compose

---

## Architecture
```
[React Frontend]  <---->  [FastAPI Backend]  <---->  [Ollama LLM | Booking.com API | Qdrant]
        |                        |                        |
     Docker                  Docker                   Docker
```
- **Frontend:** `client/` (React, TypeScript, MUI)
- **Backend:** `api/app/` (FastAPI, Python)
- **Crawler:** `crawler/` (Wikipedia → Qdrant)
- **Vector DB:** Qdrant (local or cloud)

---

## Quick Start: Docker Compose

### 1. Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

### 2. Clone the Repository
```bash
git clone https://github.com/your-repo/Travel_RAG_Final.git
cd Travel_RAG_Final
```

### 3. Set Environment Variables
Create a `.env` file in the project root (or edit `docker-compose.yml`):
```
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=booking-com15.p.rapidapi.com
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

### 4. Build and Start All Services
```bash
docker-compose up --build
```
- This will start:
  - FastAPI backend (http://localhost:8000)
  - React frontend (http://localhost:3000)
  - Qdrant vector DB (http://localhost:6333)
  - (Optional) Crawler service
  - (Optional) Ollama LLM (if configured)

### 5. Run the Crawler (Optional)
To populate Qdrant with Wikipedia data:
```bash
docker-compose run --rm crawler
```

---

## How to Use Individual Dockerfiles

### Backend (FastAPI)
```bash
cd api
# Build
docker build -t travel-backend -f Dockerfile .
# Run
# (Set env vars as needed)
docker run -p 8000:8000 --env-file ../.env travel-backend
```

### Frontend (React)
```bash
cd client
# Build
docker build -t travel-frontend -f Dockerfile .
# Run
docker run -p 3000:80 travel-frontend
```

### Crawler
```bash
cd crawler
# Build
docker build -t travel-crawler -f Dockerfile .
# Run
docker run --env-file ../.env travel-crawler
```

---

## Environment Variables (Docker)
- Set in `.env` or directly in `docker-compose.yml`:
  - `RAPIDAPI_KEY` (Booking.com API key)
  - `RAPIDAPI_HOST` (Booking.com API host)
  - `QDRANT_HOST` (should match Docker service name, e.g. `qdrant`)
  - `QDRANT_PORT` (default: `6333`)

---

## API Endpoints (Backend)
- `POST /api/travel/generate-itinerary` — Generate itinerary, return flights/hotels
- `POST /api/chat` — Chat about your trip

---

## Project Structure
```
Travel_RAG_Final/
  api/app/         # FastAPI backend (Dockerfile inside)
  client/          # React frontend (Dockerfile inside)
  crawler/         # Wikipedia crawler (Dockerfile inside)
  qdrant_data/     # Local Qdrant storage (if used)
  ollama_data/     # Ollama model data (if used)
  docker-compose.yml
  README.md
```

---

## Contact & License
- **Author:** [Madhu Vanthi Sankar Ganesh]
- **Email:** [madhuvanthi31sankarganesh@gmail.com]


---

## License
[MIT](LICENSE) 
