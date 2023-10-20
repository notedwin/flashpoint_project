import pandas as pd
import duckdb
import os
from collections import Counter

CON = duckdb.connect("file.db")
FOLDER = "./books/"


def add_catalog():
    df = pd.read_csv("pg_catalog.csv")
    CON.sql(f"CREATE TABLE catalog AS SELECT * FROM df")


def check_table_exist(name):
    try:
        CON.execute(f"DESCRIBE {name};")
        return True

    except duckdb.duckdb.CatalogException:
        return False


def get_books():
    """
    First check if the folder with books exists, then for every directory
    open every file and use the file_name to create a table which has the word counts
    book_00258
    word | count
    the | 1000
    book | 5
    """

    if not os.path.exists(FOLDER):
        raise Exception("Folder does not exist.")

    for folder_num in range(521):
        folder_path = os.path.join(FOLDER, f"{folder_num:03d}/")

        files = os.listdir(folder_path)
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            file_num = file_path.split("/")[-1].split(".txt")[0]

            counts = counts = {"": 0}

            # if file is not empty, don't read it
            if not os.path.getsize(file_path) == 0:
                with open(file_path, "r") as f:
                    counts = Counter(f.read().split())

            count_df = pd.DataFrame.from_dict(counts, orient="index").reset_index()
            count_df.columns = ["word", "count"]
            CON.execute(f"CREATE TABLE book_{file_num} AS SELECT * FROM count_df")
            # print(f"done with book {file_num}")


if __name__ == "__main__":
    add_catalog()
    get_books()
