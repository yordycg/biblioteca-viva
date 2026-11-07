#!/usr/bin/env python3
"""Carga el seed ficticio. Uso: .venv/bin/python scripts/seed.py"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.core.management import call_command  # noqa: E402

call_command("seed", "--reset")
