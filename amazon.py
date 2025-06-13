import requests
from bs4 import BeautifulSoup
import json
import os
import re

PRODUCTS = {
    "B0CPFWKGPZ": "Lick Snack Chicken Treat",
    "B0CPFVHS7P": "Lick Snack Salmon Treat"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

LAST_PRICES_FILE = "last_prices.json"

def get_amazon_price(asin):
    url = f"https://www.amazon.com/dp/{asin}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # Look for price blocks in known Amazon patterns
        selectors = [
            '#corePrice_feature_div .a-offscreen',  # Regular price
            '.a-price .a-offscreen',                # Alternate location
            '#snsBasePrice .a-offscreen',           # Subscribe & Save (we will skip this)
        ]

        for selector in selectors:
            tag = soup.select_one(selector)
            if tag:
