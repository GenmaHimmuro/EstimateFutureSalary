import requests
import statistics
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


def request_to_api_hh(lang):
    page = 0
    results = []
    try:
        while page < 19:
            payload = {
                'area': '1',
                'text': f'Программист {lang}',
                'currency': 'RUR',
                'page': page,
                'per_page': 99
            }
            url = 'https://api.hh.ru/vacancies'
            response = requests.get(url, params=payload)
            response.raise_for_status()
            data = response.json()
            results.append(data)
            page += 1
            return {
                lang: results
            }
    except requests.exceptions.HTTPError:
        return {
            lang: results
        }


def predict_rub_salary_hh(lang):
    vacancies_list = request_to_api_hh(lang)[lang][0]['items']

    list_of_salary = []
    for list_all_vacancies in vacancies_list:
        salary = list_all_vacancies.get('salary')
        list_of_salary.append(salary)

    predicts_salary = []
    for predict in list_of_salary:
        if predict is not None:

            if predict['from'] is not None:
                predicts_salary.append(predict['from']*1.2)

            elif predict['to'] is not None:
                predicts_salary.append(predict['to']*0.8)

    return predicts_salary


def request_to_api_super_job(lang):
    url = '	https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': os.getenv('superjob_token'),
    }
    page = 0
    results = []
    while page < 19:
        payload = {
            "keyword": f"Программист {lang}",
            'town': 'Москва',
            'page':page,
            'count':99
        }
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        data = response.json()
        results.append(data)
        page += 1
    return {
        lang: results
    }


def predict_rub_salary_for_superJob(lang):
    vacancies_list_sj = request_to_api_super_job(lang)[lang][0]['objects']

    list_of_salary = []
    for list_all_vacancies in vacancies_list_sj:

        payment_from = list_all_vacancies.get('payment_from')
        payment_to = list_all_vacancies.get('payment_to')

        if payment_from != 0:
            list_of_salary.append(payment_from*1.2)

        elif payment_to != 0:
            list_of_salary.append(payment_to*0.8)

    return list_of_salary


def get_stats_of_salary_from_sj(langs, table_name):
    table_data = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'],
    ]
    for lang in langs:
        founds_vacancies_from_sj = request_to_api_super_job(lang)[lang][0]['objects']
        table_data.extend([
            [
                lang, len(founds_vacancies_from_sj),
                len(predict_rub_salary_for_superJob(lang)),
                statistics.mean(predict_rub_salary_for_superJob(lang))
             ],
        ])
    table = AsciiTable(table_data, title=table_name)
    return table.table


def get_stats_of_salary_from_hh(langs, table_name):
    table_data = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'],
    ]
    for lang in langs:
        founds_vacancies_from_hh = request_to_api_hh(lang)[lang][0]['found']
        table_data.extend([
            [
                            lang, founds_vacancies_from_hh,
                            len(predict_rub_salary_hh(lang)),
                            statistics.mean(predict_rub_salary_hh(lang))
            ]
        ])
    table = AsciiTable(table_data, title=table_name)
    return table.table


def main():
    load_dotenv()
    langs = [
        'Python',
        'Java',
        'Javascript'
    ]
    print(get_stats_of_salary_from_hh(langs, 'HH Moscow'))
    print(get_stats_of_salary_from_sj(langs, 'SuperJob Moscow'))


if __name__ == "__main__":
    main()
