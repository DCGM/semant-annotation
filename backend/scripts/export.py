import logging

import requests
import argparse
import json
import sys
import csv
from datetime import datetime, timedelta
import urllib.parse
from urllib.parse import urljoin


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--login', required=True, help='Username.')
    parser.add_argument('-p', '--password', required=True, help='')
    parser.add_argument('-u', '--api-url', required=True, help='API URL.')
    return parser.parse_args()


def get_session(url, session, login, password):
    response = session.post(url, data={"username": login, "password": password})
    
    if response.status_code != 200:
        logging.error(f'Login failed.')
        raise Exception('Login failed.')

    return session


def query_api(url, session, data):
    if data is None:
        response = session.get(url)
    else:
        response = session.post(url, json=data)

    if response.status_code != 200:
        logging.error(f'Error while getting result from {url}. {response.status_code} {response.reason} {response.text}')
        raise Exception(f'Error while getting result from {url}. {response.status_code} {response.reason} {response.text}')

    return response.json()





def get_final_list( tasks, task_result_url, session):
    for task in tasks:
        data = {
                "annotation_task_id": task["id"],
                }

        tasks_response = query_api(task_result_url, session, data)

        with open(f'{task["name"]}.json', 'w') as file:
            json.dump(tasks_response, file)


def main():
    args = parse_args()

    login_url = urljoin(args.api_url, 'token')
    user_url = urljoin(args.api_url, 'user/')
    task_url = urljoin(args.api_url, 'task/task')
    task_result_url = urljoin(args.api_url, 'task/results')

    session = requests.Session()

    session = get_session(login_url, session, args.login, args.password)
    
    #users = query_api(user_url, session, None)

    tasks = query_api(task_url, session, None)

    get_final_list(tasks, task_result_url, session)


if __name__ == '__main__':
    main()
