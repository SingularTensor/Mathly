# Mathly

A gamified arithmetic learning app that applies behavioral game theory to make math practice addictive. Built as a demonstration of engaging UI/UX design and reward system mechanics.

## Concept

Traditional math practice is boring. Mathly applies the same psychological hooks that make mobile games addictive:

- **Variable reward schedules** - XP gains scale with difficulty, creating optimal challenge curves
- **Loss aversion** - Lives system makes each answer feel consequential
- **Progression systems** - Level upgrades provide visible advancement and unlock harder content
- **Session-based goals** - Complete 7 problems to bank XP, creating natural play sessions

## Features

- **4 Arithmetic Sections** - Addition, Subtraction, Multiplication, Division
- **Dynamic Difficulty** - 10 difficulty tiers per section with scaling number ranges
- **XP Economy** - Earn and spend XP to unlock higher difficulty levels
- **Lives System** - 3 lives per session; fail and lose your accumulated XP
- **Progress Tracking** - Per-section statistics and overall skill dashboard
- **User Accounts** - Persistent progress with secure authentication
- **Admin Panel** - Manage users and modify stats

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: Jinja2 templates, vanilla CSS/JS
- **Auth**: Flask-Login with password hashing

## Running Locally

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit `http://localhost:5000`

## Project Status

This is MVP v1 focused on core gameplay loop and UI polish. The foundation is built for expansion into additional math topics and game modes.

## License

MIT
