#!/usr/bin/env python3
"""Fix imports in extracted drift modules."""
import os
import re

BASE = "/home/crexs/drift/drift"

# Mapping: old import → new import
# Order matters: more specific first
IMPORT_MAP = [
    # Core modules (in drift/core/)
    (r'\bfrom config import', 'from drift.core.config import'),
    (r'\bfrom brain import', 'from drift.core.brain import'),
    (r'\bfrom being import', 'from drift.core.being import'),
    (r'\bfrom memory import', 'from drift.core.memory import'),
    (r'\bfrom global_workspace import', 'from drift.core.global_workspace import'),
    (r'\bfrom cognitive_architecture import', 'from drift.core.cognitive_architecture import'),
    (r'\bfrom cognitive_orchestrator import', 'from drift.core.cognitive_orchestrator import'),
    (r'\bfrom cognitive_factory import', 'from drift.core.cognitive_factory import'),
    (r'\bfrom embodiment import', 'from drift.core.embodiment import'),
    (r'\bfrom iit_consciousness import', 'from drift.core.iit_consciousness import'),
    (r'\bfrom homeostasis import', 'from drift.core.homeostasis import'),
    (r'\bfrom intuition import', 'from drift.core.intuition import'),
    (r'\bfrom self_modify import', 'from drift.core.self_modify import'),
    (r'\bfrom emotional_field import', 'from drift.core.emotional_field import'),
    (r'\bfrom metacognition import', 'from drift.core.metacognition import'),
    (r'\bfrom resilience import', 'from drift.core.resilience import'),
    (r'\bfrom prompt_budget import', 'from drift.core.prompt_budget import'),
    (r'\bfrom prompt_builder import', 'from drift.core.prompt_builder import'),
    (r'\bfrom history import', 'from drift.core.history import'),
    (r'\bfrom commands import', 'from drift.core.commands import'),
    (r'\bfrom tools import', 'from drift.core.tools import'),
    (r'\bfrom guardrails import', 'from drift.core.guardrails import'),
    (r'\bfrom local_llm import', 'from drift.core.local_llm import'),
    (r'\bfrom seed_cognition import', 'from drift.core.seed_cognition import'),
    # Plugins (in drift/core/plugins/)
    (r'\bfrom temporal import', 'from drift.core.plugins.temporal import'),
    (r'\bfrom predictor import', 'from drift.core.plugins.predictor import'),
    (r'\bfrom values import', 'from drift.core.plugins.values import'),
    (r'\bfrom physics import', 'from drift.core.plugins.physics import'),
    (r'\bfrom humanity import', 'from drift.core.plugins.humanity import'),
    (r'\bfrom relationship import', 'from drift.core.plugins.relationship import'),
    (r'\bfrom growth_trajectory import', 'from drift.core.plugins.growth_trajectory import'),
    (r'\bfrom aspirations import', 'from drift.core.plugins.aspirations import'),
    (r'\bfrom inner_voice import', 'from drift.core.plugins.inner_voice import'),
    (r'\bfrom dreamer import', 'from drift.core.plugins.dreamer import'),
    (r'\bfrom explorer import', 'from drift.core.plugins.explorer import'),
    (r'\bfrom creativity import', 'from drift.core.plugins.creativity import'),
    (r'\bfrom goals import', 'from drift.core.plugins.goals import'),
    (r'\bfrom scheduler import', 'from drift.core.plugins.scheduler import'),
    (r'\bfrom preferences import', 'from drift.core.plugins.preferences import'),
    (r'\bfrom documents import', 'from drift.core.plugins.documents import'),
    (r'\bfrom growth import', 'from drift.core.plugins.growth import'),
    (r'\bfrom self_eval import', 'from drift.core.plugins.self_eval import'),
    (r'\bfrom proactive import', 'from drift.core.plugins.proactive import'),
    (r'\bfrom emotion import', 'from drift.core.plugins.emotion import'),
    (r'\bfrom computer_use import', 'from drift.core.plugins.computer_use import'),
    (r'\bfrom voice import', 'from drift.core.plugins.voice import'),
    (r'\bfrom tui import', 'from drift.core.plugins.tui import'),
]

# Files that should NOT have their imports changed (they're in the same package)
# e.g., drift/core/config.py importing from config.py doesn't need changes
# Actually, we need to handle relative imports within packages

def fix_file(path):
    with open(path, "r") as f:
        content = f.read()

    original = content
    rel = os.path.relpath(path, BASE)
    is_core = rel.startswith("core/")
    is_plugin = rel.startswith("core/plugins/")

    for pattern, replacement in IMPORT_MAP:
        content = re.sub(pattern, replacement, content)

    # Also fix bare module references in strings/comments if needed
    # But be careful not to break things

    if content != original:
        with open(path, "w") as f:
            f.write(content)
        return True
    return False


changed = 0
for root, dirs, files in os.walk(BASE):
    for fname in files:
        if not fname.endswith(".py"):
            continue
        path = os.path.join(root, fname)
        if fix_file(path):
            changed += 1

print(f"Fixed imports in {changed} files.")
