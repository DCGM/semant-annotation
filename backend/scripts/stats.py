import requests
import argparse
import json
import sys
from datetime import datetime, timedelta

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--login', default='xbalca11', help='Username.')
    parser.add_argument('-f', '--file', help='Destination JSON file.', required=True)
    parser.add_argument('-p', '--password', required=True, help='')
    parser.add_argument('-s', '--start-time', default='2000-01-01T00:00:00', help='Start time.')
    parser.add_argument('-e', '--end-time', default='3000-01-01T00:00:00', help='End time.')
    parser.add_argument('-k', '--keypress-time', default='120', help='Time between keypress in seconds')
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

def time_task(data, keypress_time):
    time = float(0)
    all_timestamps = []
    for key, values in data.items():
        for entry in values:
            history = entry.get("history", [])
            timestamps = [record["timestamp"] for record in history]
            all_timestamps.extend(timestamps)

    if all_timestamps:
        previous_timestamp = format_date_ms((all_timestamps[0]))
    
    for timestamp in all_timestamps:
        print(timestamp)
        time_difference = format_date_ms(timestamp) - previous_timestamp
        if time_difference.total_seconds() <= keypress_time:
            if time_difference.total_seconds() >= 0:
                time += time_difference.total_seconds() 
        previous_timestamp = format_date_ms(timestamp)
    
    print(time)
    return time

def seconds_to_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

def get_final_list(users, tasks, start_time, end_time, keypress_time, task_result_url, time_tracking_url, session):
    list = []

    if users is None:
        return list

    for user in users:
        timed_data = {"full_name" : user["full_name"],
                      "email"     : user["email"]
                      }
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
                task_timed = time_task(json.loads(item["result"]), keypress_time)
                time_total += task_timed
            timed_data[task["name"]] = seconds_to_time(time_total)
        
        user_record = time_tracking_users(session, user, time_tracking_url, start_time, end_time)
        merged_dir = timed_data.copy()
        merged_dir.update(user_record)
        list.append(merged_dir)

    return list
        

def main():
    login_url = 'http://pchradis2.fit.vutbr.cz:8000/api/token'
    user_url = 'http://pchradis2.fit.vutbr.cz:8000/api/user/'
    task_url = 'http://pchradis2.fit.vutbr.cz:8000/api/task/task'
    task_result_url = 'http://pchradis2.fit.vutbr.cz:8000/api/task/results'
    time_tracking_url = 'http://pchradis2.fit.vutbr.cz:8000/api/time_tracking/time_tracking'
    
    args = parse_args()
    file = args.file
    username = args.login
    password = args.password
    start_time = args.start_time
    end_time = args.end_time
    keypress_time = int(args.keypress_time)

    session = requests.Session()

    session = get_session(login_url, session, username, password)
    
    if session == None:
        print("Couldn't estabilish connection")
        sys.exit(1) 


    users = get_result(user_url, session, None)

    raw_tasks = get_result(task_url, session, None)
    tasks = filter_tasks(raw_tasks)
    
    final_list = get_final_list(users, tasks, start_time, end_time, keypress_time, task_result_url, time_tracking_url, session)

    with open(file, "w") as outfile:
        for user in final_list:
            json.dump(user, outfile)
            print("",file=outfile)

if __name__ == '__main__':
    main()