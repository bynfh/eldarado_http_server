import csv
import os


def GetDataFromCsv(Path="./sorted_recommends.csv", MaxRows=float("inf")) -> dict:
    """
    Get data from csv file
    Return dict. Example: {"sdf34Nds":"fdsf234m 0.9; sdfsrwer 0.6;"}
    Path it is path to file csv
    MsxRows it is how many rows from csv we get.
    """
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
