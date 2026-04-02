# RAGY UI - Implementation Roadmap

## Overview
Build a rich terminal UI (TUI) for interacting with the RAG database, with automated background maintenance tasks.

## Implementation Steps

### Step 1: Basic Greeting ✅
**Status:** Completed
**Files:** `app.py`, `__main__.py`
**Features:**
- Display welcome screen
- Header and footer
- Quit with 'q' key

**Test:**
```bash
uv run python -m ragy_ui
```

---

### Step 2: Add Slash Commands ✅ (CURRENT)
**Status:** Completed
**Files:** `app.py` (update), `app.css` (update)
**Features:**
- Add input field with slash command support
- Add autocomplete suggestions when user types `/`
- Available commands:
  1. `/search` - Search Web
  2. `/extract` - Extract Data
  3. `/create` - Create Index
  4. `/show-db` - Show DB Content
  5. `/show-emb` - Show Embedding Info
- Commands are placeholders (no functionality yet)

**Test:** Type `/` and see autocomplete suggestions appear

---

### Step 3: Connect ragy_manager Functions
**Files:** `app.py` (update)
**Features:**
- Import ragy_manager functions
- Connect `/search` → execute_web_search (with input prompt)
- Connect `/show-db` → show_db_content (direct display)
- Connect `/show-emb` → show_emb_info (direct display)
- Display output in scrollable panel

**Test:** Test each command, verify output displays

---

### Step 4: Add Progress Bars
**Files:** `app.py` (update)
**Features:**
- Add progress bar widget
- Connect `/extract` → execute_data_extraction (with progress)
- Connect `/create` → execute_index_creation (with progress)
- Show real-time progress updates
- Handle yield pattern from ragy_manager

**Test:** Create small index (5 days), watch progress bar

---

### Step 5: Add Background Scheduler
**Files:** `scheduler.py` (new), `app.py` (update)
**Features:**
- Install APScheduler: `uv add apscheduler`
- Create scheduler module
- Start scheduler on app mount
- Stop scheduler on app unmount
- Schedule tasks every hour (dummy tasks first)
- Add status indicator showing last run time

**Test:** Run app for 2+ hours, verify scheduler executes

---

### Step 6: Add Maintenance Tasks
**Files:** `maintenance.py` (new), `scheduler.py` (update)
**Features:**
- Implement `find_missing_dates()` - detect gaps in daily sequence
- Implement `fill_missing_entries()` - auto-fill gaps by searching web
- Implement `delete_old_entries()` - remove entries older than 365 days
- Connect to scheduler
- Add logging to show what was done
- Display maintenance log in UI

**Test:**
1. Create collection with gaps (skip some dates)
2. Wait 1 hour, verify gaps filled
3. Add old test data (>365 days)
4. Wait 1 hour, verify old data deleted

---

## Technology Stack
- **textual** - Rich TUI framework
- **apscheduler** - Background task scheduling
- **ragy_manager** - Core business logic (already implemented)

## Design Principles
- Incremental development (one step at a time)
- Minimal code changes per step
- Test each step before moving to next
- Keep it simple and functional
