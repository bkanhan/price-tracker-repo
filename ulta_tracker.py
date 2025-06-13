import os
import re
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
import smtplib

EMAIL_ADDRESS = os.getenv("ALERT_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

PRODUCT_NAME = "Living Proof No Frizz Shampoo (8.0 oz)"
PRODUCT_URL = "https://www.ulta.com/p/no-frizz-shampoo-pimprod2050683?sku=2635227"
PROMO_KEYWORDS = [
    "buy one get one", "bogo", "50% off", "free gift", "promo code", "use code", "with code",
    "sale ends", "limited time offer", "buy 2 get 1 free",
    "discount applied at checkout"
]

PROMO_SEEN_FILE = "promo_seen.txt"
PRICE_FILE = "last_price.txt"

def fetch_product_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_promotions(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text().lower()
    found_promos = [keyword for keyword in PROMO_KEYWORDS if keyword in text]
    return found_promos

def parse_price(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Try to find price using common Ulta price classes or id (adjust if needed)
    # Prices usually like: $34.00
    price_text = None

    # Example attempt to find price span by class - this might change depending on the page HTML
    price_spans = soup.find_all('span', class_=re.compile('Price|price|product-price', re.I))
    for span in price_spans:
        text = span.get_text()
        if text and re.search(r'\$\d+(\.\d{2})?', text):
            price_text = text
            break

    if not price_text:
        # fallback: search whole page text for first $XX.XX pattern
        match = re.search(r'\$\d{1,3}(,\d{3})*(\.\d{2})?', soup.get_text())
        if match:
            price_text = match.group(0)

    if price_text:
        # Clean price string, remove $ and commas
        price_number = float(price_text.replace('$', '').replace(',', '').strip())
        return price_number
    else:
        raise ValueError("Price not found on page")

def read_last_price():
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE, 'r') as f:
            try:
                return float(f.read().strip())
            except:
                return None
    return None

def write_last_price(price):
    with open(PRICE_FILE, 'w') as f:
        f.write(str(price))

def read_promo_seen():
    return os.path.exists(PROMO_SEEN_FILE)

def write_promo_seen():
    with open(PROMO_SEEN_FILE, 'w') as f:
        f.write("seen")

def send_email_notification(subject, body):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Missing email credentials.")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def main():
    try:
        html_content = fetch_product_page(PRODUCT_URL)

        # Check promotions
        promotions = parse_promotions(html_content)
        promo_already_seen = read_promo_seen()

        # Check price
        current_price = parse_price(html_content)
        last_price = read_last_price()

        send_email = False
        email_subject = ""
        email_body = ""

        # Determine if promo notification is needed
        if promotions and not promo_already_seen:
            send_email = True
            email_subject = f"Promotion Alert: {PRODUCT_NAME}"
            promo_list = "\n".join(promotions)
            email_body += f"New promotions found for {PRODUCT_NAME}:\n\n{promo_list}\n\n"

        # Determine if price dropped
        if last_price is None:
            # First run - just save price, no email
            write_last_price(current_price)
        elif current_price < last_price:
            send_email = True
            email_subject = f"Price Drop Alert: {PRODUCT_NAME}"
            email_body += (f"The price dropped from ${last_price:.2f} to ${current_price:.2f}!\n\n")

            write_last_price(current_price)

        # If promo notification was sent, mark it as seen to avoid repeat emails
        if send_email and promotions:
            write_promo_seen()

        if send_email:
            email_body += f"Check it out here: {PRODUCT_URL}"
            send_email_notification(email_subject, email_body)
            print("Notification email sent.")
        else:
            print("No new promotions or price drops detected.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
