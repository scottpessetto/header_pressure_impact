import multiprocessing
import os

import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()


def gen_tag_dict(dict_path=r"pull_data\bhp_dict.csv"):
    df = pd.read_csv(dict_path)
    tag_dict = dict(zip(df["wellname"], zip(df["bhp_tag"], df["headerP_tag"], df["whp_tag"])))
    return tag_dict


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


def query_tag(tags):
    tag_list = tags
    try:
        connection = sql.connect(
            server_hostname="dbc-42b811e2-2a82.cloud.databricks.com",
            http_path=os.getenv("DATABRICKS_http_path"),
            access_token=os.getenv("DATABRICKS_API_TOKEN"),
        )
        print("Starting query")
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
        and LocalDate > '2024-2-1'
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
