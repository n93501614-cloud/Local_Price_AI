# 🛒 LocalPrice AI

LocalPrice AI is an AI-powered local and online shopping intelligence agent built using SerpApi.

## Features

- Google Shopping price comparison
- Online seller comparison
- Nearby local stores
- Google Maps information
- Store ratings
- Store reviews
- Product details
- Delivery information
- Discount detection
- Smart Deal Score
- AI-style purchase recommendation
- Budget filtering
- Price history
- Price alerts
- Google Lens image search
- Web evidence
- PDF report generation
- SQLite database

## SerpApi APIs Used

- Google Shopping
- Google Maps
- Google Maps Reviews
- Google Product
- Google Search
- Google Lens
- SerpApi Image API

## Installation

Create a virtual environment:

python -m venv .venv

Activate on Windows:

.venv\Scripts\Activate.ps1

Install requirements:

pip install -r requirements.txt

Create `.env`:

SERPAPI_API_KEY=YOUR_API_KEY

Run:

python -m streamlit run app.py

## Important Limitations

Local Maps results do not guarantee that a specific product is available at a specific price.

Online prices are search snapshots and can change.

Delivery information can change.

Always verify the final product variant, price and availability before purchasing.

## Architecture

User

↓

AI Shopping Interface

↓

SerpApi Shopping
SerpApi Maps
SerpApi Reviews
SerpApi Product
SerpApi Search
SerpApi Lens

↓

Data Processing

↓

Deal Scoring

↓

AI Recommendation

↓

User
