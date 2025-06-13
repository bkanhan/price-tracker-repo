import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.message import EmailMessage

# --- CONFIG ---

ASINS = [
    "B0CPFWKGPZ",  # Lick Snack Chicken Treat Value Pack
    "B0CPFVHS7P"   # Lick Snack Salmon Treat Value Pack
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

BASE_URL = "https://www.amazon.com/dp/"

ALERT_EMAIL = "your.email@example.com"
EMAIL_PASSWORD = "your_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- FUNCTIONS ---

def get_prime_price(asin):
    url = f"{BASE_URL}{asin}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find Prime price container, ignoring subscribe & save, Amazon Fresh, etc.
    # This selector targets the main price span used for Prime offers
    price_span = soup.select_one("span.a-price[data-a-color='price'] span.a-offscreen")

    if price_span:
        price_text = price_span.text.strip()
        price = float(price_text.replace("$", "").replace(",", ""))
        return price
    else:
        return None

def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL
    msg["To"] = ALERT_EMAIL
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(ALERT_EMAIL, EMAIL_PASSWORD)
        smtp.send_message(msg)

def load_last_price(asin):
    filename = f"{asin}_last_price.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                return float(f.read().strip())
            except:
                return None
    return None

def save_last_price(asin, price):
    filename = f"{asin}_last_price.txt"
    with open(filename, "w") as f:
        f.write(str(price))

def main():
    for asin in ASINS:
        print(f"Checking ASIN: {asin}")
        current_price = get_prime_price(asin)
        if current_price is None:
            print(f"Could not find price for {asin}")
            continue

        last_price = load_last_price(asin)
        print(f"Current price: ${current_price}, Last price: {last_price}")

        if last_price is None:
            save_last_price(asin, current_price)
            print(f"Saved initial price for {asin}")
        elif current_price < last_price:
            print(f"Price dropped for {asin}! Sending email...")
            subject = f"Price Drop Alert for ASIN {asin}"
            body = f"The price for product {asin} dropped from ${last_price} to ${current_price}.\nCheck it here: {BASE_URL}{asin}"
            send_email(subject, body)
            save_last_price(asin, current_price)
        else:
            print(f"No price drop for {asin}.")

if __name__ == "__main__":
    main()
