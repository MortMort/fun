"""Utility for scraping boligportal.dk search results.

The module exposes a :class:`BoligPortalScraper` class that can be used from
Python code and also provides a small CLI wrapper for ad-hoc scraping.  The
scraper uses the server-rendered ``__NEXT_DATA__`` payload that the site
exposes, which keeps the implementation resilient to front-end changes and
means that JavaScript execution is not required.

Example
-------
Run the tool from the command line to retrieve listings as JSON::

    $ python boligportal_scraper.py --location Copenhagen --min-rooms 2 \
          --max-rooms 4 --max-rent 12000 --limit 5

"""
from __future__ import annotations

import argparse
import dataclasses
import html
import json
import logging
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Set

LOGGER = logging.getLogger(__name__)


@dataclass
class Listing:
    """A normalized representation of a listing on boligportal.dk."""

    title: str
    url: str
    rent: Optional[int]
    rooms: Optional[float]
    size: Optional[float]
    address: Optional[str]
    city: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the listing to a JSON-serializable dictionary."""

        return dataclasses.asdict(self)


class SimpleHttpClient:
    """Minimal HTTP GET client using :mod:`urllib`.

    ``urllib`` automatically honours standard proxy environment variables, so
    this client works in most restricted environments as well.
    """

    def __init__(self, user_agent: str = "Mozilla/5.0", timeout: float = 15.0):
        self._headers = {"User-Agent": user_agent}
        self._timeout = timeout

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Retrieve the specified URL and return its decoded body."""

        full_url = url
        if params:
            query = urllib.parse.urlencode(
                {key: value for key, value in params.items() if value is not None}
            )
            if query:
                full_url = f"{url}{'&' if '?' in url else '?'}{query}"
        request = urllib.request.Request(full_url, headers=self._headers)
        LOGGER.debug("Fetching %s", full_url)
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            body = response.read().decode(charset, errors="replace")
        return body


class BoligPortalScraper:
    """Scrape apartment listings from boligportal.dk."""

    BASE_URL = "https://www.boligportal.dk"
    SEARCH_PATH_TEMPLATE = "/en/rental-apartments/{location_slug}/"

    def __init__(self, http_client: Optional[SimpleHttpClient] = None):
        self._http = http_client or SimpleHttpClient()

    def search(
        self,
        *,
        location: str,
        rooms_min: Optional[float] = None,
        rooms_max: Optional[float] = None,
        rent_min: Optional[int] = None,
        rent_max: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Listing]:
        """Retrieve listings that match the supplied filters."""

        if not location:
            raise ValueError("'location' must be provided")
        slug = self._slugify(location)
        url = f"{self.BASE_URL}{self.SEARCH_PATH_TEMPLATE.format(location_slug=slug)}"
        params = {
            "rooms_min": rooms_min,
            "rooms_max": rooms_max,
            "rent_min": rent_min,
            "rent_max": rent_max,
        }
        try:
            html_payload = self._http.get(url, params=params)
        except urllib.error.URLError as exc:  # pragma: no cover - depends on network
            raise RuntimeError(f"Unable to fetch search page: {exc}") from exc
        next_data = self._extract_next_data(html_payload)
        raw_listings = self._find_listings(next_data)
        listings: List[Listing] = []
        for raw in raw_listings:
            listing = self._normalise_listing(raw)
            if listing is not None:
                listings.append(listing)
                if limit is not None and len(listings) >= limit:
                    break
        return listings

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
        slug = slug.strip("-")
        return slug or value.strip().lower()

    @staticmethod
    def _extract_next_data(html_payload: str) -> Dict[str, Any]:
        """Extract Next.js data payload from the provided HTML."""

        match = re.search(
            r"<script[^>]+id=\"__NEXT_DATA__\"[^>]*>(.*?)</script>",
            html_payload,
            re.DOTALL,
        )
        if not match:
            raise RuntimeError("Unable to locate Next.js data payload")
        json_blob = html.unescape(match.group(1))
        try:
            return json.loads(json_blob)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise RuntimeError("Malformed Next.js data payload") from exc

    def _find_listings(self, data: Any) -> List[Dict[str, Any]]:
        """Recursively locate potential listing dictionaries in the payload."""

        candidates: List[Dict[str, Any]] = []
        seen_ids: Set[Any] = set()

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                if self._looks_like_listing(node):
                    identifier = node.get("id") or node.get("rentalUnitId") or node.get(
                        "rental_unit_id"
                    )
                    if identifier is None or identifier not in seen_ids:
                        if identifier is not None:
                            seen_ids.add(identifier)
                        candidates.append(node)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(data)
        return candidates

    @staticmethod
    def _looks_like_listing(node: Dict[str, Any]) -> bool:
        key_set = set(node)
        title_keys = {"headline", "title", "name"}
        rent_keys = {"rent", "monthlyRent", "rental_price", "price"}
        url_keys = {"permalink", "relativeUrl", "url", "relativeLink"}
        address_keys = {"address", "street", "streetName"}
        has_title = any(key in key_set for key in title_keys)
        has_rent = any(key in key_set for key in rent_keys)
        has_url = any(key in key_set for key in url_keys)
        has_address = any(key in key_set for key in address_keys)
        return (has_title or has_address) and has_rent and has_url

    def _normalise_listing(self, raw: Dict[str, Any]) -> Optional[Listing]:
        title = self._first_value(
            raw,
            [
                ["headline"],
                ["title"],
                ["name"],
                ["seo", "title"],
                ["property", "headline"],
            ],
        )
        url = self._first_value(
            raw,
            [
                ["permalink"],
                ["relativeUrl"],
                ["url"],
                ["relativeLink"],
                ["links", "self"],
            ],
        )
        if not title or not url:
            return None
        rent = self._parse_price(
            self._first_value(
                raw,
                [
                    ["rent"],
                    ["monthlyRent"],
                    ["price", "rent"],
                    ["rental_price", "total"],
                    ["rentAmount"],
                ],
            )
        )
        rooms = self._parse_float(
            self._first_value(
                raw,
                [
                    ["rooms"],
                    ["numberOfRooms"],
                    ["roomsNumber"],
                    ["property", "rooms"],
                ],
            )
        )
        size = self._parse_float(
            self._first_value(
                raw,
                [
                    ["size"],
                    ["floorArea"],
                    ["space"],
                    ["sqm"],
                    ["property", "size"],
                ],
            )
        )
        address = self._first_value(
            raw,
            [
                ["address"],
                ["street"],
                ["streetName"],
                ["location", "address"],
                ["property", "address"],
            ],
        )
        city = self._first_value(
            raw,
            [
                ["city"],
                ["location", "city"],
                ["property", "city"],
            ],
        )
        absolute_url = url if url.startswith("http") else urllib.parse.urljoin(self.BASE_URL, url)
        return Listing(title=title, url=absolute_url, rent=rent, rooms=rooms, size=size, address=address, city=city)

    @staticmethod
    def _first_value(data: Dict[str, Any], paths: Sequence[Sequence[str]]) -> Optional[Any]:
        for path in paths:
            node: Any = data
            for segment in path:
                if isinstance(node, dict) and segment in node:
                    node = node[segment]
                else:
                    break
            else:
                if node is not None:
                    return node
        return None

    @staticmethod
    def _parse_price(value: Any) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            digits = re.findall(r"\d+", value.replace(".", ""))
            if not digits:
                return None
            return int(digits[0])
        if isinstance(value, dict):
            for key in ("value", "amount", "total"):
                if key in value and value[key] is not None:
                    return BoligPortalScraper._parse_price(value[key])
        return None

    @staticmethod
    def _parse_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.replace(",", "."))
            except ValueError:
                return None
        return None


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape boligportal.dk listings")
    parser.add_argument("--location", required=True, help="Name of the city or area to search")
    parser.add_argument("--min-rooms", type=float, default=None, help="Minimum number of rooms")
    parser.add_argument("--max-rooms", type=float, default=None, help="Maximum number of rooms")
    parser.add_argument("--min-rent", type=int, default=None, help="Minimum monthly rent (DKK)")
    parser.add_argument("--max-rent", type=int, default=None, help="Maximum monthly rent (DKK)")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of returned listings")
    parser.add_argument(
        "--debug", action="store_true", help="Enable verbose logging for troubleshooting"
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    scraper = BoligPortalScraper()
    try:
        listings = scraper.search(
            location=args.location,
            rooms_min=args.min_rooms,
            rooms_max=args.max_rooms,
            rent_min=args.min_rent,
            rent_max=args.max_rent,
            limit=args.limit,
        )
    except RuntimeError as exc:
        LOGGER.error("%s", exc)
        return 1
    json.dump([listing.to_dict() for listing in listings], sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
