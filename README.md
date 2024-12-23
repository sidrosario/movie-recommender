# Movie Recommender System

## Overview
Natural language movie recommendation system using OpenAI GPT-3.5, Marqo vector search, and SQLite database.

## Prerequisites
- Python 3.8+
- Docker Desktop
- OpenAI API key
- Git

## Installation
```bash
# Clone repository
git clone <repository-url>
cd movie-recommender

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
## Configuration
1. Setup OPENAI KEY in your environment.

2. Start Marqo
```bash
docker run -p 8882:8882 marqoai/marqo:latest
```

## Database Setup
```bash
# Initialize databases
python initialiser.py
```
This will:
- Create SQLite database
- Load movies from CSV into SQLite DB
- Create vector index (using Marqo)
- Import movie metadata

## Usage
Run application:
```bash
python main.py
```