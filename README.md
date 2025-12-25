# Agentic Form Filler

An AI-powered application that helps users fill out movie order forms through a conversational interface. Built with SvelteKit for the frontend and Python FastAPI + Google ADK for the backend.

## Features

- **Conversational Form Filling**: Chat with an AI agent to provide order details
- **Country Validation**: Automatically validates shipping countries
- **Multiple Movies**: Add as many movies as you want to your order
- **Document Preservation**: Maintains original formatting when filling the form
- **Real-time Streaming**: See agent responses as they're generated via SSE

## Architecture

```
┌─────────────────┐     ┌─────────────────────────────────┐
│   SvelteKit     │     │      Python FastAPI             │
│   Frontend      │────▶│  ┌───────────────────────────┐  │
│                 │     │  │     Google ADK Agent      │  │
│  - File Upload  │◀────│  │  - inspect_form           │  │
│  - Chat UI      │ SSE │  │  - validate_country       │  │
│  - Download     │     │  │  - update_document        │  │
└─────────────────┘     │  └───────────────────────────┘  │
                        └─────────────────────────────────┘
```

## Prerequisites

- Node.js 18+
- Python 3.10+
- Google API Key (for Gemini)

## Setup

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. Start the server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open http://localhost:5173 in your browser

## Sample Document Template

Create a Word document (`OrderForm.docx`) with the following structure:

```
MOVIE ORDER FORM
================

Customer Information:
--------------------
Name: ________________
Street: ________________
Postal Code and City: ________________
Country: ________________

Movies Ordered:
--------------
| Title          | Language    |
|----------------|-------------|
|                |             |
```

The agent will detect these fields and the movie table automatically.

## Usage

1. Upload your `.docx` order form template
2. Chat with the agent to provide:
   - Your name
   - Street address
   - Postal code and city
   - Country (must be a valid country)
   - Movies you want to order (title and language)
3. The agent will validate your country and allow adding multiple movies
4. Once complete, download your filled form

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload a .docx file |
| POST | `/api/chat/{session_id}` | Send a message |
| GET | `/api/chat/stream/{session_id}` | SSE stream for responses |
| GET | `/api/status/{session_id}` | Get form completion status |
| GET | `/api/download/{session_id}` | Download filled document |
| GET | `/health` | Health check |

## Tech Stack

- **Frontend**: SvelteKit 2.0, TypeScript, Svelte 5
- **Backend**: Python 3.10+, FastAPI, python-docx
- **AI**: Google ADK, Gemini 2.0 Flash
- **Validation**: pycountry

## License

MIT

# word_form_orders_agent
