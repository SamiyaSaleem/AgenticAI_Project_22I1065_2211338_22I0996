# AgenticAI_Project_22I1065_2211338_22I0996

# AgenticAI_Project — AI-Powered Animated Video Generation System

> **From Prompt to Polished Short Film — End-to-End with LLM Agents**  
> Course: Agentic AI | FAST-NUCES Islamabad | 2026

---

## Project Overview

A fully agentic, multi-phase pipeline that accepts a single natural-language prompt and autonomously produces a complete short animated video — including story, character voices, visual scenes, and a composited MP4 — with zero manual creative intervention.

```
User Prompt
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1 — Story & Script Agent (LangGraph + Groq LLM)          │
│   → scene_manifest.json  +  character_db.json                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2 — Audio Generation (Edge-TTS / ElevenLabs + MCP)       │
│   → audio_assets/*.wav   +  timing_manifest.json                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3 — Video Composition (MoviePy + FFmpeg + PIL)            │
│   → final_output.mp4                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 4 — Web Interface (FastAPI + SSE + React-style HTML UI)   │
│   Real-time progress, phase re-run, video preview + download    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 5 — Edit Agent & Version Management (LangGraph + Undo)   │
│   Free-text edits → intent classification → targeted re-run     │
│   Append-only version history with full undo/revert             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Primary | Local / Budget Alt |
|---|---|---|
| LLM / Agents | Groq API (Llama 3.3-70b, Llama 4 Scout, Llama 3.1-8b) | Ollama + LLaMA 3 |
| TTS | Edge-TTS (local, free) | ElevenLabs API |
| Image Gen | HuggingFace FLUX / SDXL | PIL placeholder |
| Video Comp. | MoviePy + FFmpeg | FFmpeg only |
| Agents | LangGraph + LangChain | — |
| MCP | FastMCP (stdio server) | — |
| Backend | FastAPI + Uvicorn | — |
| Frontend | Single-page HTML + SSE | — |
| Memory | ChromaDB (vector store) | File-based JSON |
| State Store | File-based JSON snapshots | SQLite |

---

## Project Structure

```
AgenticAI_Project/
├── main.py                  # Phase 1 — Story, Script & Character Agent
├── phase2_pipeline.py       # Phase 2 — Audio Generation (LangGraph parallel)
├── phase3_pipeline.py       # Phase 3 — Video Composition (MoviePy + FFmpeg)
├── app.py                   # Phase 4 — FastAPI Web Server + SSE Orchestration
├── phase5_edit_agent.py     # Phase 5 — Edit Agent + StateManager (Undo)
├── mcp_server.py            # MCP stdio server (9 tools: TTS, image gen, video, etc.)
├── test_pipeline.py         # Unit tests for all phases
├── requirements.txt         # Python dependencies
├── static/
│   └── index.html           # Single-page web UI
├── scene_manifest.json      # Phase 1 output: structured scenes + dialogue
├── character_db.json        # Phase 1 output: character profiles + images
├── timing_manifest.json     # Phase 2 output: audio timing per dialogue line
├── final_output.mp4         # Phase 3 output: final animated video
├── audio_assets/            # WAV/MP3 files per dialogue line
├── image_assets/            # Character portrait JPGs per scene
├── raw_scenes/              # Intermediate per-scene MP4 clips
├── versions/                # Phase 5 state snapshots (v001/, v002/, …)
└── chroma_db/               # ChromaDB persistent memory
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- FFmpeg installed and on PATH (`ffmpeg --version`)
- A `.env` file with your API keys (see below)

### 1. Clone the repository
```bash
git clone https://github.com/<your-org>/AgenticAI_Project_<GroupName>.git
cd AgenticAI_Project_<GroupName>
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
HF_API_TOKEN=your_huggingface_token_here   # optional: for real image generation
ELEVENLABS_API_KEY=your_key_here           # optional: premium TTS
```
> Without `GROQ_API_KEY`, the pipeline runs in **offline mock mode** — it still generates outputs but uses deterministic placeholder logic instead of LLM reasoning.

---

## Running the Pipeline

### Option A — Web Interface (Recommended)
```bash
# Start the FastAPI server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Open browser
open http://localhost:8000
```
The web UI allows you to:
- Enter a prompt and start the full pipeline
- Watch real-time phase-by-phase progress via SSE
- Re-run individual phases with a single click
- Preview and download the final video
- Apply free-text edits via the Edit Agent
- View version history and undo any edit

---

### Option B — CLI (Phase by Phase)

**Phase 1 — Generate story & script:**
```bash
python main.py --prompt "A young astronaut discovers a hidden ocean on Mars" --mode auto
# Outputs: scene_manifest.json, character_db.json, image_assets/
```

**Phase 2 — Generate audio:**
```bash
python phase2_pipeline.py
# Outputs: audio_assets/*.wav, timing_manifest.json
```

**Phase 3 — Compose video:**
```bash
python phase3_pipeline.py
# Outputs: final_output.mp4, timing_manifest.json (updated)
```

**Phase 5 — Apply an edit:**
```bash
python phase5_edit_agent.py --query "Make the scene darker"
python phase5_edit_agent.py --query "Change voice tone to whispered for Kai"
python phase5_edit_agent.py --undo
python phase5_edit_agent.py --history
python phase5_edit_agent.py --revert 2
```

---

## Running Tests
```bash
# Run all unit tests
python -m pytest test_pipeline.py -v

# Or directly
python test_pipeline.py
```

Test coverage:
- **Phase 1**: JSON schema validation, scene structure, character DB
- **Phase 2**: Audio file presence, timing manifest structure
- **Phase 3**: Video output existence and size, constants validation
- **Phase 4**: FastAPI endpoint responses, security checks
- **Phase 5**: 12+ intent classification query types, StateManager CRUD, async executor

---

## Phase 5 — Edit Agent

The edit agent accepts free-text commands and classifies them into one of four targets:

| Target | Example Queries | Action |
|---|---|---|
| `audio` | "Change voice tone", "Add background music" | Re-synthesises TTS / BGM |
| `video_frame` | "Make scene darker", "Change character design" | Re-generates scene images |
| `video` | "Remove subtitle", "Speed up scene 2" | Recomposes final MP4 |
| `script` | "Regenerate the script", "Change story tone" | Re-invokes Phase 1 + cascade |

### Undo System
Every edit and pipeline run creates a versioned snapshot:
```
versions/
  v001/  state.json  scene_manifest.json  final_output.mp4  …
  v002/  state.json  …
  versions.json   ← append-only index
```
- `StateManager.snapshot(description, assets)` → saves version
- `StateManager.revert(version)` → restores files + JSON state
- `StateManager.history()` → returns all versions newest-first

---

## Division of Work

| Member | Phase | Key Responsibilities |
|---|---|---|
| Member 1 | Phase 1 — Story & Script | LangGraph agent, Groq LLM integration, JSON schema, character roster |
| Member 2 | Phase 2 — Audio | Edge-TTS synthesis, emotion classification, timing manifest, parallel LangGraph |
| Member 3 | Phase 3 — Video | MoviePy Ken Burns animation, A/V sync, subtitle overlay, MP4 export |
| Member 4 | Phase 4 + 5 — Web + Edit | FastAPI backend, SSE progress, React UI, LangGraph edit agent, undo system |

All members: shared JSON schema design, integration testing, project report, presentation.

---

## API Reference (Phase 4)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `GET` | `/health` | Health check |
| `POST` | `/generate` | Start pipeline `{"prompt":"…","mode":"auto"}` |
| `GET` | `/status` | Current pipeline status |
| `GET` | `/progress` | SSE stream for real-time updates |
| `POST` | `/rerun/{phase}` | Re-run phase1/phase2/phase3 |
| `GET` | `/video/final_output.mp4` | Stream the video |
| `GET` | `/download/{filename}` | Download generated files |
| `GET` | `/assets` | List generated assets |
| `POST` | `/edit` | Apply edit `{"query":"…"}` |
| `GET` | `/history` | Version history |
| `POST` | `/undo` | Undo `{"version":null}` or `{"version":2}` |

---

## Sample Prompts

- `"A cyberpunk detective infiltrates a neon megacity to expose a rogue AI that has been rewriting human memories."`
- `"A young astronaut discovers a hidden ocean on Mars and must convince humanity it is real."`
- `"Two rival scientists race to decode an ancient AI signal from deep space before a corporation can weaponize it."`

---

## Known Limitations

- Image generation requires a HuggingFace API token for real images; without it, the system falls back to PIL-generated placeholder frames.
- ElevenLabs TTS requires an API key; without it, the free Edge-TTS engine is used (still produces good results).
- Video generation is CPU-bound and can take several minutes for longer scripts.
- The LangGraph face-swap and lip-sync agents are simulated via the MCP server (real InsightFace/Wav2Lip would require CUDA GPU).

---

*Built for the Agentic AI Course — FAST-NUCES Islamabad, 2026*
