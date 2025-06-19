# Travel RAG: Ireland Travel Planner

A full-stack AI-powered travel planning application for Ireland, featuring:
- **FastAPI backend** with LLM (Ollama/Mistral) for itinerary generation
- **Booking.com RapidAPI** integration for real-time hotel and flight search
- **React frontend** for interactive trip planning and chat
- **Qdrant vector database** for semantic search and RAG

---

## Features
- Generate detailed, day-by-day Ireland itineraries using LLMs
- Synchronous and background hotel/flight search (Booking.com RapidAPI)
- Chat interface for follow-up questions about your trip
- State persistence (localStorage) for itinerary, flights, and hotels
- Modern, responsive React UI

---

## Architecture
```
[React Frontend]  <---->  [FastAPI Backend]  <---->  [Ollama LLM | Booking.com API | Qdrant]
```
- **Frontend:** `client/` (React, TypeScript, MUI)
- **Backend:** `api/app/` (FastAPI, Python)
- **Crawler:** `crawler/` (Wikipedia → Qdrant)
- **Vector DB:** Qdrant (local or cloud)

---

## Quick Start (Local)

### 1. Backend (FastAPI)
```bash
cd api/app
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r ../requirements.txt
uvicorn main:app --reload
```

### 2. Frontend (React)
```bash
cd client
npm install
npm start
```

### 3. Crawler (Optional, for Qdrant data)
```bash
cd crawler
pip install -r requirements.txt
python wiki_crawler.py
```

---

## Environment Variables
- **Backend:**
  - `RAPIDAPI_KEY` (Booking.com API key)
  - `RAPIDAPI_HOST` (Booking.com API host, e.g. `booking-com15.p.rapidapi.com`)
  - `QDRANT_HOST` (default: `localhost` or Docker service name)
  - `QDRANT_PORT` (default: `6333`)
- **Frontend:**
  - Set API base URL if deploying separately (see `.env` or config)

---

## Free Deployment Tips
- **Frontend:**
  - [Vercel](https://vercel.com/) or [Netlify](https://netlify.com/) (connect your GitHub repo, set build dir to `client`)
- **Backend:**
  - [Render](https://render.com/) (free FastAPI hosting)
  - [Railway](https://railway.app/) or [Fly.io](https://fly.io/) (free/cheap Python hosting)
- **Qdrant:**
  - [Qdrant Cloud Free Tier](https://cloud.qdrant.io/)
- **LLM:**
  - Ollama is not free-hostable; use [OpenRouter](https://openrouter.ai/) or mock for demo

---

## API Endpoints (Backend)
- `POST /api/travel/generate-itinerary` — Generate itinerary, return flights/hotels
- `POST /api/chat` — Chat about your trip

---

## Project Structure
```
Travel_RAG_Final/
  api/app/         # FastAPI backend
  client/          # React frontend
  crawler/         # Wikipedia crawler for Qdrant
  qdrant_data/     # Local Qdrant storage (if used)
  ollama_data/     # Ollama model data (if used)
  docker-compose.yml
  README.md
```

---

## Contributing
Pull requests and issues are welcome! Please open an issue for bugs or feature requests.

---

## Contact & Support
- **Author:** [Your Name or GitHub]
- **Email:** [your@email.com]
- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)

---

## License
[MIT](LICENSE) 