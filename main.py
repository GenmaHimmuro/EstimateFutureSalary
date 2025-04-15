import requests
import statistics
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


VACANCIES_PER_PAGE_ON_HH = 100
MAX_PAGES_ON_HH = 20
ID_MOSCOW_AREA_ON_HH = 1
VACANCIES_PER_PAGE_ON_SJ = 100
KEY_OF_CATALOG_SJ = 48
CITY_NAME_ON_SJ = 'Moscow'


def get_request_to_api_hh(lang):
    page = 0
    vacancies_filtered_by_lang_on_hh = []

    while page < MAX_PAGES_ON_HH:
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
        request_result_json = response.json()
        vacancies_filtered_by_lang_on_hh.append(request_result_json)
        page += 1

    return {
        lang: vacancies_filtered_by_lang_on_hh
    }


def get_predict_rub_salary_hh(lang):
    vacancies = get_request_to_api_hh(lang)[lang][0]['items']

    salaries = []
    for salary_of_vacancies in vacancies:
        salary = salary_of_vacancies.get('salary')
        salaries.append(salary)

    salary_expectations = []
    for predict in salaries:
        if predict:

            if predict['to'] and predict['from']:
                salary_expectations.append((predict['to'] + predict['from'])/2)

            elif predict['from']:
                salary_expectations.append(predict['from']*1.2)

            elif predict['to']:
                salary_expectations.append(predict['to']*0.8)

    return [lang, len(vacancies), len(salary_expectations), statistics.mean(salary_expectations)]


def get_request_to_api_super_job(lang):
    url = '	https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': os.getenv('superjob_token'),
    }
    vacancies_filtered_by_lang_on_sj = []
    payload = {
        "keyword": f"Программист {lang}",
        'town': CITY_NAME_ON_SJ,
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    request_result_json = response.json()
    vacancies_filtered_by_lang_on_sj.append(request_result_json)

    return {
        lang: vacancies_filtered_by_lang_on_sj
    }


def get_predict_rub_salary_for_superJob(lang):
    vacancies = get_request_to_api_super_job(lang)[lang][0]['objects']

    salary_expectations = []
    for vacancy in vacancies:

        payment_from = vacancy.get('payment_from')
        payment_to = vacancy.get('payment_to')

        if payment_from and payment_to:
            salary_expectations.append((payment_from+payment_to)/2)

        elif payment_from:
            salary_expectations.append(payment_from*1.2)

        elif payment_to:
            salary_expectations.append(payment_to*0.8)

    return [lang, len(vacancies), len(salary_expectations), statistics.mean(salary_expectations)]


def get_stats_of_salary(langs, salary_expectations, table_name, table_data):
    current_table_data = [row[:] for row in table_data]
    for lang in langs:
        current_table_data.extend([salary_expectations(lang)])
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
    get_stats_of_salary(langs, get_predict_rub_salary_for_superJob, 'SJ MOSCOW', table_data)
    get_stats_of_salary(langs, get_predict_rub_salary_hh, 'HH MOSCOW', table_data)


if __name__ == "__main__":
    main()
