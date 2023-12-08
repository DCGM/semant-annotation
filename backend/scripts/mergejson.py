import json
import csv
import argparse

# python3 mergejson.py -o out.json -ij statistics/obrazky_2023-11-13_2023-11-19.json statistics/obliceje_data_2023-01-01_2023-11-20.json -is statistics/stats.jsonl -ic statistics/start-11-21-23.csv

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True, help='Destination JSON file.')
    parser.add_argument('-ij', '--input-json-files', nargs='+', required=True, help='Input .json files')
    parser.add_argument('-ic', '--input-csv-file', required=True, help='Input .csv file')
    parser.add_argument('-is', '--input-stats-file', required=True, help='Input .json file from stats.py')
    return parser.parse_args()


def get_data_json(file_path, name):
    with open(file_path, 'r') as file:
        data = json.load(file)

    data_to_write = {}
    for key in data.keys():
        dict_to_write = {data[key]["email"] : {"full_name": key,
                         "email": data[key]["email"], 
                         name: round(data[key]["time_spent_thresholded_(h)"], 2)}}
        data_to_write.update(dict_to_write)
        
    return data_to_write


def get_data_cvs(file_path, name):
    data_to_write = {}
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)

        for user in csv_reader:
            data_to_write[user["email"]] = {name: round(float(user["time_spent_(h)"]), 2)}
    
    return data_to_write
    

def main():
    args = parse_args()

    data_dict = {}
    with open(args.input_stats_file, 'r') as file:
        for line in file:
            data = json.loads(line)
            data_dict[data["email"]] = data


    for file in args.input_json_files:
        data = get_data_json(file, file[:-5])
        for user in data.keys():
            data_dict[user].update(data[user])

    data = get_data_cvs(args.input_csv_file, args.input_csv_file[:-4])
    for user in data:
        data_dict[user].update(data[user])

    with open(args.output, 'w') as file:
        for user in data_dict.keys():
            file.write(json.dumps(data_dict[user]) + '\n')


if __name__ == '__main__':
    main()