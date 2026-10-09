import os
import streamlit as st
import pandas as pd
from urllib.parse import urlparse

from serpapi_client import SerpApiClient
from database import PriceDB
from scoring import ( 
    enrich_products,
    enrich_stores,
    build_recommendation
)
from reports import create_pdf_report


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LocalPrice AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        max-width: 1400px;
    }

    .hero {
        padding: 30px;
        border-radius: 18px;
        background:
            linear-gradient(
                135deg,
                #111827,
                #1f2937
            );
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        margin: 0 0 8px 0;
        font-size: 38px;
    }

    .hero p {
        margin: 0;
        opacity: 0.85;
        font-size: 17px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🛒 LocalPrice AI</h1>
        <p>
            AI-powered online + local shopping intelligence
            using SerpApi.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SERPAPI KEY
# =========================================================

try:

    api_key = st.secrets[
        "SERPAPI_API_KEY"
    ]

except Exception:

    api_key = os.getenv(
        "SERPAPI_API_KEY",
        ""
    ).strip()


if not api_key:

    st.error(
        "SerpApi API key is not configured."
    )

    st.info(
        "Add SERPAPI_API_KEY in "
        "Streamlit App Settings → Secrets."
    )

    st.stop()


# =========================================================
# CLIENT + DATABASE
# =========================================================

client = SerpApiClient(
    api_key
)

db = PriceDB()


# =========================================================
# SEARCH SECTION
# =========================================================

st.subheader(
    "🔎 Smart Product Search"
)


c1, c2 = st.columns(
    [2, 1]
)


with c1:

    query = st.text_input(
        "What do you want to find?",
        placeholder="e.g. iPhone 17 256GB"
    )


with c2:

    location = st.text_input(
        "Location",
        value="Hyderabad, Telangana, India"
    )


c3, c4, c5 = st.columns(3)


with c3:

    budget = st.number_input(
        "Maximum Budget (₹)",
        min_value=0.0,
        value=0.0,
        step=1000.0
    )


with c4:

    radius_km = st.slider(
        "Local Radius (km)",
        min_value=1,
        max_value=50,
        value=10
    )


with c5:

    priority = st.selectbox(
        "Recommendation Priority",
        [
            "Best Overall",
            "Cheapest",
            "Highest Rated",
            "Nearest",
            "Fastest Delivery"
        ]
    )


search_clicked = st.button(
    "🚀 Find Best Deals",
    type="primary",
    use_container_width=True
)


# =========================================================
# SEARCH
# =========================================================

if search_clicked:

    if not query.strip():

        st.error(
            "Enter a product first."
        )

        st.stop()


    with st.spinner(
        "🔍 Searching Shopping + Maps + Web..."
    ):

        # -------------------------------------------------
        # GOOGLE SHOPPING
        # -------------------------------------------------

        shopping = client.shopping_search(
            query=query,
            location=location
        )


        # -------------------------------------------------
        # GOOGLE MAPS
        # -------------------------------------------------

        stores = client.maps_search(
            query=f"{query} store",
            location=location,
            radius_km=radius_km
        )


        # -------------------------------------------------
        # GOOGLE WEB SEARCH
        # -------------------------------------------------

        web = client.web_search(
            query=f"{query} price {location}",
            location=location
        )


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    if shopping.get("error"):

        st.error(
            "Shopping search error: "
            + str(
                shopping["error"]
            )
        )


    if stores.get("error"):

        st.error(
            "Maps search error: "
            + str(
                stores["error"]
            )
        )


    if web.get("error"):

        st.warning(
            "Web search warning: "
            + str(
                web["error"]
            )
        )
        
    # =====================================================
    # PROCESS ONLINE PRODUCTS
    # =====================================================

    products = enrich_products(
        shopping.get(
            "shopping_results",
            []
        ),
        budget
    )

    # Keep only products with direct seller links
    products = [
        product
        for product in products
        if any(
            isinstance(product.get(field), str)
            and product.get(field).startswith("https://")
            and urlparse(product.get(field)).hostname
            and not (
                "google." in urlparse(product.get(field)).hostname
                or "serpapi.com" in urlparse(product.get(field)).hostname
            )
            for field in (
                "direct_link",
                "link",
                "offer_link",
                "product_url",
            )
        )
    ]
    products = enrich_products(
    shopping.get(
        "shopping_results",
        []
    ),
    budget
)

    # =====================================================
    # PROCESS LOCAL STORES
    # =====================================================

    local_stores = enrich_stores(
        stores.get(
            "local_results",
            []
        ),
        radius_km
    )


    # =====================================================
    # SAVE PRICE SNAPSHOTS
    # =====================================================

    for product in products:

        if product.get(
            "price"
        ) is not None:

            db.save_price(

                product_query=query,

                title=product.get(
                    "title",
                    ""
                ),

                source=product.get(
                    "source",
                    ""
                ),

                price=product.get(
                    "price"
                ),

                url=product.get(
                    "link",
                    ""
                ),

                product_id=product.get(
                    "product_id",
                    ""
                )
            )


    # =====================================================
    # AI RECOMMENDATION
    # =====================================================

    recommendation = build_recommendation(
        products,
        local_stores,
        priority,
        budget
    )


    # =====================================================
    # SAVE SESSION DATA
    # =====================================================

    st.session_state[
        "products"
    ] = products

    st.session_state[
        "stores"
    ] = local_stores

    st.session_state[
        "web"
    ] = web.get(
        "organic_results",
        []
    )

    st.session_state[
        "recommendation"
    ] = recommendation

    st.session_state[
        "query"
    ] = query

    st.session_state[
        "location"
    ] = location

    st.session_state[
        "budget"
    ] = budget


# =========================================================
# RESULTS
# =========================================================

if "products" in st.session_state:

    products = st.session_state[
        "products"
    ]

    stores = st.session_state[
        "stores"
    ]

    web_results = st.session_state[
        "web"
    ]

    recommendation = st.session_state[
        "recommendation"
    ]

    query = st.session_state[
        "query"
    ]

    location = st.session_state[
        "location"
    ]

    budget = st.session_state[
        "budget"
    ]


    # =====================================================
    # RECOMMENDATION SUMMARY
    # =====================================================

    if recommendation:

        st.success(
            "🏆 "
            + str(
                recommendation.get(
                    "headline",
                    "Best deal found"
                )
            )
        )


        a, b, c, d = st.columns(4)


        with a:

            st.metric(
                "Deal Score",
                f"{recommendation.get('score', 0)}/100"
            )


        with b:

            st.metric(
                "Best Price",
                recommendation.get(
                    "best_price_text",
                    "N/A"
                )
            )


        with c:

            st.metric(
                "Rating",
                recommendation.get(
                    "rating_text",
                    "N/A"
                )
            )


        with d:

            st.metric(
                "Local Options",
                str(
                    len(stores)
                )
            )


        st.info(
            recommendation.get(
                "explanation",
                ""
            )
        )


    # =====================================================
    # MAIN TABS
    # =====================================================

    tabs = st.tabs(
        [
            "💰 Online Prices",
            "📍 Nearby Stores",
            "⭐ Reviews",
            "📈 Price History",
            "🧠 AI Decision",
            "📷 Image Search",
            "🌐 Web Evidence",
            "🔔 Price Alerts",
            "📄 Report"
        ]
    )


    # =====================================================
    # TAB 1 — ONLINE PRICES
    # =====================================================

    with tabs[0]:

        st.subheader(
            "💰 Online Price Comparison"
        )


        if not products:

            st.info(
                "No usable priced shopping "
                "results were returned."
            )


        for i, product in enumerate(
            products
        ):

            with st.container(
                border=True
            ):

                cols = st.columns(
                    [
                        3,
                        1.2,
                        1,
                        1.2,
                        1.3
                    ]
                )


                # -----------------------------------------
                # PRODUCT
                # -----------------------------------------

                with cols[0]:

                    st.markdown(
                        "### "
                        + str(
                            product.get(
                                "title",
                                "Unknown product"
                            )
                        )
                    )

                    st.caption(
                        product.get(
                            "source",
                            "Unknown seller"
                        )
                    )


                    if product.get(
                        "snippet"
                    ):

                        st.caption(
                            str(
                                product[
                                    "snippet"
                                ]
                            )[:220]
                        )


                # -----------------------------------------
                # PRICE
                # -----------------------------------------

                with cols[1]:

                    st.metric(
                        "Price",
                        product.get(
                            "price_text",
                            "N/A"
                        )
                    )


                    if product.get(
                        "old_price"
                    ):

                        st.caption(
                            "Old: "
                            + str(
                                product[
                                    "old_price"
                                ]
                            )
                        )


                # -----------------------------------------
                # RATING
                # -----------------------------------------

                with cols[2]:

                    st.metric(
                        "Rating",
                        str(
                            product.get(
                                "rating"
                            )
                            or "N/A"
                        )
                    )

                    st.caption(
                        f"{product.get('reviews', 0) or 0} reviews"
                    )


                # -----------------------------------------
                # DELIVERY
                # -----------------------------------------

                with cols[3]:

                    st.write(
                        product.get(
                            "delivery"
                        )
                        or
                        "Delivery not listed"
                    )


                    if product.get(
                        "tag"
                    ):

                        st.caption(
                            "🏷️ "
                            + str(
                                product[
                                    "tag"
                                ]
                            )
                        )


                # -----------------------------------------
                # ACTIONS
                # -----------------------------------------

                
                
                # -----------------------------------------
                # ACTIONS
                # -----------------------------------------
    
                # -----------------------------------------
                # ACTIONS — OPEN THE ACTUAL SELLER WEBSITE
                # -----------------------------------------

                with cols[4]:

                    
                    from urllib.parse import quote_plus

                    product_title = str(
                        product.get("title")
                        or product.get("name")
                        or ""
                    )

                    seller = str(
                        product.get("source")
                        or product.get("seller")
                        or product.get("merchant")
                        or ""
                    ).lower()

                    # Prefer a genuine direct seller URL.
                    shopping_url = (
                        product.get("direct_link")
                        or product.get("link")
                        or product.get("product_url")
                        or product.get("offer_link")
                    )

                    # Reject Google Shopping URLs as seller URLs.
                    if (
                        isinstance(shopping_url, str)
                        and shopping_url.startswith("https://")
                        and "google." not in shopping_url.lower().split("/")[2]
                        and "serpapi.com" not in shopping_url.lower()
                    ):
                        st.link_button(
                            "🛒 Open Seller Website",
                            shopping_url,
                            key=f"seller_link_{i}"
                        )

                    elif product_title and "amazon" in seller:
                        st.link_button(
                            "🛒 Find on Amazon",
                            "https://www.amazon.in/s?k="
                            + quote_plus(product_title),
                            key=f"seller_link_{i}"
                        )

                    elif product_title and "flipkart" in seller:
                        st.link_button(
                            "🛒 Find on Flipkart",
                            "https://www.flipkart.com/search?q="
                            + quote_plus(product_title),
                            key=f"seller_link_{i}"
                        )

                    else:
                        st.warning(
                            "A direct seller link is unavailable "
                            "for this result. Try another seller."
                        )

                


    # =====================================================
    # TAB 2 — NEARBY STORES
    # =====================================================

    with tabs[1]:

        st.subheader(
            "📍 Nearby Local Stores"
        )


        if not stores:

            st.info(
                "No local store results found."
            )


        for i, store in enumerate(
            stores
        ):

            with st.container(
                border=True
            ):

                cols = st.columns(
                    [
                        2.5,
                        1,
                        1.3,
                        2,
                        1.2
                    ]
                )


                # -----------------------------------------
                # STORE
                # -----------------------------------------

                with cols[0]:

                    st.markdown(
                        "### "
                        + str(
                            store.get(
                                "title",
                                "Unknown store"
                            )
                        )
                    )


                    st.caption(
                        store.get(
                            "type",
                            "Store"
                        )
                    )


                    st.write(
                        store.get(
                            "address",
                            "Address unavailable"
                        )
                    )


                # -----------------------------------------
                # RATING
                # -----------------------------------------

                with cols[1]:

                    st.metric(
                        "Rating",
                        str(
                            store.get(
                                "rating"
                            )
                            or "N/A"
                        )
                    )


                    st.caption(
                        f"{store.get('reviews', 0) or 0} reviews"
                    )


                # -----------------------------------------
                # OPEN STATUS
                # -----------------------------------------

                with cols[2]:

                    if store.get(
                        "open_state"
                    ):

                        st.write(
                            "🟢 Open"
                        )

                    else:

                        st.write(
                            "Status unknown"
                        )


                    if store.get(
                        "hours"
                    ):

                        st.caption(
                            store[
                                "hours"
                            ]
                        )


                # -----------------------------------------
                # CONTACT
                # -----------------------------------------

                with cols[3]:

                    st.write(
                        store.get(
                            "phone"
                        )
                        or
                        "Phone unavailable"
                    )


                    if store.get(
                        "website"
                    ):

                        st.link_button(
                            "Website",
                            store[
                                "website"
                            ]
                        )


                # -----------------------------------------
                # REVIEWS
                # -----------------------------------------

                with cols[4]:

                    if store.get(
                        "data_id"
                    ):

                        if st.button(
                            "Reviews",
                            key=f"review_{i}"
                        ):

                            with st.spinner(
                                "Fetching reviews..."
                            ):

                                review_data = (
                                    client.maps_reviews(
                                        data_id=store[
                                            "data_id"
                                        ]
                                    )
                                )


                            st.session_state[
                                f"reviews_{i}"
                            ] = review_data


                    st.caption(
                        "Price may need "
                        "store confirmation."
                    )


                # -----------------------------------------
                # DISPLAY REVIEWS
                # -----------------------------------------

                review_data = (
                    st.session_state.get(
                        f"reviews_{i}"
                    )
                )


                if review_data:

                    reviews = (
                        review_data.get(
                            "reviews",
                            []
                        )
                    )


                    if reviews:

                        st.write(
                            "**Recent Reviews:**"
                        )


                        for review in (
                            reviews[:5]
                        ):

                            review_text = (
                                review.get(
                                    "snippet"
                                )
                                or
                                review.get(
                                    "extracted_snippet"
                                )
                                or
                                review.get(
                                    "text"
                                )
                                or
                                ""
                            )


                            if review_text:

                                st.write(
                                    f"⭐ "
                                    f"{review.get('rating', '')}"
                                    f" — "
                                    f"{review_text}"
                                )


    # =====================================================
    # TAB 3 — REVIEWS
    # =====================================================

    with tabs[2]:

        st.subheader(
            "⭐ Review Intelligence"
        )


        st.write(
            "Fetch reviews for selected stores "
            "from the Nearby Stores tab."
        )


        review_texts = []


        for key, value in (
            st.session_state.items()
        ):

            if (
                key.startswith(
                    "reviews_"
                )
                and
                isinstance(
                    value,
                    dict
                )
            ):

                for review in value.get(
                    "reviews",
                    []
                ):

                    text = (
                        review.get(
                            "snippet"
                        )
                        or
                        review.get(
                            "extracted_snippet"
                        )
                        or
                        review.get(
                            "text"
                        )
                    )


                    if text:

                        review_texts.append(
                            text
                        )


        if review_texts:

            positive_words = [
                "good",
                "best",
                "great",
                "helpful",
                "fast",
                "excellent",
                "friendly",
                "price",
                "amazing",
                "quality"
            ]


            negative_words = [
                "bad",
                "poor",
                "late",
                "delay",
                "worst",
                "expensive",
                "rude",
                "issue",
                "problem",
                "slow"
            ]


            positive_count = sum(
                sum(
                    word in text.lower()
                    for word in positive_words
                )
                for text in review_texts
            )


            negative_count = sum(
                sum(
                    word in text.lower()
                    for word in negative_words
                )
                for text in review_texts
            )


            if (
                positive_count
                >
                negative_count
            ):

                sentiment = "Positive 😊"

            elif (
                negative_count
                >
                positive_count
            ):

                sentiment = (
                    "Mixed / Negative 😕"
                )

            else:

                sentiment = "Mixed"


            st.metric(
                "Review Sentiment",
                sentiment
            )


            c1, c2 = st.columns(2)


            with c1:

                st.metric(
                    "Positive Signals",
                    positive_count
                )


            with c2:

                st.metric(
                    "Negative Signals",
                    negative_count
                )


            st.write(
                "### Customer Feedback"
            )


            for text in review_texts[:12]:

                st.write(
                    "•",
                    text
                )


        else:

            st.info(
                "Fetch store reviews first."
            )


        # =====================================================
    # PRICE HISTORY
    # =====================================================

    with tabs[3]:

        st.subheader(
            "📈 Price History"
        )

        history = db.get_history(
            query
        )

        if history:

            import pandas as pd

            df = pd.DataFrame(
                history
            )

            # Convert timestamp safely
            df["timestamp"] = pd.to_datetime(
                df["timestamp"],
                errors="coerce"
            )

            # Convert prices to numbers
            df["price"] = pd.to_numeric(
                df["price"],
                errors="coerce"
            )

            # Remove invalid prices
            df = df[
                df["price"].notna()
                & (df["price"] > 0)
            ]

            # Remove extreme outliers
            if len(df) >= 4:

                q1 = df["price"].quantile(0.25)
                q3 = df["price"].quantile(0.75)

                iqr = q3 - q1

                upper_limit = (
                    q3 + (3 * iqr)
                )

                df = df[
                    df["price"] <= upper_limit
                ]

            if not df.empty:

                chart_data = (
                    df.pivot_table(
                        index="timestamp",
                        columns="source",
                        values="price",
                        aggfunc="min"
                    )
                )

                st.line_chart(
                    chart_data,
                    height=450
                )

                st.caption(
                    "📌 Invalid and extreme price outliers "
                    "are excluded from the chart."
                )

                st.dataframe(
                    df.sort_values(
                        "timestamp",
                        ascending=False
                    ),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No valid price history is available yet."
                )

        else:

            st.info(
                "Search a product at least once "
                "to start building price history."
            )


    # =====================================================
    # TAB 5 — AI DECISION
    # =====================================================

    with tabs[4]:

        st.subheader(
            "🧠 Smart Buy Decision"
        )


        if recommendation:

            st.markdown(
                "## "
                + str(
                    recommendation.get(
                        "decision",
                        "🟡 CHECK BEFORE BUYING"
                    )
                )
            )


            st.write(
                recommendation.get(
                    "explanation",
                    ""
                )
            )


            st.write(
                "### Why this recommendation?"
            )


            for reason in recommendation.get(
                "reasons",
                []
            ):

                st.write(
                    "•",
                    reason
                )


            warnings = recommendation.get(
                "warnings",
                []
            )


            if warnings:

                st.write(
                    "### ⚠️ Important Checks"
                )


                for warning in warnings:

                    st.warning(
                        warning
                    )


    # =====================================================
    # TAB 6 — IMAGE SEARCH
    # =====================================================

    with tabs[5]:

        st.subheader(
            "📷 Search by Product Image"
        )


        st.write(
            "Upload a product image and "
            "search for visually similar products."
        )


        uploaded = st.file_uploader(
            "Upload JPG/JPEG/PNG/WebP "
            "(max 500 KB)",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ],
            key="product_image"
        )


        lens_type = st.selectbox(
            "Lens Mode",
            [
                "products",
                "visual_matches",
                "exact_matches"
            ]
        )


        if uploaded:

            st.image(
                uploaded,
                caption="Uploaded Product",
                use_container_width=False
            )


            if st.button(
                "🔍 Find Products From Image"
            ):

                if uploaded.size > (
                    500 * 1024
                ):

                    st.error(
                        "Image must be "
                        "500 KB or smaller."
                    )

                else:

                    with st.spinner(
                        "Uploading image and "
                        "searching Google Lens..."
                    ):

                        image_id = (
                            client.upload_image(
                                uploaded.getvalue(),
                                uploaded.name
                            )
                        )


                        if image_id:

                            lens = (
                                client.lens_search(
                                    image_id=image_id,
                                    search_type=lens_type
                                )
                            )


                            st.session_state[
                                "lens_results"
                            ] = lens

                        else:

                            st.error(
                                "Image upload failed."
                            )


        lens = st.session_state.get(
            "lens_results"
        )


        if lens:

            items = lens.get(
                lens_type,
                []
            )


            if (
                not items
                and
                lens_type == "products"
            ):

                items = lens.get(
                    "visual_matches",
                    []
                )


            if not items:

                st.info(
                    "No visual matches found."
                )


            for item in items[:15]:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "### "
                        + str(
                            item.get(
                                "title",
                                "Visual match"
                            )
                        )
                    )


                    st.write(
                        item.get(
                            "source",
                            ""
                        )
                    )


                    price = item.get(
                        "price"
                    )


                    if isinstance(
                        price,
                        dict
                    ):

                        value = (
                            price.get(
                                "value"
                            )
                            or
                            price.get(
                                "extracted_value"
                            )
                        )


                        if value:

                            st.write(
                                "💰 Price:",
                                value
                            )

                    elif price:

                        st.write(
                            "💰 Price:",
                            price
                        )


                    if item.get(
                        "in_stock"
                    ) is not None:

                        st.write(
                            "📦 In Stock:",
                            item.get(
                                "in_stock"
                            )
                        )


                    if item.get(
                        "link"
                    ):

                        st.link_button(
                            "Open Result",
                            item[
                                "link"
                            ]
                        )


    # =====================================================
    # TAB 7 — WEB EVIDENCE
    # =====================================================

    with tabs[6]:

        st.subheader(
            "🌐 Web Evidence"
        )


        st.write(
            "Supporting web results related "
            "to the product and pricing."
        )


        if not web_results:

            st.info(
                "No web evidence was found."
            )


        for result in web_results[:10]:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### "
                    + str(
                        result.get(
                            "title",
                            ""
                        )
                    )
                )


                if result.get(
                    "snippet"
                ):

                    st.write(
                        result[
                            "snippet"
                        ]
                    )


                if result.get(
                    "link"
                ):

                    st.link_button(
                        "Open Source",
                        result[
                            "link"
                        ]
                    )


    # =====================================================
    # TAB 8 — PRICE ALERTS
    # =====================================================

    with tabs[7]:

        st.subheader(
            "🔔 Price Drop Alerts"
        )


        st.write(
            "Save a target price for this product."
        )


        default_alert = (
            budget
            if budget > 0
            else 50000.0
        )


        alert_price = st.number_input(
            "Alert me when price is at or below (₹)",
            min_value=1.0,
            value=float(
                default_alert
            ),
            step=500.0
        )


        if st.button(
            "➕ Save Price Alert"
        ):

            db.add_alert(
                query,
                alert_price
            )


            st.success(
                "Price alert saved successfully."
            )


        alerts = db.get_alerts()


        if alerts:

            st.write(
                "### Saved Alerts"
            )


            alerts_df = pd.DataFrame(
                alerts
            )


            st.dataframe(
                alerts_df,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info(
                "No price alerts saved yet."
            )


        st.caption(
            "Price alerts are currently stored "
            "locally. Automatic email, WhatsApp "
            "or push notifications can be added "
            "later."
        )


    # =====================================================
    # TAB 9 — PDF REPORT
    # =====================================================

    with tabs[8]:

        st.subheader(
            "📄 Download Report"
        )


        st.write(
            "Generate a complete LocalPrice AI "
            "shopping analysis report."
        )


        if st.button(
            "📄 Generate PDF Report"
        ):

            with st.spinner(
                "Generating PDF report..."
            ):

                pdf_path = (
                    create_pdf_report(

                        query=query,

                        location=location,

                        products=products,

                        stores=stores,

                        recommendation=(
                            recommendation
                        ),

                        history=db.get_history(
                            query
                        )
                    )
                )


            with open(
                pdf_path,
                "rb"
            ) as file:

                st.download_button(

                    "⬇️ Download LocalPrice AI Report",

                    file,

                    file_name=(
                        "localprice_ai_report.pdf"
                    ),

                    mime="application/pdf"
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()


st.caption(
    "LocalPrice AI • "
    "SerpApi-powered shopping intelligence • "
    "Prices and availability are search-result "
    "snapshots and should be verified before purchase."
)
