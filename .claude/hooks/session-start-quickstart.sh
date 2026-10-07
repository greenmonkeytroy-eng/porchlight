#!/usr/bin/env bash
cat <<'EOF'
=== Porchlight OS Quickstart ===
Repo: github.com/greenmonkeytroy-eng/porchlight (main, clean)

Engine: engine/app/{clients,metrics,services}/ + config.py + main.py
  Run locally, no Docker needed (from the engine/ directory):
    python -m app.clients.provisions
    python -m app.services.rates_allocator
    python -m app.services.ocr_parser

Docker: BLOCKED - virtualization is disabled in BIOS/UEFI firmware
  (Windows 10 Home). Fix: reboot into firmware setup, enable
  Intel VT-x / AMD-V, relaunch Docker Desktop, then retry
  docker build / docker compose up.

Full context: see MEMORY.md (auto-loaded) for details.
=================================
EOF
