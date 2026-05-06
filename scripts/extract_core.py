#!/usr/bin/env python3
"""Extract and genericize core modules from infj_bot into drift."""
import os
import shutil
import re

SRC = "/home/crexs/infj_bot"
DST = "/home/crexs/drift/drift"

CORE_FILES = [
    "config.py",
    "cognitive_architecture.py",
    "cognitive_orchestrator.py",
    "cognitive_factory.py",
    "global_workspace.py",
    "being.py",
    "embodiment.py",
    "iit_consciousness.py",
    "homeostasis.py",
    "intuition.py",
    "memory.py",
    "self_modify.py",
    "emotional_field.py",
    "metacognition.py",
    "resilience.py",
    "prompt_budget.py",
    "prompt_builder.py",
    "history.py",
    "commands.py",
    "tools.py",
    "guardrails.py",
    "brain.py",
    "local_llm.py",
    "seed_cognition.py",
]

PLUGIN_FILES = [
    "temporal.py",
    "predictor.py",
    "values.py",
    "physics.py",
    "humanity.py",
    "relationship.py",
    "growth_trajectory.py",
    "aspirations.py",
    "inner_voice.py",
    "dreamer.py",
    "explorer.py",
    "creativity.py",
    "goals.py",
    "scheduler.py",
    "preferences.py",
    "documents.py",
    "growth.py",
    "self_eval.py",
    "proactive.py",
    "emotion.py",
    "computer_use.py",
    "voice.py",
    "tui.py",
]

# Files that stay in root but get renamed
API_FILES = ["api.py", "web_app.py", "cli.py", "main.py", "mcp_server.py"]

# Test files
TEST_FILES = [
    "test_aspirations.py",
    "test_growth_trajectory.py",
    "test_metacognition.py",
    "test_predictor.py",
    "test_self_modify.py",
    "test_temporal.py",
]


def copy_and_transform(src_path, dst_path):
    with open(src_path, "r") as f:
        content = f.read()

    # Genericization replacements
    replacements = [
        (r'\bJude\b', 'user'),
        (r'\bjude\b', 'user'),
        (r'\bINFJ\b', 'DRIFT'),
        (r'\binfj_bot\b', 'drift'),
        (r'\bInfjBrain\b', 'DriftBrain'),
        (r'\bInfjMemory\b', 'DriftMemory'),
        (r'\bInfjTUI\b', 'DriftTUI'),
        (r'INFJ_PRIMARY_MODEL', 'DRIFT_PRIMARY_MODEL'),
        (r'INFJ_CRITIC_MODEL', 'DRIFT_CRITIC_MODEL'),
        (r'INFJ_LOCAL_MODEL', 'DRIFT_LOCAL_MODEL'),
        (r'INFJ_USE_LOCAL_FALLBACK', 'DRIFT_USE_LOCAL_FALLBACK'),
        (r'INFJ_AUTHORIZED_TARGETS', 'DRIFT_AUTHORIZED_TARGETS'),
        (r'"infj_bot"', '"drift"'),
        (r'"INFJ Bot"', '"DRIFT"'),
        (r'"INFJ COMPANION"', '"DRIFT"'),
        (r'\[INFJ COMPANION\]', '[DRIFT]'),
        (r'\[JUDE\]', '[USER]'),
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    # Write transformed content
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w") as f:
        f.write(content)

    print(f"  -> {dst_path}")


print("=== Extracting core modules ===")
for fname in CORE_FILES:
    src = os.path.join(SRC, fname)
    if not os.path.exists(src):
        print(f"  SKIP (not found): {src}")
        continue
    dst = os.path.join(DST, "core", fname)
    copy_and_transform(src, dst)

print("\n=== Extracting plugins ===")
for fname in PLUGIN_FILES:
    src = os.path.join(SRC, fname)
    if not os.path.exists(src):
        print(f"  SKIP (not found): {src}")
        continue
    dst = os.path.join(DST, "core", "plugins", fname)
    copy_and_transform(src, dst)

print("\n=== Extracting tests ===")
for fname in TEST_FILES:
    src = os.path.join(SRC, fname)
    if not os.path.exists(src):
        print(f"  SKIP (not found): {src}")
        continue
    dst = os.path.join("/home/crexs/drift/tests", fname)
    copy_and_transform(src, dst)

# Copy tests/ directory recursively
src_tests = os.path.join(SRC, "tests")
dst_tests = os.path.join("/home/crexs/drift", "tests", "core")
if os.path.exists(src_tests):
    for root, dirs, files in os.walk(src_tests):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            src_path = os.path.join(root, fname)
            rel = os.path.relpath(src_path, src_tests)
            dst_path = os.path.join(dst_tests, rel)
            copy_and_transform(src_path, dst_path)

print("\nDone.")
