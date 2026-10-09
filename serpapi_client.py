import requests
from typing import Optional


BASE_URL = "https://serpapi.com/search.json"
IMAGE_URL = "https://serpapi.com/image"


class SerpApiClient:

    def __init__(self, api_key: str, timeout: int = 45):
        self.api_key = api_key
        self.timeout = timeout

    def _search(self, engine: str, **params):

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
                "error": f"Network/API error: {error}"
            }

        except ValueError:

            return {
                "error": "SerpApi returned invalid JSON."
            }


    # --------------------------------------------------
    # GOOGLE SHOPPING
    # --------------------------------------------------
    
    # --------------------------------------------------
    # GOOGLE SHOPPING
    # --------------------------------------------------

    def shopping_search(
        self,
        query: str,
        location: str = ""
    ):
        from urllib.parse import urlparse

        data = self._search(
            "google_shopping",
            q=query,
            location=location,
            gl="in",
            hl="en",
            currency="INR"
        )

        if not isinstance(data, dict) or data.get("error"):
            return data

        shopping_results = data.get("shopping_results", [])

        for product in shopping_results:
            if not isinstance(product, dict):
                continue

            # Preserve Google's Shopping page URL
            product["google_shopping_link"] = (
                product.get("product_link") or ""
            )

            # Look for a possible direct seller URL
            possible_links = [
                product.get("direct_link"),
                product.get("link"),
                product.get("offer_link"),
                product.get("product_url"),
            ]

            direct_link = ""

            for url in possible_links:
                if not isinstance(url, str):
                    continue

                url = url.strip()

                if not url.startswith(("https://", "http://")):
                    continue

                host = (
                    urlparse(url).hostname or ""
                ).lower()

                if (
                    host == "google.com"
                    or host.endswith(".google.com")
                    or host.endswith(".google.co.in")
                    or host.endswith(".serpapi.com")
                ):
                    continue

                direct_link = url
                break

            product["direct_link"] = direct_link

        return data


        
        
           

            
                

    # --------------------------------------------------
    # GOOGLE MAPS
    # --------------------------------------------------

    def maps_search(
        self,
        query: str,
        location: str = "",
        lat: Optional[float] = None,
        lon: Optional[float] = None,
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

            params["ll"] = (
                f"@{lat},{lon},14z"
            )

        return self._search(
            "google_maps",
            **params
        )


    # --------------------------------------------------
    # GOOGLE MAPS REVIEWS
    # --------------------------------------------------

    def maps_reviews(
        self,
        data_id: str
    ):

        return self._search(
            "google_maps_reviews",
            data_id=data_id,
            hl="en",
            sort_by="qualityScore"
        )


    # --------------------------------------------------
    # GOOGLE SEARCH
    # --------------------------------------------------

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


    # --------------------------------------------------
    # PRODUCT DETAILS
    # --------------------------------------------------

   
    def product_details(
        self,
        product_id: str
    ):
        return self._search(
            "google_product",
            product_id=product_id,
            gl="in",
            hl="en"
        )



    # --------------------------------------------------
    # IMAGE UPLOAD
    # --------------------------------------------------

    def upload_image(
        self,
        image_bytes: bytes,
        filename: str = "image.jpg"
    ):

        try:

            response = requests.post(
                IMAGE_URL,
                files={
                    "file": (
                        filename,
                        image_bytes,
                        "image/jpeg"
                    )
                },
                data={
                    "api_key": self.api_key
                },
                timeout=self.timeout
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            return {
                "error": f"Image upload error: {error}"
            }

        except ValueError:

            return {
                "error": "Image API returned invalid JSON."
            }


    # --------------------------------------------------
    # GOOGLE LENS
    # --------------------------------------------------

           # --------------------------------------------------
    # GOOGLE LENS
    # --------------------------------------------------

    def lens_search(
        self,
        image_id: str = "",
        search_type: str = "all"
    ):

        params = {
            "image_id": image_id,
            "type": search_type,
            "hl": "en",
            "country": "in"
        }

        return self._search(
            "google_lens",
            **params
        )
