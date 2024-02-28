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


def query_tag(tags):
    try:
        connection = sql.connect(
            server_hostname="dbc-42b811e2-2a82.cloud.databricks.com",
            http_path=os.getenv("DATABRICKS_http_path"),
            access_token=os.getenv("DATABRICKS_API_TOKEN"),
        )
        print(f"Starting query")
        cursor = connection.cursor()
        # Prepare the list of tags for the IN clause
        flat_tag_list = [tag for tags in tag_list.values() for tag in tags if tag is not None]
        tag_list_str = ", ".join(f"'{tag}'" for tag in flat_tag_list)

        query = f"""
        SELECT
        -- Convert the timestamp to an hour interval
        CAST(FLOOR(CAST(LocalTime AS BIGINT) / 3600) * 3600 AS TIMESTAMP) AS time_interval_start,
        tag,
        AVG(value) AS average_value
        FROM
        historian.ns.measurements
        where tag in ({tag_list_str})
        and LocalDate > '2024-2-10'
        GROUP BY
        time_interval_start,
        tag
        ORDER BY
        time_interval_start;
        """

        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        print(f"Query complete for well {tag_list_str}")
        col_names = ["datetime", "tag", "value"]
        raw = pd.DataFrame(result, columns=col_names)

    except Exception as e:
        print(e)
        print("Error querying tags")
    return raw


raw_data = query_tag(tag_list)
raw_data.to_pickle("header_data.pkl")

print(raw_data)
