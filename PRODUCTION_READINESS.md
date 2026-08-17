# Production readiness

Verified locally on Python 3.12.3 and FFmpeg/ffprobe 6.1.1.

- READY — topic queue, atomic JSON state, permanent IDs/UUIDs, state transitions, resume/idempotent completed stages, process locks, bounded stage retry guard, CLI, configuration validation, local storage, SRT generation, FFmpeg render, deterministic technical QC, checksums, archive, cleanup dry-run/safety, upload queue, dual Final Checker gate, dry-run publishing, doctor, scripts, tests.
- MOCK ONLY — research, script generation, scene planning, voice (synthetic tone), visuals (synthetic solid frames), thumbnail (synthetic image), AI final-check reasoning. Deterministic schemas/gates around these are real.
- PARTIAL — scheduler templates (safe audit behavior; not installed/enabled), structured logging (available but not wired to every stage), cloud storage interface, regeneration routing (affected stages are reported; explicit force rerun is supported), background music/transitions, analytics persistence.
- CREDENTIALS REQUIRED — YouTube Data API OAuth client and token; YouTube Analytics OAuth; any paid AI/TTS/image provider.
- EXTERNAL SERVICE REQUIRED — factual web/source retrieval; production LLM/TTS/image/video generation; YouTube upload/analytics; cloud media storage.
- NOT IMPLEMENTED — authenticated Google API transport callback, vendor cloud adapters, real analytics retrieval, licensed stock search, daemon upload retries/rate-limit adapter. Production publisher deliberately refuses to call anything without a valid PASS and credentials.

The system is not claimed fully production-ready. The local mock pipeline and safety gates are verified; external integrations remain unverified and unauthenticated.

