#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import quote
import time
import xlsxwriter

# === Ввод данных ===
vacancy = input('Укажите название вакансии: ').strip()
pages = int(input('Укажите кол-во страниц для парсинга: '))

# === Подготовка URL ===
encoded_vacancy = quote(vacancy)
base_url = f'https://hh.ru/search/vacancy?area=1&search_period=30&text={encoded_vacancy}&page='

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
}

jobs = []

def hh_parse(base_url, headers):
    global jobs
    for page in range(pages):
        print(f'Парсинг страницы {page + 1}/{pages}...')
        url = base_url + str(page)
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except Exception as e:
            print(f'Ошибка соединения на странице {page}: {e}')
            continue

        if response.status_code != 200:
            print(f'Страница {page} вернула статус {response.status_code}. Пропускаем.')
            continue

        soup = bs(response.content, 'html.parser')
        vacancy_blocks = soup.find_all('div', {'data-qa': 'vacancy-serp__vacancy'})

        for block in vacancy_blocks:
            # Ищем ссылку на вакансию — она должна содержать /vacancy/
            link_tag = block.find('a', href=lambda href: href and '/vacancy/' in href)
            if not link_tag:
                # Пропускаем блоки без ссылки на вакансию (реклама, "Компании для вас" и т.п.)
                continue

            title = link_tag.get_text(strip=True) or 'Не указано'
            href = link_tag['href']

            # Зарплата
            comp_tag = block.find(attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            compensation = comp_tag.get_text(strip=True) if comp_tag else 'None'

            # Компания
            company_tag = block.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
            company = company_tag.get_text(strip=True) if company_tag else 'None'

            # Описание
            resp = block.find('div', {'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'})
            req = block.find('div', {'data-qa': 'vacancy-serp__vacancy_snippet_requirement'})
            text1 = resp.get_text(strip=True) if resp else ''
            text2 = req.get_text(strip=True) if req else ''
            content = (text1 + ' ' + text2).strip()

            jobs.append([title, compensation, company, content, href])

        time.sleep(1)  # вежливая пауза

    # === Сохранение в Excel ===
    print(f'Собрано {len(jobs)} вакансий. Сохраняем в файл...')
    workbook = xlsxwriter.Workbook('Vacancy.xlsx')
    worksheet = workbook.add_worksheet()

    # Форматы
    bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
    center = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
    wrap = workbook.add_format({'text_wrap': True, 'valign': 'vcenter'})

    # Ширина колонок
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 40)
    worksheet.set_column('D:D', 135)
    worksheet.set_column('E:E', 45)

    # Заголовки
    worksheet.write('A1', 'Наименование', bold)
    worksheet.write('B1', 'Зарплата', bold)
    worksheet.write('C1', 'Компания', bold)
    worksheet.write('D1', 'Описание', bold)
    worksheet.write('E1', 'Ссылка', bold)

    # Данные
    for i, job in enumerate(jobs, start=1):
        row = i
        worksheet.write_string(row, 0, job[0], center)
        worksheet.write_string(row, 1, job[1], center)
        worksheet.write_string(row, 2, job[2], center)
        worksheet.write_string(row, 3, job[3], wrap)
        worksheet.write_url(row, 4, job[4])

    workbook.close()
    print('Файл "Vacancy.xlsx" успешно создан!')

# === Запуск ===

hh_parse(base_url, headers)