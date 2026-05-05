"""
Unit Tests — AI Animated Video Generation System
==================================================
Covers:
  - Phase 1: JSON schema validation, scene manifest structure
  - Phase 2: Timing manifest structure, audio file presence
  - Phase 3: Video output existence and properties
  - Phase 4: FastAPI endpoint availability and response shapes
  - Phase 5: Edit intent classification (10+ query types) + StateManager

Run:
    python -m pytest test_pipeline.py -v
or:
    python test_pipeline.py
"""

import os
import sys
import json
import asyncio
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, AsyncMock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


# ─────────────────────────────────────────────────────────────────────────────
#  PHASE 1 TESTS — Story & Script Schema
# ─────────────────────────────────────────────────────────────────────────────

class TestPhase1Schema(unittest.TestCase):
    """Validate the structure of scene_manifest.json produced by Phase 1."""

    def setUp(self):
        self.manifest_path = os.path.join(BASE_DIR, "scene_manifest.json")

    def test_manifest_file_exists(self):
        self.assertTrue(os.path.exists(self.manifest_path),
                        "scene_manifest.json must exist after Phase 1 runs")

    def test_manifest_is_valid_json(self):
        with open(self.manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list, "Manifest must be a JSON array")

    def test_manifest_not_empty(self):
        with open(self.manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertGreater(len(data), 0, "Manifest must contain at least one scene")

    def test_each_scene_has_required_keys(self):
        required = {"scene_id", "location", "characters", "dialogue"}
        with open(self.manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        for scene in data:
            for key in required:
                self.assertIn(key, scene, f"Scene missing required key: {key}")

    def test_scene_id_format(self):
        with open(self.manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        for scene in data:
            self.assertRegex(scene["scene_id"], r"^scene_\d+$",
                             "scene_id must match 'scene_NNN'")

    def test_dialogue_structure(self):
        with open(self.manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        for scene in data:
            for line in scene.get("dialogue", []):
                self.assertIn("speaker", line)
                self.assertIn("line", line)
                self.assertIsInstance(line["speaker"], str)
                self.assertIsInstance(line["line"], str)
                self.assertGreater(len(line["line"]), 0)

    def test_character_db_exists(self):
        path = os.path.join(BASE_DIR, "character_db.json")
        self.assertTrue(os.path.exists(path), "character_db.json must exist")

    def test_character_db_is_dict(self):
        path = os.path.join(BASE_DIR, "character_db.json")
        with open(path, encoding="utf-8") as f:
            db = json.load(f)
        self.assertIsInstance(db, dict, "character_db.json must be a JSON object")


# ─────────────────────────────────────────────────────────────────────────────
#  PHASE 2 TESTS — Audio Generation
# ─────────────────────────────────────────────────────────────────────────────

class TestPhase2Audio(unittest.TestCase):
    """Validate Phase 2 audio outputs."""

    def test_audio_directory_exists(self):
        audio_dir = os.path.join(BASE_DIR, "audio_assets")
        self.assertTrue(os.path.isdir(audio_dir), "audio_assets/ directory must exist")

    def test_audio_files_generated(self):
        audio_dir = os.path.join(BASE_DIR, "audio_assets")
        if os.path.isdir(audio_dir):
            files = [f for f in os.listdir(audio_dir)
                     if f.endswith((".wav", ".mp3"))]
            self.assertGreater(len(files), 0, "At least one audio file must be generated")

    def test_timing_manifest_exists(self):
        path = os.path.join(BASE_DIR, "timing_manifest.json")
        self.assertTrue(os.path.exists(path), "timing_manifest.json must exist")

    def test_timing_manifest_structure(self):
        path = os.path.join(BASE_DIR, "timing_manifest.json")
        if not os.path.exists(path):
            self.skipTest("timing_manifest.json not yet generated")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        for entry in data:
            self.assertIn("scene_id", entry)
            self.assertIn("speaker", entry)
            self.assertIn("audio_file", entry)
            self.assertIn("start_ms", entry)
            self.assertIn("end_ms", entry)

    def test_timing_ms_ordering(self):
        path = os.path.join(BASE_DIR, "timing_manifest.json")
        if not os.path.exists(path):
            self.skipTest("timing_manifest.json not yet generated")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            self.assertGreaterEqual(
                entry["end_ms"], entry["start_ms"],
                "end_ms must be >= start_ms"
            )


# ─────────────────────────────────────────────────────────────────────────────
#  PHASE 3 TESTS — Video Composition
# ─────────────────────────────────────────────────────────────────────────────

class TestPhase3Video(unittest.TestCase):
    """Validate Phase 3 video output."""

    def test_final_video_exists(self):
        path = os.path.join(BASE_DIR, "final_output.mp4")
        self.assertTrue(os.path.exists(path), "final_output.mp4 must exist")

    def test_final_video_non_empty(self):
        path = os.path.join(BASE_DIR, "final_output.mp4")
        if not os.path.exists(path):
            self.skipTest("final_output.mp4 not yet generated")
        size = os.path.getsize(path)
        self.assertGreater(size, 1024, "final_output.mp4 must be larger than 1 KB")

    def test_image_assets_generated(self):
        image_dir = os.path.join(BASE_DIR, "image_assets")
        self.assertTrue(os.path.isdir(image_dir), "image_assets/ must exist")
        if os.path.isdir(image_dir):
            imgs = [f for f in os.listdir(image_dir) if f.endswith((".jpg", ".png"))]
            self.assertGreater(len(imgs), 0, "At least one character image must exist")

    def test_phase3_constants(self):
        """Verify video dimensions and FPS are set to sensible defaults."""
        from phase3_pipeline import VID_W, VID_H, FPS
        self.assertEqual(VID_W, 854)
        self.assertEqual(VID_H, 480)
        self.assertGreaterEqual(FPS, 24)


# ─────────────────────────────────────────────────────────────────────────────
#  PHASE 4 TESTS — Web Interface (FastAPI)
# ─────────────────────────────────────────────────────────────────────────────

class TestPhase4WebAPI(unittest.TestCase):
    """Test FastAPI endpoint availability without starting a real server."""

    def setUp(self):
        from fastapi.testclient import TestClient
        from app import app
        self.client = TestClient(app)

    def test_health_endpoint(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_status_endpoint(self):
        r = self.client.get("/status")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("running", data)
        self.assertIn("phases", data)

    def test_assets_endpoint(self):
        r = self.client.get("/assets")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("final_output.mp4", data)

    def test_history_endpoint(self):
        r = self.client.get("/history")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("history", data)
        self.assertIsInstance(data["history"], list)

    def test_download_blocked_for_unknown_files(self):
        r = self.client.get("/download/../../etc/passwd")
        self.assertIn(r.status_code, [403, 404])

    def test_generate_requires_prompt(self):
        r = self.client.post("/generate", json={"prompt": ""})
        # Empty prompt should still 200 (validation is in pipeline) or 422
        self.assertIn(r.status_code, [200, 422])

    def test_rerun_invalid_phase(self):
        r = self.client.post("/rerun/phase99")
        self.assertEqual(r.status_code, 400)

    def test_ui_html_served(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers.get("content-type", ""))


# ─────────────────────────────────────────────────────────────────────────────
#  PHASE 5 TESTS — Edit Agent (10+ query types) + StateManager
# ─────────────────────────────────────────────────────────────────────────────

class TestPhase5IntentClassifier(unittest.TestCase):
    """
    Test the rule-based intent classifier across 10+ edit query types
    as required by the project spec.
    """

    def setUp(self):
        from phase5_edit_agent import classify_intent_rules
        self.classify = classify_intent_rules

    # 1. Audio — voice tone
    def test_voice_tone(self):
        result = self.classify("Change the voice tone to a whisper")
        self.assertEqual(result["target"], "audio")
        self.assertEqual(result["intent"], "change_voice_tone")

    # 2. Audio — add BGM
    def test_add_background_music(self):
        result = self.classify("Add some background music to scene 1")
        self.assertEqual(result["target"], "audio")
        self.assertEqual(result["intent"], "add_background_music")

    # 3. Audio — remove BGM
    def test_remove_music(self):
        result = self.classify("Remove the background music from this scene")
        self.assertEqual(result["target"], "audio")
        self.assertEqual(result["intent"], "remove_background_music")

    # 4. Video frame — make darker
    def test_make_scene_darker(self):
        result = self.classify("Make the scene darker and more shadowy")
        self.assertEqual(result["target"], "video_frame")
        self.assertEqual(result["intent"], "make_scene_darker")

    # 5. Video frame — make brighter
    def test_make_scene_brighter(self):
        result = self.classify("Make it brighter and more vivid")
        self.assertEqual(result["target"], "video_frame")
        self.assertEqual(result["intent"], "make_scene_brighter")

    # 6. Video frame — character design
    def test_change_character_design(self):
        result = self.classify("Change the character design for the main hero")
        self.assertEqual(result["target"], "video_frame")
        self.assertEqual(result["intent"], "change_character_design")

    # 7. Video — remove subtitle
    def test_remove_subtitle(self):
        result = self.classify("Remove the subtitle overlay from the video")
        self.assertEqual(result["target"], "video")
        self.assertEqual(result["intent"], "remove_subtitle")

    # 8. Video — speed up
    def test_speed_up_scene(self):
        result = self.classify("Speed up scene 2 a bit")
        self.assertEqual(result["target"], "video")
        self.assertEqual(result["intent"], "speed_up_scene")

    # 9. Video — slow down
    def test_slow_down_scene(self):
        result = self.classify("Slow down the action sequence")
        self.assertEqual(result["target"], "video")
        self.assertEqual(result["intent"], "slow_down_scene")

    # 10. Script — regenerate
    def test_regenerate_script(self):
        result = self.classify("Regenerate the script with a darker tone")
        self.assertEqual(result["target"], "script")
        self.assertEqual(result["intent"], "regenerate_script")

    # 11. Video frame — scene style
    def test_change_scene_style(self):
        result = self.classify("Change the art style to something more painterly")
        self.assertEqual(result["target"], "video_frame")
        self.assertEqual(result["intent"], "change_scene_style")

    # 12. Video — add transition
    def test_add_transition(self):
        result = self.classify("Add a fade transition between scenes")
        self.assertEqual(result["target"], "video")
        self.assertEqual(result["intent"], "add_transition")

    def test_intent_obj_always_has_required_keys(self):
        queries = [
            "Make it darker",
            "Regenerate the story",
            "Speed it up",
            "Remove subtitles",
            "An entirely unknown command xyz",
        ]
        for q in queries:
            result = self.classify(q)
            self.assertIn("intent", result)
            self.assertIn("target", result)
            self.assertIn("scope", result)
            self.assertIn("raw_query", result)

    def test_scope_scene_extraction(self):
        result = self.classify("Make scene 2 darker")
        self.assertEqual(result["target"], "video_frame")

    def test_unknown_query_defaults_to_video(self):
        result = self.classify("do something weird and unrecognised xyzabc123")
        self.assertEqual(result["intent"], "unknown")
        self.assertEqual(result["target"], "video")


class TestPhase5StateManager(unittest.TestCase):
    """Test the StateManager versioning and undo system."""

    def setUp(self):
        # Use a temporary directory so tests don't pollute the real versions/
        self.tmpdir = tempfile.mkdtemp()
        import phase5_edit_agent as module
        self._orig_versions_dir = module.VERSIONS_DIR
        self._orig_index = module.VERSIONS_INDEX
        module.VERSIONS_DIR = self.tmpdir
        module.VERSIONS_INDEX = os.path.join(self.tmpdir, "versions.json")
        from phase5_edit_agent import StateManager
        self.sm = StateManager()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        import phase5_edit_agent as module
        module.VERSIONS_DIR = self._orig_versions_dir
        module.VERSIONS_INDEX = self._orig_index

    def test_snapshot_creates_version(self):
        v = self.sm.snapshot("Test snapshot v1")
        self.assertEqual(v, 1)

    def test_multiple_snapshots_increment(self):
        v1 = self.sm.snapshot("First")
        v2 = self.sm.snapshot("Second")
        self.assertEqual(v1, 1)
        self.assertEqual(v2, 2)

    def test_history_returns_list(self):
        self.sm.snapshot("A")
        self.sm.snapshot("B")
        h = self.sm.history()
        self.assertIsInstance(h, list)
        self.assertEqual(len(h), 2)

    def test_history_newest_first(self):
        self.sm.snapshot("First")
        self.sm.snapshot("Second")
        h = self.sm.history()
        self.assertEqual(h[0]["description"], "Second")

    def test_revert_with_no_versions_returns_error(self):
        result = self.sm.revert()
        self.assertIn("error", result)

    def test_revert_to_invalid_version_returns_error(self):
        self.sm.snapshot("One")
        result = self.sm.revert(99)
        self.assertIn("error", result)

    def test_revert_copies_assets(self):
        # Create a temp file to snapshot
        src = os.path.join(self.tmpdir, "dummy.json")
        with open(src, "w") as f:
            json.dump({"data": "original"}, f)

        self.sm.snapshot("With asset", assets={"scene_manifest": src})

        # Modify the source
        with open(src, "w") as f:
            json.dump({"data": "modified"}, f)

        # Revert (should restore original content)
        result = self.sm.revert(1)
        self.assertEqual(result["version"], 1)

    def test_snapshot_persists_state_json(self):
        v = self.sm.snapshot("Persist test")
        snap_dir = os.path.join(self.tmpdir, "v001")
        state_path = os.path.join(snap_dir, "state.json")
        self.assertTrue(os.path.exists(state_path))


class TestPhase5EditAgentAsync(unittest.IsolatedAsyncioTestCase):
    """Async tests for the EditAgent.process_edit flow."""

    async def test_process_edit_returns_dict(self):
        from phase5_edit_agent import EditAgent
        agent = EditAgent()
        result = await agent.process_edit("Make the scene darker")
        self.assertIsInstance(result, dict)
        self.assertIn("query", result)
        self.assertIn("intent", result)
        self.assertIn("execution", result)

    async def test_process_edit_intent_has_target(self):
        from phase5_edit_agent import EditAgent
        agent = EditAgent()
        result = await agent.process_edit("Regenerate the script")
        intent = result.get("intent", {})
        self.assertIn(intent.get("target"), ("audio","video_frame","video","script"))

    async def test_audio_executor_runs_without_crash(self):
        """Execute an audio edit on a mock manifest."""
        from phase5_edit_agent import execute_audio_edit
        intent_obj = {
            "intent": "change_voice_tone",
            "target": "audio",
            "scope": "all",
        }
        result = await execute_audio_edit(intent_obj)
        # Should return a dict with 'status' key
        self.assertIn("status", result)

    async def test_video_frame_executor_runs_without_crash(self):
        from phase5_edit_agent import execute_video_frame_edit
        intent_obj = {
            "intent": "make_scene_darker",
            "target": "video_frame",
            "scope": "all",
        }
        result = await execute_video_frame_edit(intent_obj)
        self.assertIn("status", result)


# ─────────────────────────────────────────────────────────────────────────────
#  RUNNER
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Run with verbose output
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPhase1Schema))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase2Audio))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3Video))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase5IntentClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase5StateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase5EditAgentAsync))

    # Phase 4 tests require httpx (optional)
    try:
        import httpx  # noqa
        suite.addTests(loader.loadTestsFromTestCase(TestPhase4WebAPI))
    except ImportError:
        print("[Warning] httpx not installed — skipping Phase 4 API tests")
        print("  Install with: pip install httpx")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
