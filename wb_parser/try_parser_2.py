import requests
import json
import os

from django.conf import settings

from wb_parser.models import Product


def parse_wildberries(query):
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

    url = "https://search.wb.ru/exactmatch/ru/common/v4/search"

    params = {
        "query": query,
        "resultset": "catalog",
        "limit": 30,
        "page": 1
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Ошибка запроса: {response.status_code}")
        return

    try:
        data = response.json()
        print(data)
        products = data.get("data", {}).get("products", [])

        if not products:
            print("Нет товаров по запросу.")
            return

        products_data = []

        for item in products:
            name = item.get("name", "Без названия")
            price = item.get("priceU", 0) / 100
            discounted_price = item.get("salePriceU", 0) / 100
            rating = item.get("reviewRating", 0)
            review_count = item.get("feedbacks", 0)

            # Запись в базу данных
            Product.objects.create(
                name=name,
                price=price,
                discounted_price=discounted_price,
                rating=rating,
                review_count=review_count
            )

            products_data.append({
                "name": name,
                "price": price,
                "discounted_price": discounted_price,
                "rating": rating,
                "review_count": review_count
            })

        # А также сохраняем в файл json
        output_path = os.path.join(settings.BASE_DIR, 'products.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=4)

        print(f"Сохранено {len(products_data)} товаров в файл 'products.json'")

    except Exception as e:
        print(f"Ошибка обработки JSON: {e}")
