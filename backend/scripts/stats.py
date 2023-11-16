import requests
import argparse
import json
import sys
import csv
from datetime import datetime, timedelta

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--login', default='xbalca11', help='Username.')
    parser.add_argument('-f', '--file', help='Destination JSON file.', required=True)
    parser.add_argument('-p', '--password', required=True, help='')
    parser.add_argument('-s', '--start-time', default='2000-01-01T00:00:00', help='Start time.')
    parser.add_argument('-e', '--end-time', default='3000-01-01T00:00:00', help='End time.')
    parser.add_argument('-k', '--keypress-time', default='120', help='Time between keypress in seconds')
    parser.add_argument('-a', '--api-link', default='http://pchradis2.fit.vutbr.cz:8000/api/', help='API link')
    return parser.parse_args()

def get_session(url, session, login, password):
    response = session.post(url, data={"username": login , "password": password})
    
    if response.status_code != 200:
        session = None

    return session

def get_result(url, session, data):
    if data is None:
        response = session.get(url)
    else:
        response = session.post(url, json=data)
    result = None
    
    if response.status_code == 200:
        result = response.json()
    return result

# Filter active tasks with only id and name
def filter_tasks(raw_tasks):
    if raw_tasks is None:
        return []
    tasks = [{'id': item['id'], 'name': item['name']} for item in raw_tasks if item['active'] == True] 
    return tasks

def format_date(raw_date):
    return datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")

def format_date_ms(raw_date):
    return datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S.%fZ")

def format_result_date(raw_date): 
    if len(raw_date) == 19: # sometimes we get 2023-11-16T15:54:12
        raw_date = raw_date + ".000000"
    return datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S.%f")

def format_time_tracking_url(url, start_time, end_time, user_id):
    start_time = start_time.replace(':', '%3A')
    end_time = end_time.replace(':', '%3A')
    url = url + '?' + 'from_time=' + start_time + '&to_time=' + end_time + '&user_id=' + user_id
    return url

def user_record_to_time(user_record):
    for key, value in user_record.items():
        if key != 'user_id':
            user_record[key] = seconds_to_time(value)
    return user_record

def time_tracking_users(session, user, time_tracking_url, start_time, end_time):
    user_tracking_time_url = format_time_tracking_url(time_tracking_url, start_time, end_time, user['id'])
    user_time_tracking = get_result(user_tracking_time_url, session, None)
    
    user_record = {'user_id' : user['id']}

    for record in user_time_tracking:
        time_spent = format_date(record['end_time']) - format_date(record['start_time'])
        if time_spent.days < 0: # if negative just zero
            time_spent = timedelta()
        
        if record['task'] in user_record:
            user_record[record['task']] += time_spent.seconds
        else:
            user_record[record['task']] = time_spent.seconds

    return user_record_to_time(user_record)

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

def seconds_to_time(seconds):
    hours = seconds / 3600
    return "{:.2f}h".format(hours)

def get_final_list(users, tasks, start_time, end_time, keypress_time, task_result_url, time_tracking_url, session):
    list = []

    if users is None:
        return list

    for user in users:
        timed_data = {"full_name" : user["full_name"],
                      "email"     : user["email"]
                      }
        time_all_tasks = 0
        for task in tasks:
            data = {
                    "annotation_task_id": task["id"],
                    "from_date": start_time,
                    "to_date": end_time,
                    "user_id": user["id"]
                    }

            raw_tasks_result = get_result(task_result_url, session, data)

            if raw_tasks_result is None:
                timed_data[task["name"]] = seconds_to_time(0)
                break

            time_total = 0
            
            for item in raw_tasks_result:
                task_timed = time_task(json.loads(item["result"]), item["start_time"], item["end_time"], keypress_time)
                time_total += task_timed
            timed_data[task["name"]] = seconds_to_time(time_total)
            time_all_tasks += time_total
        
        timed_data["all_times"] = seconds_to_time(time_all_tasks)
        user_record = time_tracking_users(session, user, time_tracking_url, start_time, end_time)
        merged_dir = timed_data.copy()
        merged_dir.update(user_record)
        list.append(merged_dir)

    return list
        

def main():
    args = parse_args()
    file = args.file
    username = args.login
    password = args.password
    start_time = args.start_time
    end_time = args.end_time
    link = args.api_link
    keypress_time = int(args.keypress_time)

    login_url = link + 'token'
    user_url = link + 'user/'
    task_url = link + 'task/task'
    task_result_url = link + 'task/results'
    time_tracking_url = link + 'time_tracking/time_tracking'

    session = requests.Session()

    session = get_session(login_url, session, username, password)
    
    if session == None:
        print("Couldn't estabilish connection")
        sys.exit(1) 

    users = get_result(user_url, session, None)

    raw_tasks = get_result(task_url, session, None)
    tasks = filter_tasks(raw_tasks)
    
    final_list = get_final_list(users, tasks, start_time, end_time, keypress_time, task_result_url, time_tracking_url, session)

    field_names = []
    field_names_dict = max(final_list,key=len)
    for key in field_names_dict:
        field_names.append(key)

    with open(file, 'w') as csvfile: 
        writer = csv.DictWriter(csvfile, fieldnames = field_names) 
        writer.writeheader() 
        writer.writerows(final_list) 

if __name__ == '__main__':
    main()