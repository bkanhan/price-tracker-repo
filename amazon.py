import requests
from bs4 import BeautifulSoup
import json
import os
import sys

ASINS = {
    "B0CPFWKGPZ": "Lick Snack Chicken Treat",
    "B0CPFVHS7P": "Lick Snack Salmon Treat"
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

LAST_PRICES_FILE = "last_prices.json"

def get_amazon_price(asin):
    url = f"https://www.amazon.com/dp/{asin}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Try multiple selectors in order
        selectors = [
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "#price_inside_buybox",
            ".a-price .a-offscreen"
        ]
        for selector in selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                return price_elem.text.strip()

        print(f"❌ Could not find price on page for ASIN: {asin}")
        return None

    except requests.RequestException as e:
        print(f"❌ Network error while fetching ASIN {asin}: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error for ASIN {asin}: {e}")
        return None

def load_last_prices():
    if os.path.exists(LAST_PRICES_FILE):
        try:
            with open(LAST_PRICES_FILE, "r") as file:
                return json.load(file)
        except Exception as
