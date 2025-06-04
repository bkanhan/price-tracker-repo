import os
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
import smtplib

EMAIL_ADDRESS = os.getenv("ALERT_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

PRODUCT_NAME = "Living Proof No Frizz Shampoo (8.0 oz)"
PRODUCT_URL = "https://www.ulta.com/p/no-frizz-shampoo-pimprod2050683?sku=2635227"
PROMO_KEYWORDS = [
    "buy one get one", "bogo", "50% off", "free gift", "promo code", "use code",
    "sale ends", "limited time offer", "buy 2 get 1 free", "special offer",
    "discount applied at checkout"
]

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

def send_email_notification(promotions):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Missing email credentials.")
        return
    msg = EmailMessage()
    msg['Subject'] = f"Promotion Alert: {PRODUCT_NAME}"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    promo_list = "\n".join(promotions)
    msg.set_content(f"The following promotions were found for {PRODUCT_NAME}:\n\n{promo_list}\n\nCheck it out here: {PRODUCT_URL}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def main():
    try:
        html_content = fetch_product_page(PRODUCT_URL)
        promotions = parse_promotions(html_content)
        if promotions:
            send_email_notification(promotions)
        else:
            print("No applicable promotions found.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
