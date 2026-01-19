# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Vision

**Mathly** is a gamified math learning app targeting general learners and students. The goal is to be *more gamified than Duolingo* — making math practice feel rewarding, satisfying, and addictive through exceptional UX.

### Design Philosophy

The core mechanic stays simple: **select the right answer**. The magic comes from how it *feels*:
- Every correct answer should feel like a win
- Progression should be visible and exciting  
- Users should want "just one more problem"

### Gamification Priorities

1. **Satisfying Feedback** — Animations, sounds, visual rewards for correct answers
2. **Streak System** — Daily streaks, combo multipliers, flame effects
3. **Visual Progression** — XP bars, level-ups with fanfare, skill trees
4. **Achievements** — Badges, milestones, unlock notifications
5. **Character/Avatar** — Customization unlocked through XP
6. **Social/Competitive** — Leaderboards, daily challenges, timed modes

### Current State

- Addition section: Available
- Subtraction, Multiplication, Division, Advanced: Scaffolded but locked (`available: False`)
- User auth, XP system, level progression: Working

---

## Commands

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask development server
python app.py

# Seed the database with sample quizzes (drops existing data)
python seed.py
```

## Architecture

Flask quiz application using SQLAlchemy with SQLite.

**Core files:**
- `app.py` — Flask init, SQLAlchemy config, imports routes
- `routes.py` — All route handlers
- `database.py` — SQLAlchemy models (User, Unit, Quiz, Option, ProblemCategory, UserLevelProgress)
- `seed.py` — Database reset and seed script

**Data flow:** Routes → models from `database.py` → Jinja2 templates in `templates/`

**Database:** SQLite at `instance/game.db`

## Code Style

- No emojis in code
- Minimal comments — only when actually noteworthy

## Visuals

- Reference images in `readhereclaude/` for GUI direction

## Agency

- Feel free to refactor folders or expand scope if adjacent to the task 