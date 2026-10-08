import math
import re


def _num(value):

    if value is None:
        return None

    if isinstance(
        value,
        (int, float)
    ):

        return float(value)


    match = re.search(
        r"[\d,]+(?:\.\d+)?",
        str(value)
    )


    if not match:
        return None


    return float(
        match.group(
            0
        ).replace(
            ",",
            ""
        )
    )


def _price_from_item(product):

    return (

        _num(
            product.get(
                "extracted_price"
            )
        )

        or

        _num(
            product.get(
                "price"
            )
        )

    )


def enrich_products(
    raw_products,
    budget=0
):

    products = []


    for product in raw_products:

        price = _price_from_item(
            product
        )


        if price is None:
            continue


        item = dict(product)


        item["price"] = price


        item["price_text"] = (
            product.get(
                "price"
            )
            or
            f"₹{price:,.0f}"
        )


        item["rating"] = _num(
            product.get(
                "rating"
            )
        )


        item["reviews"] = int(
            _num(
                product.get(
                    "reviews"
                )
            )
            or 0
        )


        item["old_price"] = (
            product.get(
                "old_price"
            )
        )


        item["discount_pct"] = None


        old_price = _num(
            product.get(
                "extracted_old_price"
            )
        )


        if (
            old_price
            and
            old_price > price
        ):

            item["discount_pct"] = round(

                (
                    old_price - price
                )
                /
                old_price
                *
                100,

                1
            )


        item["within_budget"] = bool(

            budget
            and
            price <= budget
        )


        products.append(
            item
        )


    products.sort(
        key=lambda x: x["price"]
    )


    return products


def haversine_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    if None in (
        lat1,
        lon1,
        lat2,
        lon2
    ):

        return None


    radius = 6371.0


    p1 = math.radians(
        lat1
    )

    p2 = math.radians(
        lat2
    )


    dp = math.radians(
        lat2 - lat1
    )

    dl = math.radians(
        lon2 - lon1
    )


    a = (

        math.sin(dp / 2) ** 2

        +

        math.cos(p1)
        *
        math.cos(p2)
        *
        math.sin(dl / 2) ** 2
    )


    return (
        2
        *
        radius
        *
        math.asin(
            math.sqrt(a)
        )
    )


def enrich_stores(
    raw_stores,
    radius_km=10
):

    stores = []


    for store in raw_stores:

        item = dict(store)


        item["rating"] = _num(
            store.get(
                "rating"
            )
        )


        item["reviews"] = int(
            _num(
                store.get(
                    "reviews"
                )
            )
            or 0
        )


        gps = store.get(
            "gps_coordinates",
            {}
        )


        item["lat"] = gps.get(
            "latitude"
        )


        item["lon"] = gps.get(
            "longitude"
        )


        item["open_state"] = (
            store.get(
                "open_state"
            )
        )


        stores.append(
            item
        )


    return stores


def build_recommendation(
    products,
    stores,
    priority,
    budget=0
):

    if not products and not stores:

        return None


    candidates = [

        product

        for product in products

        if (
            not budget
            or
            product["price"] <= budget
        )
    ]


    if not candidates:

        candidates = products[:]


    if not candidates:

        return None


    prices = [

        product["price"]

        for product in candidates
    ]


    minimum_price = min(
        prices
    )

    maximum_price = max(
        prices
    )


    price_span = max(

        maximum_price
        -
        minimum_price,

        1
    )


    def calculate_score(
        product
    ):

        price_score = (

            100
            *
            (
                maximum_price
                -
                product["price"]
            )
            /
            price_span
        )


        rating = (
            product.get(
                "rating"
            )
            or 0
        )


        rating_score = min(

            100,

            rating / 5 * 100
        )


        review_score = min(

            100,

            math.log10(
                (
                    product.get(
                        "reviews"
                    )
                    or 0
                )
                + 1
            )
            /
            4
            *
            100
        )


        discount_score = min(

            100,

            (
                product.get(
                    "discount_pct"
                )
                or 0
            )
            *
            2
        )


        if priority == "Cheapest":

            return (

                0.75
                *
                price_score

                +

                0.15
                *
                rating_score

                +

                0.10
                *
                review_score
            )


        if priority == "Highest Rated":

            return (

                0.25
                *
                price_score

                +

                0.60
                *
                rating_score

                +

                0.15
                *
                review_score
            )


        if priority == "Fastest Delivery":

            return (

                0.30
                *
                price_score

                +

                0.30
                *
                rating_score

                +

                0.20
                *
                review_score

                +

                0.20
                *
                discount_score
            )


        return (

            0.50
            *
            price_score

            +

            0.25
            *
            rating_score

            +

            0.15
            *
            review_score

            +

            0.10
            *
            discount_score
        )


    best = max(
        candidates,
        key=calculate_score
    )


    best_score = round(
        calculate_score(
            best
        )
    )


    reasons = [

        f"Price: {best.get('price_text', 'N/A')}",

        f"Seller: {best.get('source', 'Unknown')}",

        f"Rating: {best.get('rating') or 'N/A'} / 5",

        f"Reviews: {best.get('reviews') or 0:,}"
    ]


    if best.get(
        "delivery"
    ):

        reasons.append(
            f"Delivery: "
            f"{best['delivery']}"
        )


    if best.get(
        "discount_pct"
    ):

        reasons.append(
            f"Estimated discount: "
            f"{best['discount_pct']}%"
        )


    warnings = [

        "Search prices are snapshots; "
        "verify the final checkout price.",

        "A nearby store result does not prove "
        "that the exact product is in stock."
    ]


    return {

        "headline":
            f"Best match: "
            f"{best.get('title', 'product')} "
            f"from "
            f"{best.get('source', 'seller')}",

        "decision":
            "🟢 BUY NOW"
            if best_score >= 75
            else
            "🟡 CHECK BEFORE BUYING",

        "score":
            best_score,

        "best_price_text":
            best.get(
                "price_text",
                "N/A"
            ),

        "rating_text":
            str(
                best.get(
                    "rating"
                )
                or
                "N/A"
            ),

        "explanation":
            (
                "The recommendation balances "
                "price, seller rating, review volume "
                "and discount signals. "
                f"The current top result scores "
                f"{best_score}/100."
            ),

        "reasons":
            reasons,

        "warnings":
            warnings,

        "best_product":
            best
    }
  
