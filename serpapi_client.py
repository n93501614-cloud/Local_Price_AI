import requests
from typing import Optional


BASE_URL = "https://serpapi.com/search.json"
IMAGE_URL = "https://serpapi.com/image"


class SerpApiClient:

    def __init__(
        self,
        api_key: str,
        timeout: int = 45
    ):
        self.api_key = api_key
        self.timeout = timeout

    # =====================================================
    # COMMON SEARCH
    # =====================================================

    def _search(
        self,
        engine: str,
        **params
    ):
        payload = {
            "engine": engine,
            "api_key": self.api_key,
            "output": "json",
            **{
                key: value
                for key, value in params.items()
                if value not in (None, "")
            }
        }

        try:

            response = requests.get(
                BASE_URL,
                params=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            if "error" in data:

                return {
                    "error": data["error"]
                }

            return data

        except requests.RequestException as error:

            return {
                "error":
                    f"Network/API error: {error}"
            }

        except ValueError:

            return {
                "error":
                    "SerpApi returned invalid JSON."
            }

    # =====================================================
    # GOOGLE SHOPPING
    # =====================================================

    def shopping_search(
        self,
        query: str,
        location: str = ""
    ):

        return self._search(
            "google_shopping",
            q=query,
            location=location,
            gl="in",
            hl="en",
            currency="INR"
        )
            def maps_search(
        self,
        query: str,
        location: str = "",
        lat=None,
        lon=None,
        radius_km: int = 10
    ):
        full_query = f"{query} {location}".strip()

        params = {
            "q": full_query,
            "type": "search",
            "hl": "en",
            "gl": "in"
        }

        if lat is not None and lon is not None:
            params["ll"] = f"@{lat},{lon},14z"

        return self._search(
            "google_maps",
            **params
        )

    # =====================================================
    # GOOGLE MAPS
    # =====================================================
def maps_search(
    self,
    query: str,
    location: str = "",
    lat=None,
    lon=None,
    radius_km: int = 10
):

    params = {
        "q": query,
        "type": "search",
        "hl": "en",
        "gl": "in"
    }

    # Only use coordinates if they are actually supplied.
    if lat is not None and lon is not None:

        params["ll"] = (
            f"@{lat},{lon},14z"
        )

    return self._search(
        "google_maps",
        **params
    )
    
    # =====================================================
    # GOOGLE MAPS REVIEWS
    # =====================================================

    def maps_reviews(
        self,
        data_id: str = "",
        place_id: str = ""
    ):

        return self._search(
            "google_maps_reviews",

            data_id=(
                data_id
                if data_id
                else None
            ),

            place_id=(
                place_id
                if place_id
                else None
            ),

            sort_by="newestFirst",

            hl="en",

            num=10
        )

    # =====================================================
    # GOOGLE PRODUCT
    # =====================================================

    def product_details(
        self,
        product_id: str = "",
        page_token: str = ""
    ):

        return self._search(
            "google_product",

            product_id=(
                product_id
                if product_id
                else None
            ),

            page_token=(
                page_token
                if page_token
                else None
            ),

            gl="in",
            hl="en",
            currency="INR"
        )

    # =====================================================
    # GOOGLE WEB SEARCH
    # =====================================================

    def web_search(
        self,
        query: str,
        location: str = ""
    ):

        return self._search(
            "google",
            q=query,
            location=location,
            gl="in",
            hl="en"
        )

    # =====================================================
    # GOOGLE LENS
    # =====================================================

    def lens_search(
        self,
        image_id: str,
        search_type: str = "products"
    ):

        return self._search(
            "google_lens",

            image_id=image_id,

            type=search_type,

            country="IN",

            hl="en"
        )

    # =====================================================
    # IMAGE UPLOAD
    # =====================================================

    def upload_image(
        self,
        content: bytes,
        filename: str
    ):

        try:

            files = {
                "image": (
                    filename,
                    content
                )
            }

            data = {
                "api_key":
                    self.api_key
            }

            response = requests.post(
                IMAGE_URL,
                files=files,
                data=data,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.json()

            if "error" in result:

                return None

            return result.get(
                "image_id"
            )

        except requests.RequestException:

            return None
