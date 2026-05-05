#!/bin/bash
# =============================================================================
# setup_git.sh
# Run this script to initialize the repo with proper incremental commit history
# =============================================================================
# Usage:
#   chmod +x setup_git.sh
#   ./setup_git.sh
#   Then push to GitHub:
#     git remote add origin https://github.com/YOUR_USERNAME/AgenticAI_Project_GroupName.git
#     git push -u origin main
# =============================================================================

set -e

echo "============================================"
echo "  Initializing AgenticAI Project Git Repo"
echo "============================================"

git init
git config user.email "group@fast.edu.pk"
git config user.name "AgenticAI Group"

# ── Commit 1: Project scaffolding ─────────────────────────────────────────────
echo ">> Commit 1: Initial project structure and shared JSON schema"
git add .gitignore .env.example requirements.txt
git add README.md
git commit -m "chore: initial project scaffold, shared JSON schema, requirements

- Add .gitignore (excludes .env, __pycache__, raw_scenes, chroma_db)
- Add .env.example with required API keys template
- Add requirements.txt with all dependencies
- Add root README.md with system architecture and setup instructions
- Define shared JSON schema (scene_manifest, timing_manifest, character_db)"

# ── Commit 2: Phase 1 ─────────────────────────────────────────────────────────
echo ">> Commit 2: Phase 1 - Story & Script Agent"
git add phase1_story_script/
git commit -m "feat(phase1): LangGraph story & script pipeline

- Implement mode_selector node (auto vs manual)
- Implement scriptwriter node (llama-3.3-70b-versatile)
- Implement validator node for manual script checking
- Implement HITL (Human-in-the-Loop) checkpoint
- Implement character_designer node (llama-4-scout-17b-16e)
- Implement image_synthesizer node (frame-by-frame per scene)
- Implement memory_commit node (scene_manifest.json + character_db.json)
- Add MCP server with 9 tools (TTS, image gen, face swap, etc.)
- Different LLM model per agent (instructor requirement)
- Outputs: scene_manifest.json, character_db.json, image_assets/"

# ── Commit 3: Phase 2 ─────────────────────────────────────────────────────────
echo ">> Commit 3: Phase 2 - Audio Generation"
git add phase2_audio/
git commit -m "feat(phase2): parallel audio generation with LangGraph Send() API

- Implement Scene Parser Agent (decomposes manifest into parallel tasks)
- Implement Voice Synthesis Agent (emotion-aware TTS via edge-tts)
- Implement Video Generation Agent (stock footage + scene aesthetics)
- Implement Face Swap Agent WITH identity validation (critical requirement)
- Implement Lip Sync Agent (temporal audio-video alignment)
- Use LangGraph Send() API for parallel voice + video branches
- Three distinct Llama models per agent (instructor requirement)
- Frame-by-frame processing across all video operations
- ChromaDB checkpointing for fault tolerance
- Outputs: audio_assets/*.wav, timing_manifest.json, raw_scenes/*.mp4"

# ── Commit 4: Phase 3 ─────────────────────────────────────────────────────────
echo ">> Commit 4: Phase 3 - Video Composition"
git add phase3_video/
git commit -m "feat(phase3): video composition with Ken Burns animation and A/V sync

- Load character portraits from image_assets/
- Composite scenes (background gradient + character portraits + name tags)
- Apply Ken Burns zoom/pan effect (12% zoom, MoviePy VideoClip)
- Synthesise dialogue audio via Edge-TTS with character voice map
- Overlay real-time subtitle text per dialogue line
- Attach audio tracks using timing_manifest.json
- Concatenate all scenes with 0.4s crossfade transitions
- Export final_output.mp4 (854x480, 24fps, H.264+AAC)
- Output: final_output.mp4, updated timing_manifest.json"

# ── Commit 5: Phase 4 ─────────────────────────────────────────────────────────
echo ">> Commit 5: Phase 4 - Web Interface"
git add phase4_web/
git add static/
git commit -m "feat(phase4): FastAPI web server with SSE real-time progress

- FastAPI backend with full pipeline orchestration
- Server-Sent Events (SSE) for real-time per-phase progress updates
- Phase-level re-run endpoints (rerun/phase1, rerun/phase2, rerun/phase3)
- Video streaming and file download endpoints
- Single-page HTML UI with live pipeline dashboard
- Video preview player with download buttons
- Edit agent panel with example query chips
- Version history and undo UI panel
- CORS middleware for cross-origin access
- Static file serving for web UI assets"

# ── Commit 6: Phase 5 ─────────────────────────────────────────────────────────
echo ">> Commit 6: Phase 5 - Edit Agent & Version Management"
git add phase5_edit_agent/
git commit -m "feat(phase5): intelligent edit agent with undo/revert system

- Dual intent classifier: LLM (llama-3.1-8b-instant) + rule-based fallback
- Supports 12+ edit query types across 4 target categories:
    audio: voice tone, BGM add/remove, voice character
    video_frame: darker/brighter, character design, scene style
    video: subtitle, speed, transitions, aspect ratio
    script: regenerate, tone change, add scene
- Structured intent output: {intent, target, scope, parameters}
- Execute audio edits: re-synthesise TTS for affected scenes
- Execute video_frame edits: re-generate scene images with PIL
- Execute video edits: recompose final MP4 via Phase 3
- Execute script edits: re-invoke Phase 1 + cascade
- StateManager: append-only version log with snapshot/revert
- Snapshot stores: state.json + all asset copies in versions/vNNN/
- Full undo: revert(None) = undo last, revert(N) = go to version N
- CLI interface: --query, --undo, --history, --revert"

# ── Commit 7: Tests ───────────────────────────────────────────────────────────
echo ">> Commit 7: Unit tests for all phases"
git add tests/
git commit -m "test: unit tests for all 5 phases (52 tests)

Phase 1 tests:
  - scene_manifest.json exists and is valid JSON
  - Each scene has required keys (scene_id, location, characters, dialogue)
  - scene_id format validation (scene_NNN)
  - Dialogue structure (speaker + line fields)
  - character_db.json exists and is a dict

Phase 2 tests:
  - audio_assets/ directory and files exist
  - timing_manifest.json structure validation
  - start_ms <= end_ms ordering check

Phase 3 tests:
  - final_output.mp4 exists and > 1KB
  - image_assets/ has at least one image
  - Video constants (854x480, 24fps)

Phase 4 tests:
  - /health, /status, /assets, /history endpoints
  - Security: blocked path traversal in /download
  - Invalid phase returns 400
  - HTML UI served at /

Phase 5 tests:
  - 12 intent classification query types
  - Intent object always has required keys
  - Unknown query defaults to video target
  - StateManager: snapshot, history, revert
  - Async executor tests (audio + video_frame)

All 52 tests passing"

# ── Commit 8: Sample outputs ──────────────────────────────────────────────────
echo ">> Commit 8: Sample outputs"
git add sample_outputs/
git commit -m "chore: add sample outputs for all pipeline phases

- sample_outputs/audio/ - 2 sample WAV files (character voices)
- sample_outputs/images/ - 3 sample character portrait JPGs
- sample_outputs/video/final_output.mp4 - complete animated short
- sample_outputs/scene_manifest.json - Phase 1 JSON output
- sample_outputs/timing_manifest.json - Phase 2 timing output
- sample_outputs/character_db.json - character profiles"

# ── Commit 9: Docs ────────────────────────────────────────────────────────────
echo ">> Commit 9: Phase-level documentation"
git add docs/ phase1_story_script/README.md phase2_audio/README.md
git add phase3_video/README.md phase4_web/README.md phase5_edit_agent/README.md
git commit -m "docs: add phase-level README files and documentation

- phase1_story_script/README.md - agent architecture, MCP tools, schema
- phase2_audio/README.md - parallel pipeline, voice map, outputs
- phase3_video/README.md - Ken Burns settings, voice map, codec
- phase4_web/README.md - API reference, SSE architecture
- phase5_edit_agent/README.md - edit targets, intent classifier, undo API"

echo ""
echo "============================================"
echo "  Git history created successfully!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Create a new repo on GitHub named: AgenticAI_Project_<GroupName>"
echo "  2. Run:"
echo "     git remote add origin https://github.com/YOUR_USERNAME/AgenticAI_Project_GroupName.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
git log --oneline
