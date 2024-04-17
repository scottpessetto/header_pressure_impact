import multiprocessing
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()


def gen_tag_dict(dict_path: Path = Path("pull_data/bhp_dict.csv")) -> Dict[str, Tuple[str, str, str]]:
    """
    Generates a dictionary mapping well names to their respective SCADA tags.

    This function reads a CSV file containing well names and their corresponding SCADA tags
    for BHP (Bottom Hole Pressure), header pressure, and WHP (Wellhead Pressure). It returns
    a dictionary where each key is a well name and the value is a tuple of the associated tags.

    Args:
        dict_path (Path): The file path to the CSV file containing the tag data.
                         Defaults to "pull_data/bhp_dict.csv".

    Returns:
        Dict[str, Tuple[str, str, str]]: A dictionary where keys are well names and values are tuples
                                         containing the BHP tag, header pressure tag, and WHP tag.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        pd.errors.EmptyDataError: If the CSV file is empty.
        pd.errors.ParserError: If there is an issue parsing the CSV file.
    """
    try:
        df = pd.read_csv(dict_path)
        tag_dict = {
            row["wellname"]: (row["bhp_tag"], row["headerP_tag"], row["whp_tag"]) for index, row in df.iterrows()
        }
        return tag_dict
    except FileNotFoundError:
        print(f"Error: The file {dict_path} does not exist.")
        raise
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        raise
    except pd.errors.ParserError:
        print("Error: There was an issue parsing the CSV file.")
        raise


def get_tags(wells: List[str], tag_dict: Dict[str, List[str]]) -> Dict[str, Optional[List[str]]]:
    """
    Retrieves tags for specified wells from a given dictionary.

    Args:
        wells (List[str]): A list of well names for which tags are to be retrieved.
        tag_dict (Dict[str, List[str]]): A dictionary where keys are well names and values are lists of tags associated with each well.

    Returns:
        Dict[str, Optional[List[str]]]: A dictionary with well names as keys and a list of tags or None as values.
    """
    tags = {}
    for name in wells:
        # Check if the name is in the dictionary
        if name in tag_dict:
            # Add the name and associated tags to the result dictionary
            tags[name] = tag_dict[name]
        else:
            # If the name is not found, you can choose to add a None or an empty list, etc.
            tags[name] = None  # or [] if you prefer an empty list for not found names
    return tags


def query_tag(tags: Dict[str, List[str]]) -> Optional[pd.DataFrame]:
    """
    Executes a SQL query to retrieve average values of specified tags over time intervals from a historian database.

    This function connects to a SQL database using credentials from environment variables, constructs a SQL query
    to fetch the average values of specified tags that are grouped by hourly intervals, and returns the results
    as a pandas DataFrame.

    Args:
        tags (Dict[str, List[str]]): A dictionary where keys are tag categories and values are lists of tag strings.

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing the time intervals, tags, and their average values.
                                Returns None if the query fails or if an exception is raised.

    Raises:
        Exception: Outputs an error message to the console if the database connection fails or if the query execution
                   encounters an error.

    """

    tag_list = tags
    raw = None
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
        and LocalDate > '2024-3-1'
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
