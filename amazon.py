import requests
from bs4 import BeautifulSoup
import json
import os

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
                price_text = tag.text.strip()
                if "Subscribe" in price_text:
                    continue
                return price_text
    except Exception as e:
        print(f"⚠️ Error fetching {asin}: {e}")
    return None

def load_last_prices():
    if os.path.exists(LAST_PRICES_FILE):
        with open(LAST_PRICES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_prices(data):
    with open(LAST_PRICES_FILE, "w") as f:
        json.dump(data, f, in
