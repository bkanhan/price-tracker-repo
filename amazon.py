import requests
from bs4 import BeautifulSoup
import json
import os

ASINS = {
    "B0CPFWKGPZ": "Lick Snack Chicken Treat",
    "B0CPFVHS7P": "Lick Snack Salmon Treat"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

LAST_PRICES_FILE = "last_prices.json"

def get_amazon_price(asin):
    url = f"https://www.amazon.com/dp/{asin}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch page for ASIN {asin}, status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Try to find the prime price element
    # Amazon page HTML changes frequently; this targets typical Prime price spans
    price = None
    selectors = [
        '#priceblock_ourprice',
        '#priceblock_dealprice',
        '#priceblock_saleprice',
        'span.a-price.a-text-price.a-size-medium',  # Sometimes prime price is here
        'span.a-price > span.a-offscreen'  # Generic price span
    ]
    
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag and tag.text.strip():
            price_text = tag.text.strip()
            if price_text.startswith("$"):
                price = price_text
                break

    # Additional filters could be added here if you want to exclude subscribe & save or others,
    # but often those are not in these selectors for the ASIN page itself.

    return price

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
    updated_prices = {}

    for asin, name in ASINS.items():
        print(f"🔍 Checking ASIN: {asin} ({name})")
        price = get_amazon_price(asin)

        if price:
            print(f"✅ Found price for {asin} ({name}): {price}")
            old_price = last_prices.get(asin)
            if old_price != price:
                print(f"⚠️ Price changed for {asin}: {old_price} -> {price}")
            else:
                print(f"ℹ️ Price unchanged for {asin}")
            updated_prices[asin] = price
        else:
            print(f"❌ Could not find price for {asin} ({name})")
            # Keep old price if exists
            if asin in last_prices:
                updated_prices[asin] = last_prices[asin]

    save_last_prices(updated_prices)

if __name__ == "__main__":
    main()
