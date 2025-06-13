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

        # Try multiple known selectors
        selectors = [
            '#corePrice_feature_div .a-offscreen',
            '.a-price .a-offscreen',
        ]

        for selector in selectors:
            tag = soup.select_one(selector)
            if tag:
                price_text = tag.text.strip()
                if "Subscribe" in price_text:
                    continue  # skip subscribe prices
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
        json.dump(data, f, indent=2)

def main():
    last_prices = load_last_prices()
    current_prices = {}

    for asin, name in PRODUCTS.items():
        print(f"🔍 Checking ASIN: {asin} ({name})")
        price = get_amazon_price(asin)

        if price:
            print(f"✅ Current price for {name}: {price}")
            current_prices[asin] = price

            if asin in last_prices and last_prices[asin] != price:
                print(f"🔄 Price change for {name}!\n   Previous: {last_prices[asin]} → Now: {price}")
        else:
            print(f"❌ Could not find price for {asin} ({name})")

    save_last_prices(current_prices)

if __name__ == "__main__":
    main()
