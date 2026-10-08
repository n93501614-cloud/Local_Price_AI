import math
import re
import requests
import streamlit as st
from textblob import TextBlob


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Local Price Finder AI",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONFIGURATION
# ============================================================

SERPAPI_API_KEY = st.secrets.get("SERPAPI_API_KEY", "")

# Keep Demo Mode selected while testing.
# The user can switch to Live SerpApi from the main page.
DEFAULT_MODE = "🎭 Demo Mode"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 900px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        text-align: center;
        padding: 10px 0 18px 0;
    }

    .hero-title {
        font-size: 34px;
        font-weight: 850;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        color: #6b7280;
        font-size: 14px;
        line-height: 1.5;
    }

    .section-title {
        font-size: 20px;
        font-weight: 800;
        margin-top: 24px;
        margin-bottom: 12px;
    }

    .card {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 16px;
        margin: 10px 0;
        background: #ffffff;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }

    .card-title {
        font-size: 16px;
        font-weight: 750;
        margin-bottom: 7px;
    }

    .price {
        font-size: 25px;
        font-weight: 850;
        margin-bottom: 6px;
    }

    .muted {
        color: #6b7280;
        font-size: 12px;
        line-height: 1.65;
    }

    .deal-card {
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 17px;
        background: #f0fdf4;
        margin: 10px 0;
    }

    .deal-title {
        font-size: 18px;
        font-weight: 800;
    }

    .review-card {
        border: 1px solid #e5e7eb;
        border-radius: 13px;
        padding: 14px;
        margin: 9px 0;
        background: #fafafa;
    }

    .review-text {
        color: #374151;
        font-size: 13px;
        line-height: 1.65;
    }

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 11px;
        padding-top: 30px;
    }

    div.stButton > button,
    div.stLinkButton > a {
        border-radius: 10px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "priced_results" not in st.session_state:
    st.session_state.priced_results = []

if "store_results" not in st.session_state:
    st.session_state.store_results = []


# ============================================================
# HELPERS
# ============================================================

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default

        if isinstance(value, str):
            value = (
                value.replace("₹", "")
                .replace(",", "")
                .replace("$", "")
                .strip()
            )

        return float(value)
    except Exception:
        return default


def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def haversine_km(lat1, lon1, lat2, lon2):
    try:
        earth_radius = 6371.0

        lat1 = math.radians(float(lat1))
        lon1 = math.radians(float(lon1))
        lat2 = math.radians(float(lat2))
        lon2 = math.radians(float(lon2))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )

        return earth_radius * 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )
    except Exception:
        return None


def normalize_price(item):
    return safe_float(
        item.get(
            "extracted_price",
            item.get("price", 0),
        )
    )


def condition_matches(item, selected_condition):
    if selected_condition == "Any":
        return True

    raw = clean_text(
        item.get("second_hand_condition", "")
    ).lower()

    title = clean_text(
        item.get("title", "")
    ).lower()

    if selected_condition == "Used":
        return (
            "used" in raw
            or "used" in title
            or "second hand" in title
        )

    if selected_condition == "Refurbished":
        return (
            "refurbished" in raw
            or "renewed" in title
            or "refurbished" in title
        )

    if selected_condition == "New":
        return (
            raw == ""
            or "new" in raw
            or (
                "used" not in title
                and "refurbished" not in title
                and "renewed" not in title
            )
        )

    return True


# ============================================================
# DEMO DATA
# ============================================================

def demo_price_results(product, location):
    return [
        {
            "title": f"{product} — Amazon",
            "price": "₹74,999",
            "extracted_price": 74999,
            "rating": 4.6,
            "reviews": 1240,
            "source": "Amazon",
            "delivery": "Free Delivery",
            "second_hand_condition": "New",
            "product_id": "demo-amazon",
            "product_link": "https://www.amazon.in/",
        },
        {
            "title": f"{product} — Flipkart",
            "price": "₹72,499",
            "extracted_price": 72499,
            "rating": 4.5,
            "reviews": 892,
            "source": "Flipkart",
            "delivery": "Free Delivery",
            "second_hand_condition": "New",
            "product_id": "demo-flipkart",
            "product_link": "https://www.flipkart.com/",
        },
        {
            "title": f"{product} — Croma",
            "price": "₹76,990",
            "extracted_price": 76990,
            "rating": 4.4,
            "reviews": 621,
            "source": "Croma",
            "delivery": "Delivery Available",
            "second_hand_condition": "New",
            "product_id": "demo-croma",
            "product_link": "https://www.croma.com/",
        },
        {
            "title": f"{product} — Reliance Digital",
            "price": "₹78,499",
            "extracted_price": 78499,
            "rating": 4.3,
            "reviews": 514,
            "source": "Reliance Digital",
            "delivery": "Delivery Available",
            "second_hand_condition": "New",
            "product_id": "demo-reliance",
            "product_link": "https://www.reliancedigital.in/",
        },
    ]


def demo_stores(product, location):
    return [
        {
            "name": "Yashu Digital World",
            "address": "Giri Nagar, Kukatpally, Hyderabad",
            "distance_km": 4.8,
            "rating": 5.0,
            "reviews": 792,
            "phone": "091339 1995",
            "link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=Yashu+Digital+World+Hyderabad"
            ),
        },
        {
            "name": "Croma",
            "address": "Forum Sujana Mall, Kukatpally, Hyderabad",
            "distance_km": 6.2,
            "rating": 4.4,
            "reviews": 1240,
            "phone": "040 4000 0000",
            "link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=Croma+Kukatpally+Hyderabad"
            ),
        },
        {
            "name": "Reliance Digital",
            "address": "Manjeera Mall, Kukatpally, Hyderabad",
            "distance_km": 7.1,
            "rating": 4.3,
            "reviews": 918,
            "phone": "040 4000 1111",
            "link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=Reliance+Digital+Kukatpally+Hyderabad"
            ),
        },
    ]


def demo_reviews(product):
    return {
        "rating": 4.6,
        "review_count": 1240,
        "reviews": [
            {
                "text": (
                    "The product quality is excellent and performance "
                    "is very smooth. Battery life is also impressive."
                ),
                "rating": 5,
                "title": "Excellent product",
            },
            {
                "text": (
                    "Good performance and premium build quality. "
                    "Delivery was quick and the product arrived safely."
                ),
                "rating": 5,
                "title": "Worth the price",
            },
            {
                "text": (
                    "The performance is good but the price is slightly "
                    "high compared to other products."
                ),
                "rating": 4,
                "title": "Good overall",
            },
            {
                "text": (
                    "Very satisfied with the purchase. Everything works "
                    "perfectly and the quality feels premium."
                ),
                "rating": 5,
                "title": "Very satisfied",
            },
        ],
    }


# ============================================================
# SERPAPI REQUESTS
# ============================================================

def serpapi_get(params):
    if not SERPAPI_API_KEY:
        return None, "missing_key"

    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            params={
                **params,
                "api_key": SERPAPI_API_KEY,
            },
            timeout=30,
        )

        if response.status_code == 401:
            return None, "unauthorized"

        if response.status_code == 429:
            return None, "quota"

        if response.status_code != 200:
            return None, f"http_{response.status_code}"

        data = response.json()

        if data.get("error"):
            return None, "api_error"

        return data, "ok"

    except requests.RequestException:
        return None, "network"


@st.cache_data(ttl=1800, show_spinner=False)
def search_product_prices_live(product, location):
    data, status = serpapi_get(
        {
            "engine": "google_shopping",
            "q": product,
            "location": location,
            "hl": "en",
            "gl": "in",
        }
    )

    if status != "ok":
        return [], status

    return data.get("shopping_results", []), "ok"


@st.cache_data(ttl=1800, show_spinner=False)
def search_local_stores_live(product, location, radius_km):
    data, status = serpapi_get(
        {
            "engine": "google_maps",
            "q": f"{product} store",
            "location": location,
            "m": int(radius_km * 1000),
            "type": "search",
            "hl": "en",
            "gl": "in",
        }
    )

    if status != "ok":
        return [], status

    stores = []

    for place in data.get("local_results", []):
        gps = place.get("gps_coordinates", {})

        stores.append(
            {
                "name": place.get("title", "Unknown Store"),
                "address": place.get(
                    "address",
                    "Address unavailable",
                ),
                "rating": place.get("rating", "N/A"),
                "reviews": place.get("reviews", 0),
                "phone": place.get("phone", "N/A"),
                "link": (
                    place.get("links", {}).get("directions")
                    or place.get("link")
                    or ""
                ),
                "distance_km": place.get(
                    "distance",
                    "N/A",
                ),
                "gps": gps,
            }
        )

    return stores, "ok"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_product_reviews_live(product_id, page_token=""):
    params = {
        "engine": "google_product",
        "hl": "en",
        "gl": "in",
    }

    if page_token:
        params["page_token"] = page_token
    else:
        params["product_id"] = product_id
        params["offer_view"] = "true"

    data, status = serpapi_get(params)

    if status != "ok":
        return None, status

    product_results = data.get("product_results", {})

    raw_reviews = data.get(
        "user_reviews",
        product_results.get("user_reviews", []),
    )

    actual_reviews = []

    for review in raw_reviews:
        text = clean_text(review.get("text", ""))

        if text:
            actual_reviews.append(
                {
                    "text": text,
                    "rating": review.get("rating", "N/A"),
                    "title": review.get("title", ""),
                    "date": review.get("date", ""),
                    "source": review.get("source", ""),
                    "link": review.get("link", ""),
                }
            )

    if not actual_reviews:
        return None, "no_review_text"

    return {
        "rating": product_results.get(
            "rating",
            data.get("rating", "N/A"),
        ),
        "review_count": product_results.get(
            "reviews",
            data.get("reviews", 0),
        ),
        "reviews": actual_reviews,
    }, "ok"


# ============================================================
# REVIEW SENTIMENT
# ============================================================

def analyze_customer_reviews(reviews):
    polarities = []

    positive = 0
    neutral = 0
    negative = 0

    for review in reviews:
        text = clean_text(review.get("text", ""))

        if not text:
            continue

        polarity = TextBlob(text).sentiment.polarity
        polarities.append(polarity)

        if polarity > 0.10:
            positive += 1
        elif polarity < -0.10:
            negative += 1
        else:
            neutral += 1

    if not polarities:
        return None

    average = sum(polarities) / len(polarities)

    score = round(
        max(0, min(100, (average + 1) * 50)),
        1,
    )

    if average > 0.25:
        sentiment = "😊 Very Positive"
    elif average > 0.05:
        sentiment = "🙂 Positive"
    elif average < -0.20:
        sentiment = "😞 Negative"
    elif average < -0.05:
        sentiment = "😐 Slightly Negative"
    else:
        sentiment = "😐 Neutral"

    return {
        "score": score,
        "sentiment": sentiment,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "analyzed": len(polarities),
    }


# ============================================================
# SORTING / RECOMMENDATION
# ============================================================

def sort_products(results, priority):
    if priority == "Lowest Price":
        return sorted(
            results,
            key=normalize_price,
        )

    if priority == "Best Rating":
        return sorted(
            results,
            key=lambda x: safe_float(x.get("rating", 0)),
            reverse=True,
        )

    if priority == "Best Overall Deal":
        def score(item):
            price = normalize_price(item)
            rating = safe_float(item.get("rating", 0))
            reviews = safe_float(item.get("reviews", 0))

            price_score = (
                0
                if price <= 0
                else max(0, 50 - price / 2000)
            )

            rating_score = (rating / 5) * 30
            review_score = min(reviews / 1000, 1) * 20

            return price_score + rating_score + review_score

        return sorted(
            results,
            key=score,
            reverse=True,
        )

    return results


def deal_score(item):
    price = normalize_price(item)
    rating = safe_float(item.get("rating", 0))
    reviews = safe_float(item.get("reviews", 0))

    if price <= 0:
        return 0

    return round(
        min(
            100,
            (rating / 5) * 60
            + min(reviews / 1000, 1) * 20
            + 20,
        ),
        1,
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            🛍️ Local Price Finder AI
        </div>
        <div class="hero-subtitle">
            Compare online prices, discover nearby stores,
            analyze customer reviews and find the smartest deal.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MODE
# ============================================================

mode = st.radio(
    "⚙️ Search Mode",
    ["🎭 Demo Mode", "🌐 Live SerpApi"],
    index=0,
    horizontal=True,
)

if mode == "🎭 Demo Mode":
    st.info(
        "🎭 Demo Mode is active. No SerpApi requests are used."
    )
else:
    if SERPAPI_API_KEY:
        st.success("🟢 SerpApi key detected.")
    else:
        st.error(
            "🔴 SerpApi key is missing. Add SERPAPI_API_KEY "
            "in Streamlit Secrets."
        )


# ============================================================
# SEARCH INPUTS
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Search Product</div>',
    unsafe_allow_html=True,
)

product = st.text_input(
    "🛍️ Product",
    placeholder="Example: iPhone 16",
)

location = st.text_input(
    "📍 Location",
    value="Hyderabad",
    placeholder="Example: Hyderabad",
)

col1, col2 = st.columns(2)

with col1:
    max_budget = st.number_input(
        "💰 Maximum Budget (₹)",
        min_value=0,
        value=100000,
        step=1000,
    )

with col2:
    radius_km = st.selectbox(
        "📍 Store Search Radius",
        [5, 10, 25, 50],
        index=0,
        format_func=lambda x: f"{x} km",
    )

condition = st.selectbox(
    "📦 Product Condition",
    ["Any", "New", "Used", "Refurbished"],
)

priority = st.selectbox(
    "⭐ Shopping Priority",
    [
        "Best Overall Deal",
        "Lowest Price",
        "Nearest Store",
        "Best Rating",
    ],
)


# ============================================================
# PRICE SEARCH
# ============================================================

if st.button(
    "🔎 Find Best Prices",
    use_container_width=True,
):
    if not product.strip():
        st.warning("⚠️ Please enter a product name.")
    elif not location.strip():
        st.warning("⚠️ Please enter a location.")
    else:
        with st.spinner("🔍 Finding the best prices..."):
            if mode == "🎭 Demo Mode":
                results = demo_price_results(
                    product,
                    location,
                )
                status = "ok"
            else:
                results, status = search_product_prices_live(
                    product,
                    location,
                )

            if status == "quota":
                st.error(
                    "⚠️ SerpApi request limit reached. "
                    "Switch to Demo Mode."
                )
                results = []

            elif status == "unauthorized":
                st.error(
                    "🔐 SerpApi authentication failed. "
                    "Check the API key in Streamlit Secrets."
                )
                results = []

            elif status == "missing_key":
                st.error(
                    "🔑 SERPAPI_API_KEY is missing."
                )
                results = []

            elif status != "ok":
                st.error(
                    "⚠️ Could not retrieve shopping results."
                )
                results = []

            filtered = []

            for item in results:
                price = normalize_price(item)

                if max_budget > 0 and price > max_budget:
                    continue

                if not condition_matches(
                    item,
                    condition,
                ):
                    continue

                filtered.append(item)

            # If a strict condition filter removes everything,
            # keep the user from seeing a confusing blank page.
            if not filtered and results:
                st.info(
                    "No exact condition matches were found. "
                    "Showing the available results instead."
                )
                filtered = results

            results = sort_products(
                filtered,
                priority,
            )

            st.session_state.priced_results = results


# ============================================================
# ONLINE RESULTS
# ============================================================

priced_results = st.session_state.priced_results

if priced_results:
    st.markdown("---")

    st.markdown(
        '<div class="section-title">💰 Best Online Prices</div>',
        unsafe_allow_html=True,
    )

    prices = [
        normalize_price(item)
        for item in priced_results
        if normalize_price(item) > 0
    ]

    if prices:
        lowest = min(prices)
        highest = max(prices)
        savings = max(0, highest - lowest)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Lowest Price",
                f"₹{lowest:,.0f}",
            )

        with c2:
            st.metric(
                "Highest Price",
                f"₹{highest:,.0f}",
            )

        with c3:
            st.metric(
                "Potential Savings",
                f"₹{savings:,.0f}",
            )

    for item in priced_results:
        title = clean_text(
            item.get("title", "Product")
        )

        price = normalize_price(item)

        rating = item.get(
            "rating",
            "N/A",
        )

        reviews = item.get(
            "reviews",
            0,
        )

        source = item.get(
            "source",
            item.get(
                "merchant",
                "Online Store",
            ),
        )

        delivery = item.get(
            "delivery",
            "Delivery information unavailable",
        )

        condition_text = item.get(
            "second_hand_condition",
            "",
        )

        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">
                    🛍️ {title}
                </div>

                <div class="price">
                    ₹{price:,.0f}
                </div>

                <div class="muted">
                    ⭐ Rating: {rating}
                    &nbsp; • &nbsp;
                    💬 Reviews: {reviews}
                    <br>
                    🏪 Store: {source}
                    <br>
                    🚚 {delivery}
                    {f"<br>📦 Condition: {condition_text}" if condition_text else ""}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        product_link = item.get(
            "product_link",
            item.get("link", ""),
        )

        if product_link:
            st.link_button(
                "🌐 Visit Website",
                product_link,
                use_container_width=True,
            )


    # ========================================================
    # SMART DEAL RECOMMENDATION
    # ========================================================

    st.markdown(
        '<div class="section-title">🤖 Smart Deal Recommendation</div>',
        unsafe_allow_html=True,
    )

    best_item = priced_results[0]

    best_price = normalize_price(best_item)
    best_rating = safe_float(
        best_item.get("rating", 0)
    )
    best_reviews = safe_float(
        best_item.get("reviews", 0)
    )

    best_source = best_item.get(
        "source",
        "Online Store",
    )

    score = deal_score(best_item)

    st.markdown(
        f"""
        <div class="deal-card">
            <div class="deal-title">
                🏆 Recommended Deal
            </div>

            <div class="muted">
                <br>
                <b>{best_item.get("title", product)}</b>
                <br><br>
                💰 Price: <b>₹{best_price:,.0f}</b>
                <br>
                ⭐ Rating: <b>{best_rating}/5</b>
                <br>
                💬 Reviews: <b>{int(best_reviews)}</b>
                <br>
                🏪 Seller: <b>{best_source}</b>
                <br>
                🎯 Deal Score: <b>{score}/100</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# NEARBY STORES
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">📍 Nearby Local Stores</div>',
    unsafe_allow_html=True,
)

if st.button(
    "📍 Find Nearby Stores",
    use_container_width=True,
):
    if not product.strip():
        st.warning("⚠️ Please enter a product name first.")
    elif not location.strip():
        st.warning("⚠️ Please enter a location first.")
    else:
        with st.spinner("📍 Finding nearby stores..."):
            if mode == "🎭 Demo Mode":
                stores = demo_stores(
                    product,
                    location,
                )
                status = "ok"
            else:
                stores, status = search_local_stores_live(
                    product,
                    location,
                    radius_km,
                )

            if status == "quota":
                st.error(
                    "⚠️ SerpApi request limit reached. "
                    "Switch to Demo Mode."
                )
                stores = []

            elif status == "unauthorized":
                st.error(
                    "🔐 SerpApi authentication failed."
                )
                stores = []

            elif status == "missing_key":
                st.error(
                    "🔑 SERPAPI_API_KEY is missing."
                )
                stores = []

            elif status != "ok":
                st.error(
                    "⚠️ Could not retrieve nearby stores."
                )
                stores = []

            st.session_state.store_results = stores


store_results = st.session_state.store_results

if store_results:
    st.success(
        f"Found {len(store_results)} nearby store(s)."
    )

    for store in store_results:
        name = clean_text(
            store.get("name", "Local Store")
        )

        address = clean_text(
            store.get(
                "address",
                "Address unavailable",
            )
        )

        distance = store.get(
            "distance_km",
            "N/A",
        )

        rating = store.get(
            "rating",
            "N/A",
        )

        reviews = store.get(
            "reviews",
            0,
        )

        phone = store.get(
            "phone",
            "N/A",
        )

        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">
                    🏪 {name}
                </div>

                <div class="muted">
                    📍 {address}
                    <br>
                    📏 Distance: <b>{distance}</b>
                    <br>
                    ⭐ Rating: <b>{rating}</b>
                    &nbsp; • &nbsp;
                    💬 Reviews: <b>{reviews}</b>
                    <br>
                    📞 Phone: {phone}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        link = store.get("link", "")

        if link:
            st.link_button(
                "🗺️ Get Directions",
                link,
                use_container_width=True,
            )


# ============================================================
# AI CUSTOMER REVIEW ANALYSIS
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">⭐ AI Customer Review Analysis</div>',
    unsafe_allow_html=True,
)

if priced_results:
    reviewed_products = []

    with st.spinner(
        "🔍 Checking products for real customer reviews..."
    ):
        for item in priced_results[:3]:
            if mode == "🎭 Demo Mode":
                review_data = demo_reviews(
                    item.get("title", product)
                )
            else:
                product_id = item.get("product_id", "")
                page_token = item.get(
                    "immersive_product_page_token",
                    "",
                )

                if not product_id and not page_token:
                    continue

                review_data, status = fetch_product_reviews_live(
                    product_id,
                    page_token,
                )

                if status == "quota":
                    st.warning(
                        "⚠️ Review API limit reached. "
                        "Showing only reviews already available."
                    )
                    continue

            # IMPORTANT:
            # Only products containing actual review text
            # are included in AI Customer Review Analysis.
            if review_data and review_data.get("reviews"):
                reviewed_products.append(
                    {
                        "product": item,
                        "review_data": review_data,
                    }
                )

    if reviewed_products:
        for entry in reviewed_products:
            item = entry["product"]
            review_data = entry["review_data"]

            reviews = review_data.get(
                "reviews",
                [],
            )

            analysis = analyze_customer_reviews(
                reviews
            )

            if not analysis:
                continue

            st.markdown(
                f"### 🛍️ {item.get('title', product)}"
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Customer Rating",
                    f"{review_data.get('rating', 'N/A')}/5",
                )

            with c2:
                st.metric(
                    "Review Count",
                    review_data.get(
                        "review_count",
                        0,
                    ),
                )

            with c3:
                st.metric(
                    "Reviews Analyzed",
                    analysis["analyzed"],
                )

            st.markdown(
                f"""
                <div class="review-card">
                    <div style="text-align:center;">
                        <div style="font-size:30px;font-weight:850;">
                            {analysis["score"]}/100
                        </div>
                        <div class="muted">
                            🤖 AI Review Score
                        </div>
                        <br>
                        <b>{analysis["sentiment"]}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            r1, r2, r3 = st.columns(3)

            with r1:
                st.success(
                    f"😊 Positive: {analysis['positive']}"
                )

            with r2:
                st.info(
                    f"😐 Neutral: {analysis['neutral']}"
                )

            with r3:
                st.error(
                    f"😞 Negative: {analysis['negative']}"
                )

            st.markdown(
                "#### 💬 Actual Customer Reviews"
            )

            for review in reviews:
                review_text = clean_text(
                    review.get("text", "")
                )

                if not review_text:
                    continue

                title = clean_text(
                    review.get("title", "")
                )

                rating = review.get(
                    "rating",
                    "N/A",
                )

                date = clean_text(
                    review.get("date", "")
                )

                st.markdown(
                    f"""
                    <div class="review-card">
                        <b>⭐ {rating}/5</b>
                        &nbsp;&nbsp;
                        <b>{title}</b>
                        <br><br>
                        <div class="review-text">
                            "{review_text}"
                        </div>
                        {f'<br><span class="muted">📅 {date}</span>' if date else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        st.info(
            "No products with actual customer review text "
            "were found."
        )
else:
    st.info(
        "🔎 Search for a product first to analyze customer reviews."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🛍️ Local Price Finder AI
        <br>
        Compare • Discover • Save
        <br><br>
        Powered by SerpApi + AI
    </div>
    """,
    unsafe_allow_html=True,
)
