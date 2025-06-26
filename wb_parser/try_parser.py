import requests
from bs4 import BeautifulSoup
import json
import os

from django.conf import settings

from wb_parser.models import Product

HTML_FILE = os.path.join(settings.BASE_DIR, "wildberries_page.html")


def download_html(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;"
                  "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.wildberries.ru/",
        "Connection": "keep-alive",
    }

    url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Ошибка загрузки страницы:", response.status_code)
        return

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"Страница для '{query}' сохранена в {HTML_FILE}")


def parse_html_from_file():
    if not os.path.exists(HTML_FILE):
        print("Файл с HTML не найден, сначала вызовите download_html(query)")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    product_cards = soup.select(".product-card__wrapper")

    if not product_cards:
        print("Не удалось найти карточки товаров.")
        return

    products_data = []

    for card in product_cards[:20]:
        try:
            name = card.select_one(".product-card__name").text.strip()
            price_text = card.select_one(".price__lower-price").text.strip().replace("₽", "").replace(" ", "")
            old_price_el = card.select_one(".price__higher-price")
            old_price = old_price_el.text.strip().replace("₽", "").replace(" ", "") if old_price_el else price_text

            review_el = card.select_one(".product-card__count")
            review_count = int(review_el.text.strip().split()[0]) if review_el else 0

            price = float(price_text)
            old_price = float(old_price)

            rating = 0.0  # Рейтинг здесь не парсим

            # Сохраняем в БД
            Product.objects.create(
                name=name,
                price=old_price,
                discounted_price=price,
                rating=rating,
                review_count=review_count
            )

            products_data.append({
                "name": name,
                "price": old_price,
                "discounted_price": price,
                "rating": rating,
                "review_count": review_count
            })
        except Exception as e:
            print(f"⚠Ошибка в карточке: {e}")
            continue

    json_path = os.path.join(settings.BASE_DIR, "products.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(products_data, f, ensure_ascii=False, indent=4)

    print(f"Сохранено {len(products_data)} товаров в БД и {json_path}")
