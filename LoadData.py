import csv
import os


def GetDataFromCsv(Path="/media/oleg/MARKOV_32/Работа/Поиск работы 2020/sorted_recommends.csv", MaxRows=float("inf")):
    DataFromCsv = {}
    if not os.path.exists(Path):
        raise FileNotFoundError
    with open(Path, encoding='utf-8') as csv_file:
        csv_row_iterator = csv.reader(csv_file, delimiter=",")
        for index_row_csv, row_csv in enumerate(csv_row_iterator):
            if row_csv[0] not in DataFromCsv:
                DataFromCsv[row_csv[0]] = f'{row_csv[1]} {row_csv[2]};'
            else:
                DataFromCsv[row_csv[0]] += f' {row_csv[1]} {row_csv[2]};'
            if MaxRows < index_row_csv:
                break
    return DataFromCsv
