# Grimoire System

## Overview

The Grimoire is a JSON-based knowledge storage system for Trinity Context Core. It contains foundational memories that can be loaded into the vector database.

## Files

### `src/data/initial_memories.json`
Contains 5 foundational context cards:
1. **Identity** - User profile, learning style, goals
2. **Tech Stack** - Python, Rust, Qdrant, Gemini 2.5 Pro
3. **Architecture** - Trinity agents (Haq, Liar's Requiem, Mahoraga)
4. **Coding Rules** - Clean Architecture principles
5. **History** - Mentor Goblini and Context Cards origin

### `src/scripts/load_grimoire.py`
Loader script that imports all memories from the grimoire into the active memory system.

## Usage

```bash
# Load all grimoire memories into the system
python src/scripts/load_grimoire.py
```

## Structure

Each memory card in the grimoire follows this schema:
```json
{
  "content": "The actual knowledge/fact",
  "tags": ["category", "keywords"],
  "source": "system_init",
  "importance": 1-10
}
```

## Results

**Status**: ✅ All 5/5 memories loaded successfully

These foundational memories are now searchable and will provide context to the Trinity agents.
