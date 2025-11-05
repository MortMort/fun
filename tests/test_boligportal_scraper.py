"""Tests for the BoligPortal scraper utility."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, Optional

import unittest
from unittest import mock

import urllib.error

from projects.boligportal.boligportal_scraper import (
    BoligPortalScraper,
    Listing,
    SimpleHttpClient,
)


class FakeHttpClient(SimpleHttpClient):
    """HTTP client that returns predefined HTML payloads for testing."""

    def __init__(self, html: str):
        super().__init__()
        self.html = html
        self.last_url: Optional[str] = None
        self.last_params: Optional[Dict[str, Any]] = None

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:  # type: ignore[override]
        self.last_url = url
        self.last_params = params
        return self.html


def _build_sample_html(listing: Dict[str, Any]) -> str:
    payload = {"props": {"pageProps": {"searchResult": {"listings": [listing]}}}}
    return (
        "<html><head><script id=\"__NEXT_DATA__\" type=\"application/json\">"
        f"{json.dumps(payload)}"
        "</script></head><body></body></html>"
    )


class BoligPortalScraperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.listing_data = {
            "id": 123,
            "headline": "Bright two-room apartment",
            "permalink": "/en/rental-apartments/copenhagen/bright-two-room",
            "rent": 8500,
            "rooms": 2,
            "size": 72,
            "address": "Main Street 1",
            "city": "Copenhagen",
        }
        html = _build_sample_html(self.listing_data)
        self.http_client = FakeHttpClient(html)
        self.scraper = BoligPortalScraper(http_client=self.http_client)

    def test_search_returns_normalised_listing(self) -> None:
        listings = self.scraper.search(
            location="Copenhagen",
            rooms_min=1,
            rooms_max=3,
            rent_min=7000,
            rent_max=9000,
            limit=5,
        )

        self.assertEqual(self.http_client.last_url, "https://www.boligportal.dk/en/rental-apartments/copenhagen/")
        self.assertEqual(
            self.http_client.last_params,
            {
                "rooms_min": 1,
                "rooms_max": 3,
                "rent_min": 7000,
                "rent_max": 9000,
            },
        )

        self.assertEqual(len(listings), 1)
        listing = listings[0]
        self.assertIsInstance(listing, Listing)
        self.assertEqual(listing.title, self.listing_data["headline"])
        self.assertEqual(listing.url, "https://www.boligportal.dk/en/rental-apartments/copenhagen/bright-two-room")
        self.assertEqual(listing.rent, 8500)
        self.assertEqual(listing.rooms, 2)
        self.assertEqual(listing.size, 72)
        self.assertEqual(listing.address, "Main Street 1")
        self.assertEqual(listing.city, "Copenhagen")

    def test_listing_can_be_serialised(self) -> None:
        listing = Listing(
            title="Cozy studio",
            url="https://www.boligportal.dk/en/rental-apartments/copenhagen/cozy-studio",
            rent=6500,
            rooms=1.0,
            size=34.0,
            address="Side Street 5",
            city="Copenhagen",
        )

        self.assertEqual(listing.to_dict(), asdict(listing))


if __name__ == "__main__":  # pragma: no cover - test module
    unittest.main()


class SimpleHttpClientFallbackTests(unittest.TestCase):
    def test_curl_fallback_used_when_https_unsupported(self) -> None:
        fake_response = mock.Mock()
        fake_response.stdout = b"<html>payload</html>"
        fake_response.stderr = b""

        with mock.patch("projects.boligportal.boligportal_scraper.shutil.which", return_value="/usr/bin/curl"):
            client = SimpleHttpClient()

        error = urllib.error.URLError("unknown url type: https")
        with mock.patch(
            "projects.boligportal.boligportal_scraper.urllib.request.urlopen",
            side_effect=error,
        ):
            with mock.patch(
                "projects.boligportal.boligportal_scraper.subprocess.run",
                return_value=fake_response,
            ) as run_mock:
                body = client.get("https://example.com")

        run_mock.assert_called_once()
        self.assertEqual(body, "<html>payload</html>")

