#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests


def coords_to_address(x, y):
    geocoder_request = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={x},{y}&format=json"

    # Выполняем запрос.
    response = requests.get(geocoder_request,headers ={
'Connection': 'keep-alive',
'Cache-Control': 'max-age=0',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'DNT': '1',
'Accept-Encoding': 'gzip, deflate, lzma, sdch',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
})
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Печатаем извлечённые из ответа поля:
        return toponym_address
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")


def addess_to_coords(address):
    # geocoder_request = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={address}&format=json"
    # geocoder_request = f'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={address}&ll=58.051264, 56.597753&format=json'
    geocoder_request = f'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={address}&ll=58.051264, 56.597753&spn=3.552069,2.400552&format=json'

    # Выполняем запрос.
    response = requests.get(geocoder_request,headers ={
'Connection': 'keep-alive',
'Cache-Control': 'max-age=0',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'DNT': '1',
'Accept-Encoding': 'gzip, deflate, lzma, sdch',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
})
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Печатаем извлечённые из ответа поля:
        return toponym_coodrinates
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")

