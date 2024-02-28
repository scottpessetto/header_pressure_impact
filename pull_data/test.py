import multiprocessing
import os

import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

dict_path = r"pull_data\bhp_dict.csv"

df = pd.read_csv(dict_path)


tag_dict = dict(zip(df["wellname"], zip(df["bhp_tag"], df["headerP_tag"])))


well_list = [
    "MPG-02",
    "MPG-14",
    "MPG-16",
    "MPG-18",
    "MPH-08",
    "MPH-16",
    "MPH-18",
    "MPH-19",
    "MPI-06",
    "MPI-20",
    "MPI-38",
    "MPI-15",
    "MPI-17",
    "MPI-27",
    "MPI-29",
    "MPI-31",
    "MPI-33",
    "MPI-36",
    "MPI-40",
    "MPJ-06",
    "MPJ-10",
    "MPJ-28",
    "MPJ-29",
    "MPJ-27",
]


def get_tags(wells, dict):
    tags = {}
    for name in wells:
        # Check if the name is in the dictionary
        if name in dict:
            # Add the name and associated tags to the result dictionary
            tags[name] = dict[name]
        else:
            # If the name is not found, you can choose to add a None or an empty list, etc.
            tags[name] = None  # or [] if you prefer an empty list for not found names
    return tags


tag_list = get_tags(well_list, tag_dict)

print(tag_list)
