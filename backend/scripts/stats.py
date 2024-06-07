import logging

#import requests
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
    parser.add_argument('-o', '--output', required=True, help='Destination JSON file.')
    parser.add_argument('-p', '--password', required=True, help='')
    parser.add_argument('-s', '--start-date', default='2000-01-01', help='Results will include this date.')
    parser.add_argument('-e', '--end-date', default='3000-01-0', help='Results will include this date.')
    parser.add_argument('-k', '--keypress-time', default='180', help='Time between keypress in seconds')
    parser.add_argument('-u', '--api-url', required=True, help='API URL.')
    parser.add_argument('-b', '--export-blocks', action='store_true', help='Export time blocks')
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


def format_date(raw_date):
    return datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")


def format_date_ms(raw_date):
    return datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S.%fZ")


def format_result_date(raw_date): 
    if len(raw_date) == 19: # sometimes we get 2023-11-16T15:54:12
        raw_date = raw_date + ".000000"
    return datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S.%f")


def format_time_tracking_url(url, start_time, end_time, user_id):
    start_time = urllib.parse.quote(start_time)
    end_time = urllib.parse.quote(end_time)
    url = url + '?' + 'from_time=' + start_time + '&to_time=' + end_time + '&user_id=' + user_id
    return url


def user_record_to_time(user_record):
    for key, value in user_record.items():
        if key != 'user_id':
            user_record[key] = seconds_to_formatted_hours(value)
    return user_record


def time_tracking_users(session, user, time_tracking_url, start_time, end_time):
    user_tracking_time_url = format_time_tracking_url(time_tracking_url, start_time, end_time, user['id'])
    user_time_tracking = query_api(user_tracking_time_url, session, None)
    
    user_record = {'user_id': user['id']}

    for record in user_time_tracking:
        time_spent = format_date(record['end_time']) - format_date(record['start_time'])
        if time_spent.days < 0:  # if negative just zero
            time_spent = timedelta()
        
        if record['task'] in user_record:
            user_record[record['task']] += time_spent.seconds
        else:
            user_record[record['task']] = time_spent.seconds

    return user_record_to_time(user_record)

def get_time_blocks(session, user, time_tracking_url, start_time, end_time):
    user_tracking_time_url = format_time_tracking_url(time_tracking_url, start_time, end_time, user['id'])
    user_time_tracking = query_api(user_tracking_time_url, session, None)

    time_blocks = {'user_name': user['username'], 'email': user['email'], 'user_id': user['id']}

    for record in user_time_tracking:
        if not record['task'] in time_blocks:
            time_blocks[record['task']] = []
        time_blocks[record['task']].append({
            'start': record['start_time'],
            'end': record['end_time'],
        })

    return time_blocks

def get_time_blocks_list(session, users, time_tracking_url, start_time, end_time):
    time_blocks_list = []
    for user in users:
        time_blocks = get_time_blocks(session, user, time_tracking_url, start_time+ 'T00:00:00', end_time+ 'T23:59:59')
        if len(time_blocks) == 2 and 'user_id' in time_blocks and 'user_name' in time_blocks and 'email' in time_blocks:
            continue
        time_blocks_list.append(time_blocks)
    return time_blocks_list


def time_task(data, start_time, end_time, keypress_time):
    time = float(0)
    all_timestamps = []

    for key, values in data.items():
        for entry in values:
            history = entry.get("history", [])
            timestamps = [record["timestamp"] for record in history]
            all_timestamps.extend(timestamps)

    previous_timestamp = format_result_date(start_time) # add start time
    
    all_timestamps.sort() # sort times

    for timestamp in all_timestamps:
        time_difference = format_date_ms(timestamp) - previous_timestamp
        if time_difference.total_seconds() <= keypress_time:
            time += time_difference.total_seconds() 
        previous_timestamp = format_date_ms(timestamp)
    
    end_difference = format_result_date(end_time) - previous_timestamp
    if end_difference.total_seconds() <= keypress_time:  # add end time
        time += end_difference.total_seconds()

    return time


def seconds_to_formatted_hours(seconds):
    return "{:.2f}".format(seconds / 3600)


def get_final_list(users, tasks, start_date, end_date, keypress_time, task_result_url, time_tracking_url, session):
    list = []

    for user in users:
        timed_data = {"full_name" : user["full_name"],
                      "email"     : user["email"]
                      }
        time_all_tasks = 0
        for task in tasks:
            data = {
                    "annotation_task_id": task["id"],
                    "from_date": start_date,
                    "to_date": end_date,
                    "user_id": user["id"]
                    }

            tasks_response = query_api(task_result_url, session, data)

            time_total = 0
            for item in tasks_response:
                task_timed = time_task(json.loads(item["result"]), item["start_time"], item["end_time"], keypress_time)
                time_total += task_timed
            timed_data[task["name"]] = seconds_to_formatted_hours(time_total)
            time_all_tasks += time_total
        
        timed_data["all_times"] = seconds_to_formatted_hours(time_all_tasks)
        user_record = time_tracking_users(session, user, time_tracking_url, start_date + 'T00:00:00', end_date + 'T23:59:59')
        merged_dir = timed_data.copy()
        merged_dir.update(user_record)
        list.append(merged_dir)

    return list
        
#def main():
#    args = parse_args()
#    keypress_time = int(args.keypress_time)
#
#    login_url = urljoin(args.api_url, 'token')
#    user_url = urljoin(args.api_url, 'user/')
#    task_url = urljoin(args.api_url, 'task/task')
#    task_result_url = urljoin(args.api_url, 'task/results')
#    time_tracking_url = urljoin(args.api_url, 'time_tracking/time_tracking')
#
#    session = requests.Session()
#
#    session = get_session(login_url, session, args.login, args.password)
#    
#    users = query_api(user_url, session, None)
#
#    tasks = query_api(task_url, session, None)
#    tasks = [item for item in tasks if item['active']]
#    
#    final_list = get_final_list(users, tasks, args.start_date, args.end_date, keypress_time, task_result_url, time_tracking_url, session)
#    field_names = []
#    field_names_dict = max(final_list, key=len)
#    for key in field_names_dict:
#        field_names.append(key)
#
#    with open(args.output + '.jsonl', 'w') as csvfile:
#        for item in final_list:
#            csvfile.write(json.dumps(item) + '\n')
#
#    with open(args.output + '.csv', 'w') as csvfile:
#        writer = csv.DictWriter(csvfile, fieldnames=field_names)
#        writer.writeheader() 
#        writer.writerows(final_list) 
#
#    if args.export_blocks:
#        time_blocks_list = get_time_blocks_list(session, users, time_tracking_url, args.start_date, args.end_date)
#        with open(args.output + '_time_blocks.jsonl', 'w') as jsonfile:
#            for item in time_blocks_list:
#                jsonfile.write(json.dumps(item) + '\n')
#    
#
#if __name__ == '__main__':
#    main()
#