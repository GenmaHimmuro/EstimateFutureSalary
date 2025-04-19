import requests
import pandas as pd
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


VACANCIES_PER_PAGE_ON_HH = 100
ID_MOSCOW_AREA_ON_HH = 1
COUNT_VACANCIES_ON_PAGE_SJ = 100
CITY_NAME_ON_SJ = 'Moscow'


def get_request_to_api_hh(lang: str) -> dict[str, list | int]:
    page = 0
    url = 'https://api.hh.ru/vacancies'
    all_vacancies_hh = {'items': [], 'found': 0}
    while True:
        payload = {
            'area': ID_MOSCOW_AREA_ON_HH,
            'text': f'Программист {lang}',
            'currency': 'RUR',
            'page': page,
            'per_page': VACANCIES_PER_PAGE_ON_HH,
        }
        response = requests.get(url, params=payload)
        response.raise_for_status()
        vacancies_hh = response.json()
        all_vacancies_hh['items'].extend(vacancies_hh.get('items', []))
        all_vacancies_hh['found'] = vacancies_hh.get('found', 0)
        max_pages_from_api_response = vacancies_hh.get('pages', 0)
        page += 1
        if page >= max_pages_from_api_response:
            break
    return all_vacancies_hh


def get_rub_salary_hh(vacancies_hh: list[dict[str | int]]) -> list[float | int]:
    salaries = []
    for salary_of_vacancies in vacancies_hh:
        salary = salary_of_vacancies.get('salary')
        salaries.append(salary)
    salary_expectations = []
    for predict_salary in salaries:
        if predict_salary:
            salary_expectations.append(
                get_middle_salary_expectations(predict_salary['from'],
                                               predict_salary['to']))
    return salary_expectations


def get_middle_salary_expectations(payment_from: str | int, payment_to: str | int) -> int | float:
    if payment_to and payment_from:
        middle_salary_expectations = ((payment_to + payment_from) / 2)
        return middle_salary_expectations
    elif payment_from:
        middle_salary_expectations = (payment_from * 1.2)
        return middle_salary_expectations
    elif payment_to:
        middle_salary_expectations = (payment_to * 0.8)
        return middle_salary_expectations


def get_request_to_api_super_job(lang: str) -> dict[str, list]:
    url = '	https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': os.getenv('superjob_token'),
    }
    page = 0
    all_vacancies_sj = {'objects': []}
    while True:
        payload = {
            "keyword": f"Программист {lang}",
            'town': CITY_NAME_ON_SJ,
            'page': page,
            'count': COUNT_VACANCIES_ON_PAGE_SJ
        }
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        vacancies_sj = response.json()
        all_vacancies_sj['objects'].extend(vacancies_sj.get('objects', []))
        all_vacancies_sj['total'] = vacancies_sj.get('total', 0)
        if not vacancies_sj["more"]:
            break
        page += 1
    return all_vacancies_sj


def get_rub_salary_sj(vacancies_sj: dict[str | int]) -> list[float | int]:
    salary_expectations = []
    for salary in vacancies_sj:
        if salary:
            salary_expectations.append(
                get_middle_salary_expectations(salary['payment_from'],
                                               salary['payment_to']))
    return salary_expectations


def get_stats_of_salary(lang: str, found_vacancies: list, salary_expectations: dict) -> list[str | float]:
    return [lang,
            found_vacancies,
            len(salary_expectations),
            round(pd.Series(salary_expectations).mean(), 1)]


def create_table_with_statistic(stats_of_salary: list, table_name: str, table_data: list) -> str:
    current_table_data = [row[:] for row in table_data]
    current_table_data.extend(stats_of_salary)
    table = AsciiTable(current_table_data, title=table_name)
    return table.table


def main():
    load_dotenv()
    langs = [
        'Python',
        'Java',
        'Javascript'
    ]
    table_data = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'],
    ]

    stats_of_salary_hh = []
    stats_of_salary_sj = []

    for lang in langs:

        all_vacanies_hh = get_request_to_api_hh(lang)['items']
        found_vacancies_hh = get_request_to_api_hh(lang)['found']
        all_vacancies_sj = get_request_to_api_super_job(lang)['objects']
        found_vacancies_sj = get_request_to_api_super_job(lang)['total']

        stats_of_salary_hh.extend(
            [get_stats_of_salary(lang, found_vacancies_hh,
                                 get_rub_salary_hh(all_vacanies_hh),)])
        stats_of_salary_sj.extend(
            [get_stats_of_salary(lang, found_vacancies_sj,
                                 get_rub_salary_sj(all_vacancies_sj))])

    print(create_table_with_statistic(stats_of_salary_hh,
                                      'HH MOSCOW', table_data))
    print(create_table_with_statistic(stats_of_salary_sj,
                                      'SJ MOSCOW', table_data))


if __name__ == "__main__":
    main()
