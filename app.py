import os
import streamlit as st
from dotenv import load_dotenv

from serpapi_client import SerpApiClient
from database import PriceDB
from scoring import enrich_products, enrich_stores, build_recommendation
from reports import create_pdf_report

load_dotenv()

st.set_page_config(
    page_title="LocalPrice AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    max-width: 1400px;
}

.hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(135deg,#111827,#1f2937);
    color: white;
    margin-bottom: 20px;
}

.hero h1 {
    margin: 0 0 8px 0;
}

.hero p {
    margin: 0;
    opacity: .85;
}

.card {
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}

.badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 999px;
    background: #eef2ff;
    margin-right: 5px;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
<h1>🛒 LocalPrice AI</h1>
<p>AI-powered online + local shopping intelligence using SerpApi.</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# API KEY
# =========================================================

try:
    api_key = st.secrets["SERPAPI_API_KEY"]
except Exception:
    api_key = os.getenv(
        "SERPAPI_API_KEY",
        ""
    ).strip()

if not api_key:
    st.error(
        "SerpApi API key is not configured."
    )
    st.stop()
# =========================================================
# SEARCH SECTION
# =========================================================

st.subheader("🔎 Smart Product Search")


c1, c2 = st.columns([2, 1])

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
        1,
        50,
        10
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

        st.error("Enter a product first.")

        st.stop()


    with st.spinner(
        "🔍 Searching Shopping + Maps + Web..."
    ):

        shopping = client.shopping_search(
            query=query,
            location=location
        )

        stores = client.maps_search(
    query=f"{query} store",
    location=location,
    radius_km=radius_km
)
)

        web = client.web_search(
            query=f"{query} price {location}",
            location=location
        )


    if shopping.get("error"):

        st.error(
            f"Shopping search error: "
            f"{shopping['error']}"
        )


    if stores.get("error"):

        st.error(
            f"Maps search error: "
            f"{stores['error']}"
        )


    if web.get("error"):

        st.warning(
            f"Web search warning: "
            f"{web['error']}"
        )


    products = enrich_products(
        shopping.get(
            "shopping_results",
            []
        ),
        budget
    )


    local_stores = enrich_stores(
        stores.get(
            "local_results",
            []
        ),
        radius_km
    )


    # Save price snapshots

    for product in products:

        if product.get("price") is not None:

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


    recommendation = build_recommendation(
        products,
        local_stores,
        priority,
        budget
    )


    st.session_state["products"] = products

    st.session_state["stores"] = local_stores

    st.session_state["web"] = web.get(
        "organic_results",
        []
    )

    st.session_state["recommendation"] = (
        recommendation
    )

    st.session_state["query"] = query

    st.session_state["location"] = location

    st.session_state["budget"] = budget


# =========================================================
# RESULTS
# =========================================================

if "products" in st.session_state:

    products = st.session_state["products"]

    stores = st.session_state["stores"]

    web_results = st.session_state["web"]

    recommendation = (
        st.session_state["recommendation"]
    )

    query = st.session_state["query"]

    location = st.session_state["location"]

    budget = st.session_state["budget"]


    # =====================================================
    # RECOMMENDATION SUMMARY
    # =====================================================

    if recommendation:

        st.success(
            "🏆 " +
            recommendation["headline"]
        )


        a, b, c, d = st.columns(4)


        with a:

            st.metric(
                "Deal Score",
                f"{recommendation['score']}/100"
            )


        with b:

            st.metric(
                "Best Price",
                recommendation[
                    "best_price_text"
                ]
            )


        with c:

            st.metric(
                "Rating",
                recommendation[
                    "rating_text"
                ]
            )


        with d:

            st.metric(
                "Local Options",
                str(len(stores))
            )


        st.info(
            recommendation["explanation"]
        )


    # =====================================================
    # TABS
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
            "📄 Report",
        ]
    )


    # =====================================================
    # ONLINE PRICES
    # =====================================================

    with tabs[0]:

        st.subheader(
            "💰 Online Price Comparison"
        )


        if not products:

            st.info(
                "No usable priced shopping results were returned."
            )


        for i, product in enumerate(products):

            with st.container(border=True):

                cols = st.columns(
                    [3, 1.2, 1, 1.2, 1.3]
                )


                with cols[0]:

                    st.markdown(
                        f"### {product.get('title', 'Unknown product')}"
                    )

                    st.caption(
                        product.get(
                            "source",
                            "Unknown seller"
                        )
                    )

                    if product.get("snippet"):

                        st.caption(
                            product["snippet"][:220]
                        )


                with cols[1]:

                    st.metric(
                        "Price",
                        product.get(
                            "price_text",
                            "N/A"
                        )
                    )

                    if product.get("old_price"):

                        st.caption(
                            f"Old: {product['old_price']}"
                        )


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


                with cols[3]:

                    st.write(
                        product.get(
                            "delivery"
                        )
                        or "Delivery not listed"
                    )

                    if product.get("tag"):

                        st.caption(
                            "🏷️ " +
                            str(
                                product["tag"]
                            )
                        )


                with cols[4]:

                    if product.get("link"):

                        st.link_button(
                            "Open Seller",
                            product["link"]
                        )


                    if product.get("product_id"):

                        if st.button(
                            "Product Details",
                            key=f"prod_{i}"
                        ):

                            with st.spinner(
                                "Loading product details..."
                            ):

                                detail = (
                                    client.product_details(
                                        product_id=product[
                                            "product_id"
                                        ]
                                    )
                                )


                            st.session_state[
                                f"detail_{i}"
                            ] = detail


                detail = st.session_state.get(
                    f"detail_{i}"
                )


                if detail and not detail.get(
                    "error"
                ):

                    product_detail = detail.get(
                        "product_results",
                        {}
                    )


                    with st.expander(
                        "📦 Product Details"
                    ):

                        st.write(
                            "**Description:**",
                            product_detail.get(
                                "description",
                                "Not available"
                            )
                        )


                        specifications = (
                            product_detail.get(
                                "specifications",
                                []
                            )
                        )


                        if specifications:

                            for specification in specifications[
                                :20
                            ]:

                                st.write(
                                    specification
                                )


    # =====================================================
    # LOCAL STORES
    # =====================================================

    with tabs[1]:

        st.subheader(
            "📍 Nearby Local Stores"
        )


        if not stores:

            st.info(
                "No local store results found."
            )


        for i, store in enumerate(stores):

            with st.container(
                border=True
            ):

                cols = st.columns(
                    [2.5, 1, 1.3, 2, 1.2]
                )


                with cols[0]:

                    st.markdown(
                        f"### {store.get('title', 'Unknown store')}"
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


                with cols[2]:

                    st.write(
                        "🟢 Open"
                        if store.get(
                            "open_state"
                        )
                        else
                        "Status unknown"
                    )

                    if store.get("hours"):

                        st.caption(
                            store["hours"]
                        )


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
                            store["website"]
                        )


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
                        "Price may need store confirmation."
                    )


                review_data = st.session_state.get(
                    f"reviews_{i}"
                )


                if review_data:

                    reviews = review_data.get(
                        "reviews",
                        []
                    )


                    if reviews:

                        st.write(
                            "**Recent Reviews:**"
                        )


                        for review in reviews[:5]:

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
    # REVIEWS
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


        for key, value in st.session_state.items():

            if (
                key.startswith("reviews_")
                and isinstance(value, dict)
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
                "price"
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
                "problem"
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


            if positive_count > negative_count:

                sentiment = "Positive"

            elif negative_count > positive_count:

                sentiment = "Mixed / Negative"

            else:

                sentiment = "Mixed"


            st.metric(
                "Rule-Based Sentiment",
                sentiment
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


            df["timestamp"] = (
                pd.to_datetime(
                    df["timestamp"]
                )
            )


            chart_data = (
                df.pivot_table(
                    index="timestamp",
                    columns="source",
                    values="price",
                    aggfunc="min"
                )
            )


            st.line_chart(
                chart_data
            )


            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info(
                "Search a product at least once "
                "to start building price history."
            )


    # =====================================================
    # AI DECISION
    # =====================================================

    with tabs[4]:

        st.subheader(
            "🧠 Smart Buy Decision"
        )


        if recommendation:

            st.markdown(
                f"## {recommendation['decision']}"
            )


            st.write(
                recommendation[
                    "explanation"
                ]
            )


            st.write(
                "### Why this recommendation?"
            )


            for reason in recommendation[
                "reasons"
            ]:

                st.write(
                    "•",
                    reason
                )


            if recommendation.get(
                "warnings"
            ):

                st.write(
                    "### ⚠️ Important Checks"
                )


                for warning in recommendation[
                    "warnings"
                ]:

                    st.warning(
                        warning
                    )


    # =====================================================
    # IMAGE SEARCH
    # =====================================================

    with tabs[5]:

        st.subheader(
            "📷 Search by Product Image"
        )


        uploaded = st.file_uploader(
            "Upload JPG/JPEG/PNG/WebP (max 500 KB)",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ]
        )


        lens_type = st.selectbox(
            "Lens Mode",
            [
                "products",
                "visual_matches",
                "exact_matches"
            ]
        )


        if uploaded and st.button(
            "🔍 Find Products From Image"
        ):

            if uploaded.size > 500 * 1024:

                st.error(
                    "Image must be 500 KB or smaller."
                )

            else:

                with st.spinner(
                    "Uploading image and searching Google Lens..."
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
                and lens_type == "products"
            ):

                items = lens.get(
                    "visual_matches",
                    []
                )


            for item in items[:15]:

                with st.container(
                    border=True
                ):

                    st.write(
                        "###",
                        item.get(
                            "title",
                            "Visual match"
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

                        st.write(
                            "💰",
                            price.get(
                                "value",
                                price.get(
                                    "extracted_value",
                                    ""
                                )
                            )
                        )


                    elif price:

                        st.write(
                            "💰",
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
                            item["link"]
                        )


    # =====================================================
    # WEB RESULTS
    # =====================================================

    with tabs[6]:

        st.subheader(
            "🌐 Web Evidence"
        )


        for result in web_results[:10]:

            st.markdown(
                f"### {result.get('title', '')}"
            )


            st.write(
                result.get(
                    "snippet",
                    ""
                )
            )


            if result.get(
                "link"
            ):

                st.link_button(
                    "Open Source",
                    result["link"]
                )


    # =====================================================
    # PRICE ALERTS
    # =====================================================

    with tabs[7]:

        st.subheader(
            "🔔 Price Drop Alerts"
        )


        alert_price = st.number_input(
            "Alert me when price is at or below (₹)",
            min_value=1.0,
            value=max(
                1.0,
                budget
                if budget
                else 50000.0
            )
        )


        if st.button(
            "➕ Save Price Alert"
        ):

            db.add_alert(
                query,
                alert_price
            )


            st.success(
                "Price alert saved."
            )


        alerts = db.get_alerts()


        if alerts:

            import pandas as pd


            st.dataframe(
                pd.DataFrame(
                    alerts
                ),
                use_container_width=True,
                hide_index=True
            )


        st.caption(
            "Alerts are stored locally. "
            "Automatic email/WhatsApp/push notifications "
            "require a scheduled notification service."
        )


    # =====================================================
    # PDF REPORT
    # =====================================================

    with tabs[8]:

        st.subheader(
            "📄 Download Report"
        )


        if st.button(
            "Generate PDF Report"
        ):

            pdf_path = create_pdf_report(

                query=query,

                location=location,

                products=products,

                stores=stores,

                recommendation=recommendation,

                history=db.get_history(
                    query
                )
            )


            with open(
                pdf_path,
                "rb"
            ) as file:

                st.download_button(

                    "⬇️ Download LocalPrice AI Report",

                    file,

                    file_name="localprice_ai_report.pdf",

                    mime="application/pdf"
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "LocalPrice AI • SerpApi-powered shopping intelligence • "
    "Prices and availability are search-result snapshots "
    "and should be verified before purchase."
)
