#!/usr/bin/env python
# coding: utf-8

import requests
from config import API_KEY


# Общие заголовки для запросов
HEADERS = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, lzma, sdch',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
}

def coords_to_address(x, y):
    """
    Преобразует координаты (широта, долгота) в адрес с использованием Яндекс.Геокодера.
    """
    geocoder_request = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={x},{y}&format=json"

    try:
        # Выполняем запрос
        response = requests.get(geocoder_request, headers=HEADERS)
        response.raise_for_status()  # Проверяем, что запрос успешен

        # Преобразуем ответ в JSON
        json_response = response.json()

        # Извлекаем первый топоним из ответа
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        return toponym_address

    except requests.exceptions.RequestException as e:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code if 'response' in locals() else "N/A", "(", str(e), ")")
        return None

def address_to_coords(address):
    """
    Преобразует адрес в координаты (широта, долгота) с использованием Яндекс.Геокодера.
    """
    geocoder_request = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json"

    try:
        # Выполняем запрос
        response = requests.get(geocoder_request, headers=HEADERS)
        response.raise_for_status()  # Проверяем, что запрос успешен

        # Преобразуем ответ в JSON
        json_response = response.json()

        # Извлекаем первый топоним из ответа
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coordinates = toponym["Point"]["pos"]
        return tuple(map(float, toponym_coordinates.split()))  # Возвращаем кортеж (широта, долгота)

    except requests.exceptions.RequestException as e:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code if 'response' in locals() else "N/A", "(", str(e), ")")
        return None

# Пример использования
if __name__ == "__main__":
    # Тест для coords_to_address
    address = coords_to_address(56.741076,58.030465)  # Координаты Красной площади
    print("Адрес:", address)

    # Тест для address_to_coords
    coordinates = address_to_coords("Посёлок Сылва, улица Корнеева 27")
    print("Координаты:", coordinates)