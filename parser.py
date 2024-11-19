from bs4 import BeautifulSoup

from datetime import datetime

from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

import time
import random

import re

def main():

    print('Пример ссылки: https://plati.market/seller/darkawe/392951/#ss=price \n')

    while True:
        # Ввод ссылки на продавца на Plati Market
        url = input('Введите ссылку на продавца на Plati Market: ')

        # Если в переменную ссылки не было передано текста вообще
        # или переданна только неопределенная последовательность пробелов
        if not url or url.strip() == '':
            print('\nВнимание: Вы не передали ссылку продавца площадки Plati Market. В таком случае будет использована ссылка из примера')
            url = 'https://plati.market/seller/darkawe/392951/#ss=price'

        # Проверка, что ссылка ведет именно на сайт Plati Market
        if 'plati.market' not in url:
            print('Ошибка: Неверно указана ссылка сайта Plati Market\n')
            continue

        # Если отсутствует сортировка по цене (от меньшего к большему), добавляем сортировку
        if '#ss=price' not in url:
            url = url + '#ss=price' if url.endswith('/') else url + '/#ss=price'

        # Отступ для удобства в терминале
        print()

        break

    # Ввод минимальной цены товара
    while True:
        try:
            min_price = int(input('Введите минимальную сумму товара: '))
            break
        except ValueError as error:
            print('\nВнимание: Введенная информация не является числом\n')
            continue

    # Ввод максимальной цены товара
    while True:
        try:
            max_price = int(input('Введите максимальную сумму товара: '))
            break
        except ValueError as error:
            print('\nВнимание: Введенная информация не является числом\n')
            continue


    if min_price > max_price:
        min_price, max_price = max_price, min_price
        print('\nВнимание: Минимальное значение цены не может быть больше максимального. Значения были переназначены\n')


    # Время начала парсинга для отчета
    start_parsing_time = datetime.now().strftime("%H:%M:%S")

    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")

    # Ссылка на материал: https://stackoverflow.com/questions/7593611/selenium-testing-without-browser

    # Обозначаем Selenium, что не будем открывать браузер
    # options.add_argument('headless')

    # Создаем объект selenuim
    driver = webdriver.Edge(options=options)

    # Скрывает браузер
    driver.minimize_window()

    # Переходим на сайт
    driver.get(url)

    print('Загружена страница №1....')

    # Получаем объект select-option
    # Получаем полный перечень элементов с теггом product-price
    all_product_prices = driver.find_elements(By.CLASS_NAME, 'product-price')

    # Поскольку нас интересует выпадающий список из заголовка таблицы, то он будет первым элементом с индексом 0
    dropdown_price = all_product_prices[0].find_element(By.CLASS_NAME, 'select_dd')

    # Получаем Select-элемент
    dropdown_price_select = Select(dropdown_price)

    # Меняем значение цены на сайте на Российскую валючу
    dropdown_price_select.select_by_value('RUR')

    # Ждем некоторый промежуток времени, чтобы цены на странице поменялись
    # Ссылка на материал: https://stackoverflow.com/questions/6088077/how-to-get-a-random-number-between-a-float-range
    time.sleep(random.uniform(1.5, 3.0))

    # Переменная контента таблицы
    myContent = ''

    # Переменная контента html-страницы
    # html_content = ''

    # Текущая страница парсера
    current_page = 1

    # Переменная остановки парсера
    stop_parsing = False

    # Переменная, отслеживающая количество записей, выгруженных с Plati Market
    products_counter = 0

    # Получаем общую информацию для отчета на главной странице
    # Начало блока

    # Передаем html-код страницы в BeautifulSoup и создаем объект на основе полученных данных
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Получаем тело страницы
    body = soup.body

    # Имя продавца для отчета
    seller_name = body.find('div', {'class': 'content_center'}).h1.span.text

    # Общее количество таворов продавца
    total_products_count = body.find('div', {'class': 'merchant_products'}).span.text

    # Конец блока


    # for current_page in range(1, 6):
    while True:

        # Получаем html-код страницы
        html_page = driver.page_source

        # Передаем html-код страницы в BeautifulSoup и создаем объект на основе полученных данных
        soup = BeautifulSoup(html_page, 'html.parser')

        # Получаем тело страницы
        body = soup.body

        # print(f'Количество уникальных позиций продавца: {total_products_count}\n')

        # Название товара
        product_title = body.find_all('td', {'class': 'product-title'})

        # Цена товара (внутри этого div, находиться еще один div с ценой)
        product_price = body.find_all('div', {'class': 'product-price-inner'})

        product_rows_display_data = []

        # Заголовки таблицы
        display_data_headers = ["Название товара", "Ссылка", "Цена"]

        # Формируем массив данных (список):
        # 1 элемент -> [0] -> название товара
        # 2 элемент -> [1] -> ссылка на товар
        # 3 элемент -> [2] -> цена товара

        for naming_data, price_data in zip(product_title, product_price):
            a_tag = naming_data.find('a')

            extracted_price = int(re.findall(r'\d+', price_data.div.text)[0])

            if extracted_price >= min_price:

                if extracted_price <= max_price:
                    product_rows_display_data.append([a_tag.text, a_tag['href'], price_data.div.text])
                    products_counter += 1

                else:
                    stop_parsing = True
                    break


        with open('template.html', 'r') as file:
            html_content = file.read()
            html_content = html_content.replace('\n', '').replace('\t', '')

            for row in product_rows_display_data:
                # Проверка: Если цена товара больше либо равна 30 рублям, то отображаем товар в таблице
                # if int(re.findall(r'\d+', row[2])[0]) >= 25:

                myContent += f"""
                    <tr>
                        <td>{row[0]}</td>
                        <td><a href="https://plati.market{row[1]}" target="_blank" rel="noopener noreferrer"> https://plati.market{row[1]}</a></td>
                        <td>{row[2]}</td>
                    </tr>
                """

                # else:
                #     continue


        # Если максимальная цена превышена, то останавливаем парсер
        if stop_parsing:
            print('\nВыгрузка товаров в html-документ завершена успешно!')
            break

        # Блок перехода на следующую страницу

        # Скроллинг страницы необходим для проверки
        # Возможно для того чтобы действия на странице отображались корректно они должны быть в поле видимости
        # Как вариант можно загружать новую страницу, но тогда, возможно, придется прописывать выбор валюты по новой
        driver.execute_script("window.scrollTo(0, 700)")

        current_page += 1

        # Данный код отрабатывает корректно при скроллинге страницы
        pagination_wrapper = driver.find_element(By.CLASS_NAME, 'pages_nav')
        pagination_a = pagination_wrapper.find_element(By.LINK_TEXT, f'{current_page}')

        # Ошибка невозможности найти элемент возникает в связи с тем, что пагинация таблицы иногда не успевает прогрузиться
        # Есть смысл увеличить ожидание с диапозона [1.5; 2.5] секунд до [3.0, 4.0] если current_page > 15 или 20
        try:
            pagination_a.click()
            # Поменял ожидание с 2.5 до 5.0
            time.sleep(random.uniform(3.0, 5.0))

        except StaleElementReferenceException as error:
            print('Внимание: Возникла ошибка связанная с невозможностью найти элемент. Работы парсера будет продолжена через 5 секунд...')
            time.sleep(5)
            current_page -= 1
            pagination_a = pagination_wrapper.find_element(By.LINK_TEXT, f'{current_page}')
            pagination_a.click()
            print('Кнопка нажата... Ожидание 5 секунд')
            time.sleep(5)

        print(f'Загружена страница №{current_page}....')

        driver.execute_script("window.scrollTo(0, 0)")

        # Окончание блока перехода на следующую страницу

        
    html_content = html_content.replace('{headers}', '''
        <th>Название товара</th>
        <th>Ссылка</th>
        <th>Цена</th>
        ''')

    # Указываем заголовок отчета
    html_content = html_content.replace('{report_title}', 'Отчет-выгрузка с площадки Plati Market')

    # Указываем общее количество продуктов продавца в отчете
    html_content = html_content.replace('{all_products_count}', f'Общее количество товаров продавца: {total_products_count}')

    # Указываем количество выгруженных в отчет товаров продавца
    html_content = html_content.replace('{report_products_count}',
                                        f'Количество выгруженных в отчет товаров продавца: {products_counter}')

    # Указываем имя продавца в отчете
    html_content = html_content.replace('{sellers_name}', f'Продавец: <a href="{url}" target="_blank" rel="noopener noreferrer">{seller_name}</a>')

    # Указываем текущую дату в отчете
    html_content = html_content.replace('{report_date}', f'Дата выгрузки: {datetime.now().strftime("%d.%m.%Y")}')

    # Указываем время начала выгрузки в отчете
    html_content = html_content.replace('{report_start_time}',
                                        f'Время начала выгрузки: {start_parsing_time}')

    # Указываем время окончания выгрузки в отчете
    html_content = html_content.replace('{report_end_time}',
                                        f'Время окончания выгрузки: {datetime.now().strftime("%H:%M:%S")}')

    # Указываем диапозон цен товаров
    html_content = html_content.replace('{products_prices_range}',
                                        f'Диапазон цен: от {min_price} руб. до {max_price} руб.')

    # Заполняем таблицу
    html_content = html_content.replace('{content}', myContent)

    # Указываем Автора проекта
    html_content = html_content.replace('{CreatedByIgorVeshkin}', 'ПО формирования отчетов для площадки Plati Market создано Игорем Вешкиным (by IgorVeshkin)')

    with open(f'Reports_result_{seller_name}_{datetime.now().strftime("%d_%m_%Y--%H_%M")}.html', 'w', encoding="utf-8") as html_savefile:
        html_savefile.write(html_content)


if __name__ == '__main__':
    main()

