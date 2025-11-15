import requests
import json

API_KEY = ""
PAGE_SIZE = 10  # Количество результатов


def search_places(query):
    """
    Поиск мест по запросу
    """
    url = "https://catalog.api.2gis.com/3.0/items"

    params = {
        "q": query,  # что ищем
        "key": API_KEY,  # ключ
        "fields": "items.reviews,items.id,items.name,items.address",  # что хотим получить
        "page_size": PAGE_SIZE
    }

    try:
        print(f"🔍 Ищем: {query} ...")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверка на ошибки

        data = response.json()

        if data.get('result'):
            items = data['result'].get('items', [])
            print(f"✅ Найдено мест: {len(items)}")
            return items
        else:
            print("❌ Не удалось найти результаты")
            return []

    except requests.exceptions.RequestException as e:
        print(f"🚫 Ошибка запроса: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"🚫 Ошибка разбора JSON: {e}")
        return []


def display_results(places):
    """
    Выводим результаты
    """
    print("\n" + "=" * 50)
    print("НАЙДЕННЫЕ МЕСТА:")
    print("=" * 50)

    for i, place in enumerate(places, 1):
        print(f"\n{i}. {place.get('name', 'Нет названия')}")
        print(f"   🆔 ID: {place.get('id', 'Нет ID')}")
        print(f"   📍 Адрес: {place.get('address_name', 'Нет адреса')}")

        # Информация об отзывах
        reviews = place.get('reviews', {})
        if reviews:
            print(f"   ⭐ Рейтинг: {reviews.get('general_rating', 'Нет')}")
            print(f"   💬 Всего отзывов: {reviews.get('general_review_count_with_stars', 0)}")
        else:
            print(f"   💬 Отзывы: нет информации")

        print(f"   🔗 Подробнее: https://2gis.ru/firm/{place.get('id', '')}")


# Основная программа
if __name__ == "__main__":
    search_query = input("Запрос для поиска: ")

    # Выполняем поиск
    places = search_places(search_query)

    # Показываем результаты
    if places:
        display_results(places)

        # Собираем данные об отзывах для каждого места
        places_with_reviews = []
        for place in places:
            reviews = place.get('reviews', {})
            review_count = reviews.get('general_review_count_with_stars', 0)
            rating = reviews.get('general_rating', 0)

            # Если рейтинг есть, используем его, иначе ставим 0
            if rating and isinstance(rating, (int, float)):
                current_rating = float(rating)
            else:
                current_rating = 0.0

            places_with_reviews.append({
                'place': place,
                'review_count': review_count,
                'rating': current_rating
            })

        # Вычисляем среднее количество отзывов
        if places_with_reviews:
            total_reviews = sum(item['review_count'] for item in places_with_reviews)
            average_reviews = total_reviews / len(places_with_reviews)
            print(f"\n📊 Среднее количество отзывов: {average_reviews:.1f}")

            # Отфильтровываем места с количеством отзывов меньше среднего
            filtered_places = [item for item in places_with_reviews if item['review_count'] >= average_reviews]
            print(f"📈 После фильтрации осталось мест: {len(filtered_places)}")

            # Сортируем по рейтингу (по убыванию) и берём топ-3
            filtered_places.sort(key=lambda x: x['rating'], reverse=True)
            top_places = filtered_places[:3]

            # Выводим финальные результаты
            print("\n" + "=" * 50)
            print("ТОП-3 МЕСТА ПО РЕЙТИНГУ:")
            print("=" * 50)

            for i, item in enumerate(top_places, 1):
                place = item['place']
                print(f"\n{i}. {place.get('name', 'Нет названия')}")
                print(f"   📍 Адрес: {place.get('address_name', 'Нет адреса')}")
                print(f"   ⭐ Рейтинг: {item['rating']}")
                print(f"   💬 Отзывов: {item['review_count']}")
                print(f"   🔗 Подробнее: https://2gis.ru/firm/{place.get('id', '')}")
        else:
            print("❌ Нет данных для фильтрации")

        # Сохраняем в файл для дальнейшего использования
        with open('places.json', 'w', encoding='utf-8') as f:
            json.dump(places, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Результаты сохранены в файл: places.json")
    else:
        print("😞 Не удалось найти места. Проверь API-ключ и подключение к интернету.")
