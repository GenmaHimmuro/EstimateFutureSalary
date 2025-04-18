import requests
import statistics
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


VACANCIES_PER_PAGE_ON_HH = 100
ID_MOSCOW_AREA_ON_HH = 1
COUNT_VACANCIES_ON_PAGE_SJ = 100
CITY_NAME_ON_SJ = 'Moscow'


def get_request_to_api_hh(lang: str) -> dict[str]:
    page = 0
    while True:
        payload = {
            'area': ID_MOSCOW_AREA_ON_HH,
            'text': f'Программист {lang}',
            'currency': 'RUR',
            'page': page,
            'per_page': VACANCIES_PER_PAGE_ON_HH
        }
        url = 'https://api.hh.ru/vacancies'
        response = requests.get(url, params=payload)
        response.raise_for_status()
        page += 1
        vacancies_hh = response.json()
        return vacancies_hh


def get_predict_rub_salary_hh(vacancies_hh: dict) -> list[float | int]:

    salaries = []
    for salary_of_vacancies in vacancies_hh:
        salary = salary_of_vacancies.get('salary')
        salaries.append(salary)
    salary_expectations = []
    for predict_salary in salaries:
        if predict_salary:
            salary_expectations.extend(
                get_middle_salary_expectations(
                                               predict_salary['from'],
                                               predict_salary['to']
                )
            )
    return salary_expectations


def get_middle_salary_expectations(payment_from: str | int, payment_to: str | int) -> list[float | int]:
    middle_salary_expectations = []
    if payment_to and payment_from:
        middle_salary_expectations.append((payment_to + payment_from) / 2)
    elif payment_from:
        middle_salary_expectations.append(payment_from * 1.2)
    elif payment_to:
        middle_salary_expectations.append(payment_to * 0.8)
    return middle_salary_expectations


def get_request_to_api_super_job(lang: str) -> dict[str]:
    url = '	https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': os.getenv('superjob_token'),
    }
    page = 0
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
        if vacancies_sj['objects']:
            break
        page += 1
    return vacancies_sj


def get_predict_rub_salary_sj(vacancies_sj: dict[str]) -> list[float | int]:
    salary_expectations = []
    for predict_salary in vacancies_sj:
        if predict_salary:
            salary_expectations.extend(
                get_middle_salary_expectations(
                                               predict_salary['payment_from'],
                                               predict_salary['payment_to']
                )
            )
    return salary_expectations


def get_stats_of_salary(lang: str, found_vacancies: str | int, salary_expectations: list[float | int]) -> list[str | float]:
    return [lang,
            found_vacancies,
            len(salary_expectations),
            statistics.mean(salary_expectations)]


def create_table_with_statistic(stats_of_salary: list, table_name: str, table_data: list) -> str:
    current_table_data = [row[:] for row in table_data]
    current_table_data.extend(stats_of_salary)
    table = AsciiTable(current_table_data, title=table_name)
    print(table.table)
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
        vacancies_hh = get_request_to_api_hh(lang)['items']
        vacancies_sj = get_request_to_api_super_job(lang)['objects']

        stats_of_salary_hh.extend(
            [get_stats_of_salary(lang,
                                 get_request_to_api_hh(lang)['found'],
                                 get_predict_rub_salary_hh(vacancies_hh),
                                 )]
        )
        stats_of_salary_sj.extend(
            [get_stats_of_salary(lang,
                                 get_request_to_api_super_job(lang)['total'],
                                 get_predict_rub_salary_sj(vacancies_sj))]
        )

    create_table_with_statistic(stats_of_salary_hh, 'HH MOSCOW', table_data)
    create_table_with_statistic(stats_of_salary_sj, 'SJ MOSCOW', table_data)


if __name__ == "__main__":
    main()
