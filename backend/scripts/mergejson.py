import json
import csv
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True, help='Destination JSON file.')
    parser.add_argument('-ij', '--input-json-files', nargs='+', required=True, help='Input .json files')
    parser.add_argument('-is', '--input-stats-file', required=True, help='Input .json file from stats.py')
    parser.add_argument('--from-date', required=True, help='From date.')
    parser.add_argument('--to-date', required=True, help='To date.')
    return parser.parse_args()


def get_data_json(file_path, name):
    with open(file_path, 'r') as file:
        data = json.load(file)

    data_to_write = {}
    for key in data.keys():
        if not data[key]["email"]:
            if 'Krolop' in data[key]['name']:
                data[key]["email"] = "xkrolo00@vutbr.cz"
            elif 'MartinF' in data[key]['name']:
                data[key]["email"] = "martin.fajcik@vut.cz"
            elif 'xvasko16' in data[key]['name']:
                data[key]["email"] = "xvasko16@stud.fit.vutbr.cz"
            elif 'Kiss' in data[key]['name']:
                data[key]["email"] = "ikiss@fit.vutbr.cz"
            else:
                raise Exception(f'No email for {key}, {data[key]["name"]}')
        dict_to_write = {data[key]["email"] : {"full_name": key,
                         "email": data[key]["email"], 
                         name: round(data[key]["time_spent_thresholded_(h)"], 2)}}
        data_to_write.update(dict_to_write)
        
    return data_to_write 


def main():
    args = parse_args()

    data_dict = {}
    with open(args.input_stats_file, 'r') as file:
        for line in file:
            data = json.loads(line)
            data_dict[data["email"]] = data
            data_dict[data["email"]]['from_date'] = args.from_date
            data_dict[data["email"]]['to_date'] = args.to_date

    for file in args.input_json_files:
        file_key = file[:-27]
        data = get_data_json(file, file_key)
        for user in data.keys():
            if user not in data_dict:
                print(f'ERROR: unknown user {user}')
                continue
            data_dict[user].update(data[user])

    with open(args.output, 'w') as file:
        for user in data_dict.keys():
            file.write(json.dumps(data_dict[user]) + '\n')


if __name__ == '__main__':
    main()
