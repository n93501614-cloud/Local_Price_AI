Local Price Finder AI
No-sidebar Streamlit app for the SerpApi India Hackathon.
Features
Product search
Location search
Maximum budget
Store search radius
Product condition
Shopping priority
Google Shopping price comparison
Deal Score
Smart Deal Recommendation
Nearby local stores using Google Maps
Google Maps directions
Customer rating and review count
AI customer review sentiment analysis
Demo Mode that uses no SerpApi requests
Live SerpApi Mode
Files
app.py
requirements.txt
.gitignore
Local run
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```
Streamlit Secrets
Add this in Streamlit Cloud Secrets:
```toml
SERPAPI_API_KEY = "YOUR_REAL_SERPAPI_KEY"
```
Never commit your real API key to GitHub.
Important
Keep Demo Mode selected while testing if your SerpApi quota is exhausted.
Switch to Live SerpApi only when your API quota is available.
