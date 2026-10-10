LocalPrice AI
Shopping intelligence for comparing online offers, discovering nearby stores, and making more informed buying decisions.
LocalPrice AI is a Streamlit application that combines SerpApi-powered shopping, local-business, review, web, and visual search with a lightweight recommendation engine. It brings the results into one workflow so a shopper can compare available offers, review seller signals, inspect nearby stores, save price snapshots, and export a shopping report.
Product status: LocalPrice AI is an actively developed prototype. Search results and recommendations are decision-support signals, not guarantees of price, stock, delivery, or seller quality.
Contents
Why LocalPrice AI
Features
How the workflow works
Agent and capability map
Technology stack
Requirements
Quick start
API keys and configuration
SerpApi engines and endpoints
Project structure
Architecture
Data storage and generated reports
Troubleshooting
Current scope and limitations
Extension roadmap
Security notes
Why LocalPrice AI
Online price search and local shopping research often live in separate places. LocalPrice AI combines those research steps into a single interface and adds a transparent, rule-based recommendation layer.
The intended workflow is simple: search → compare → inspect → decide → save → report.
Features
Online price comparison — find matching shopping listings and compare reported prices, sellers, ratings, review counts, and delivery information when available.
Budget-aware discovery — enter a maximum budget and a preferred recommendation priority.
Nearby store discovery — search Google Maps results for relevant stores around a chosen location.
Review lookup and review signals — retrieve reviews for supported Maps results and show lightweight keyword-based feedback signals.
Product details — request additional Google Product information when a result provides a supported product identifier.
Web evidence — surface web results with source links and snippets that can help contextualize a product or price.
Image-based product discovery — upload a supported image and use Google Lens search modes to find products or visual matches.
Price history — store price snapshots locally in SQLite and chart the saved history for a query.
Target-price alerts — save target-price records for later reference.
Downloadable PDF report — export a summary of the search, recommendation, online listings, and nearby stores.
Responsive web interface — use the workflow in a browser through Streamlit.
How the workflow works
Enter the product query and location.
Optionally set a budget, local search radius, and recommendation preference.
Start a search. The application requests Google Shopping, Google Maps, and Google Search data through SerpApi.
Normalize available product/store fields and apply the application's scoring rules.
Review online offers, local listings, review information, web evidence, and the recommendation in the dashboard tabs.
Save price snapshots and target-price records to the local SQLite database.
Generate a PDF report when needed.
Agent and capability map
LocalPrice AI is built as a modular, tool-using workflow. The roles below are task-specific components; they are not separate autonomous LLM agents, and the current recommendation engine does not require an external generative-AI API.
Agent / capability
Main implementation
Responsibility
Output
Shopping Discovery
SerpApiClient.shopping_search()
Searches Google Shopping for the requested product.
Online listings and reported offer details.
Local Store Finder
SerpApiClient.maps_search()
Finds relevant nearby businesses using a location-aware Maps query.
Store names, addresses, contact/opening details, ratings, and coordinates when supplied.
Review Intelligence
SerpApiClient.maps_reviews() plus the review section in app.py
Retrieves reviews for supported Maps listings and summarizes simple positive/negative keyword signals.
Review text and lightweight feedback indicators.
Product Detail Enrichment
SerpApiClient.product_details()
Requests additional product information using a supported product ID.
Additional product details when SerpApi returns them.
Web Evidence
SerpApiClient.web_search()
Finds general web results related to the product, pricing, and location.
Organic results, snippets, and source links.
Visual Product Search
SerpApiClient.upload_image() and SerpApiClient.lens_search()
Uploads an image to SerpApi and searches with Google Lens.
Product, visual-match, or exact-match results when available.
Recommendation Engine
enrich_products(), enrich_stores(), build_recommendation() in scoring.py
Normalizes result fields and computes a rule-based recommendation using available price, rating, review, discount, budget, and priority signals.
Ranked candidate and an explainable buy/check suggestion.
Price Memory and Alerts
PriceDB in database.py
Saves price-history snapshots and target-price records in SQLite.
Local history and saved alert records.
Report Generator
create_pdf_report() in reports.py
Builds a downloadable PDF from the current search results.
localprice_ai_report.pdf.
The components can be extended independently as the product grows. If a future release introduces an LLM or an autonomous agent framework, document its provider, model, tool permissions, and API key separately rather than implying that one is already required.
Technology stack
Layer
Technology
Use
User interface
Streamlit
Search form, dashboard tabs, charts, upload controls, and downloads.
Application language
Python 3.10+ recommended
Application orchestration and business logic.
Search data
SerpApi REST API
Shopping, Maps, Maps reviews, Google Product, Google Search, and Google Lens results.
HTTP requests
requests
Sends requests to SerpApi.
Configuration
Environment variables, python-dotenv, and Streamlit Secrets
Loads the SerpApi API key for local or hosted use.
Data transformation
pandas and Python utility functions
Tabular processing and price-history display.
Recommendation logic
Custom Python rules in scoring.py
Normalization and weighted heuristic scoring; not a trained ML model.
Local persistence
SQLite (sqlite3)
Price snapshots and target-price records.
PDF generation
ReportLab
Creates downloadable shopping reports.
Requirements
Python 3.10 or later is recommended.
A SerpApi account and a valid API key.
Internet access for SerpApi requests.
The dependencies listed in requirements.txt.
No separate Google Maps key, Google Cloud key, OpenAI key, or other LLM key is required by the documented workflow. SerpApi usage is subject to the quotas and billing/credit limits of your SerpApi plan.
Quick start
1. Get the code
git clone https://github.com/n93501614-cloud/Local_Price_AI.git
cd Local_Price_AI
2. Create and activate a virtual environment
Windows PowerShell:
py -m venv .venv
.\.venv\Scripts\Activate.ps1
macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
4. Configure the API key
Copy the example environment file and edit .env:
Windows PowerShell:
Copy-Item .env.example .env
macOS / Linux:
cp .env.example .env
Put your own key in .env:
SERPAPI_API_KEY=your_real_serpapi_key
Do not include quotation marks unless required by your environment, and do not add spaces around the = sign. Keep .env private and out of source control.
Important local setup check: the app must load .env before it reads os.getenv("SERPAPI_API_KEY"). If your current app.py does not already load it, add these lines near the other imports and before the key is read:
from dotenv import load_dotenv
load_dotenv()
The repository's .gitignore should include .env. If the file does not exist, add it before committing.
5. Run the application
python -m streamlit run app.py
Streamlit will print a local URL (usually http://localhost:8501). Open that URL in your browser.
6. Make your first comparison
Type a specific product name or model.
Enter a city or area (for example, Hyderabad, Telangana, India).
Set a budget and comparison preference if required.
Select Find Best Deals.
Use the dashboard tabs to review price listings, stores, review signals, price history, recommendations, image search, and web evidence.
Generate a PDF report when you are ready to save or share the results.
API keys and configuration
Required key
Variable
Required?
Purpose
SERPAPI_API_KEY
Yes
Authenticates requests to SerpApi search engines and the image upload endpoint.
This project uses one SerpApi key for its current external-data workflow. There is no separate key for each SerpApi engine.
Local development
Use a .env file as described in Quick start. The application can read the key from the process environment as well. If both .env and a shell environment variable define the same name, the effective value depends on the python-dotenv loading options and the application's configuration logic.
For a one-session Windows PowerShell alternative, set the environment variable before launching Streamlit:
$env:SERPAPI_API_KEY = "your_real_serpapi_key"
python -m streamlit run app.py
Streamlit Community Cloud
Open the deployed app's settings.
Open Secrets.
Add the following TOML entry (replace the placeholder with your real key):
SERPAPI_API_KEY = "your_real_serpapi_key"
Save the settings and restart/redeploy the app if needed.
Use Streamlit Secrets for hosted deployments rather than committing an .env file. The application version deployed to Streamlit must contain code that reads st.secrets["SERPAPI_API_KEY"] or the appropriate environment variable.
SerpApi engines and endpoints
The search adapter is implemented in serpapi_client.py. It sends search requests to SerpApi's /search.json endpoint and uses the SerpApi image endpoint to upload files for Lens search.
SerpApi engine / endpoint
Method in this project
Purpose
google_shopping
shopping_search()
Retrieves online shopping listings and available offer, price, rating, review, and delivery fields.
google_maps
maps_search()
Discovers local businesses and returns available address, contact, hours, rating, and coordinate fields.
google_maps_reviews
maps_reviews()
Fetches reviews for a Maps result using its supported data_id or place_id.
google_product
product_details()
Requests a product-details result using product_id and, where applicable, page_token.
google
web_search()
Retrieves general web search results for pricing context and supporting sources.
google_lens
lens_search()
Uses an uploaded image ID to return product or visual matches.
SerpApi Image API (/image)
upload_image()
Uploads the user's image and returns the temporary image ID passed to Google Lens.
API calls are made on demand by the application. Results depend on the search query, location, source coverage, SerpApi response fields, service availability, and account limits. Not every search returns every field.
Project structure
Local_Price_AI/
├── app.py                     # Streamlit UI and workflow orchestration
├── serpapi_client.py           # SerpApi HTTP client and engine-specific methods
├── scoring.py                  # Result normalization and recommendation heuristics
├── database.py                 # SQLite tables and data access for history/alerts
├── reports.py                  # PDF report generation
├── requirements.txt            # Python dependencies
├── .env.example                # Example API-key environment file
├── .gitignore                  # Excludes secrets, DB, cache, and generated report
├── run_localprice_ai.bat       # Optional Windows launcher, if included in the checkout
└── README.md                   # Product and developer documentation
Runtime files are created as needed and may not exist in a fresh clone:
localprice_ai.db — SQLite database for price snapshots and saved target-price alerts.
localprice_ai_report.pdf — generated PDF report.
.venv/ — local Python virtual environment, if created.
Architecture
flowchart TD
    U[Shopper] --> UI[Streamlit UI - app.py]
    UI --> S[SerpApiClient - serpapi_client.py]
    S --> GS[Google Shopping]
    S --> GM[Google Maps]
    S --> GR[Google Maps Reviews]
    S --> GP[Google Product]
    S --> GW[Google Search]
    S --> GL[Google Lens + Image Upload]
    GS --> N[Normalize results - scoring.py]
    GM --> N
    GP --> N
    GR --> R[Review display and keyword signals]
    GW --> W[Web evidence]
    GL --> V[Visual matches]
    N --> D[Rule-based recommendation]
    N --> DB[SQLite - database.py]
    DB --> H[Price history and saved alerts]
    D --> UI
    R --> UI
    W --> UI
    V --> UI
    UI --> PDF[PDF generator - reports.py]
Design principles
Modular responsibilities: HTTP integration, scoring, persistence, and reporting are separated into small Python modules.
Explainable recommendations: the decision layer uses visible inputs and weighted rules instead of claiming opaque model predictions.
Graceful handling of external data: SerpApi errors and incomplete result fields should be expected and surfaced to the user.
Local persistence by default: price history and alert records are stored in a local SQLite file unless deployment storage is explicitly configured.
Data storage and generated reports
The SQLite database contains two main tables:
price_history — query, product title, seller/source, price, URL, product ID, and timestamp.
alerts — product query, target price, active flag, and creation timestamp.
Price history is built from searches made through the app. A new search can add a new snapshot; the application cannot reconstruct prices from before it was first used. In hosted environments, local files may not be durable across redeployments unless persistent storage is configured.
The PDF report is generated locally from the current search context and saved price history. It is a point-in-time report, not a live price feed.
Troubleshooting
Symptom
What to check
SerpApi API key is not configured
Confirm .env is in the project root, the variable is spelled SERPAPI_API_KEY, and load_dotenv() runs before reading the environment. For Streamlit Cloud, check the app's Secrets settings.
ModuleNotFoundError
Activate the correct virtual environment and run python -m pip install -r requirements.txt. Confirm pandas is listed if the app imports it.
SerpApi returns an API or quota error
Check the key, available searches/credits, request parameters, and SerpApi account status. Do not publish the key in logs or screenshots.
Results have no price or rating
Not all search listings include those fields. Try a more specific product query and verify the listing on the seller's site.
No local stores appear
Try a more specific location or broader store query. Maps coverage and result availability vary by area.
Image search does not return results
Use a supported JPG, JPEG, PNG, or WebP file within the application's configured size limit, and confirm image upload and Lens requests are succeeding.
Local history or alerts look empty
The database only contains records saved by the running app and matching the requested product query. Check which working directory contains localprice_ai.db.
Current scope and limitations
Prices, discounts, seller ratings, delivery details, and availability are third-party search-result snapshots; they can change and should be verified at checkout.
A Maps listing identifies a business; it does not prove that the exact product is stocked there or that the business's product price is current.
Recommendation scores are application-level heuristics, not model confidence, financial advice, or a guarantee of the best purchase. The current Nearest and Fastest Delivery preference labels should not be interpreted as guaranteed distance-based or delivery-time-based ranking; those capabilities need dedicated scoring and validation.
Review sentiment signals are simple keyword-based indicators, not a trained sentiment-analysis model.
Target-price alerts are saved records. Automatic periodic price checks and email, SMS, WhatsApp, or push notifications are not part of the current documented implementation.
Local SQLite storage is suitable for a small single-instance deployment. A shared database and durable hosted storage would be needed for multi-user production operations.
The project does not currently require an external LLM key; the word “AI” refers to the shopping-intelligence workflow and decision heuristics in the present implementation.
Extension roadmap
Potential next steps for a production-oriented release include:
Scheduled price monitoring — a background scheduler, alert status lifecycle, and email/SMS/push delivery with user consent.
Stronger entity matching — compare model numbers, storage sizes, colors, condition, seller identity, and variant attributes before ranking prices.
Distance-aware local ranking — geocode the shopper's position and calculate dependable distances for nearby-store sorting and radius filtering.
Persistent multi-user storage — replace or augment local SQLite with a managed database, migrations, backups, and account-scoped records.
Test coverage and observability — unit tests for scoring and parsing, API mocks, structured logging, latency metrics, and safe error messages.
Product-grade operations — CI checks, versioned releases, configuration validation, privacy/retention documentation, and deployment health checks.
Optional LLM integration — add natural-language explanations only if useful, document the provider clearly, and keep user data and API credentials protected.
Security notes
Never commit .env, API keys, personal tokens, or Streamlit secrets.
Keep .env in .gitignore; commit .env.example with placeholders only.
If a key is accidentally exposed, revoke or rotate it in the provider dashboard and update the environment configuration.
Do not send confidential images or personal information to external search services. Uploaded images are sent to SerpApi for visual search.
Before offering this as a public service, add an explicit privacy notice, terms of use, abuse controls, and a policy for retaining or deleting query and price-history data.
LocalPrice AI — compare smarter, research with context, and make better-informed shopping decisions.
