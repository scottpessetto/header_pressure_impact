import multiprocessing
import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()


def gen_tag_dict(dict_path: Path = Path("pull_data/pw_jetpump_tags.csv")) -> Dict[str, List[str]]:
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
        tag_dict = {row["Well"]: (row["BHG"], row["PF Pres"], row["PF Rate"]) for index, row in df.iterrows()}
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


def get_tags(wells: List[str], tag_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
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


def query_tag_list(
    tags: Dict[str, List[str]], tag_dict: Dict[str, List[str]], start_date: str
) -> Dict[str, pd.DataFrame]:
    """
    Queries and processes time-weighted average values for specified tags over six-hour intervals. The
    goal is to return the highest 6 hour average to best capture the likely test time for a give test.

    This function connects to a SQL database, executes a query to compute the maximum six-hour average
    values for each tag per day, and organizes the results into a DataFrame for each well.

    Args:
        tags (Dict[str, List[str]]): A dictionary where keys are well identifiers and values are lists of tag strings.
        tag_dict (Dict[str, Tuple[str, str, str]]): A dictionary mapping well identifiers to tuples of tag strings for BHP, header pressure, and WHP.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where keys are well identifiers and values are DataFrames with columns for BHP, header pressure, and WHP.

    Raises:
        Exception: If there is an error in executing the query or processing the data.
    """
    raw = None

    try:
        # Establish connection using Databricks SQL
        connection = sql.connect(
            server_hostname="dbc-42b811e2-2a82.cloud.databricks.com",
            http_path=os.getenv("DATABRICKS_http_path"),
            access_token=os.getenv("DATABRICKS_API_TOKEN"),
        )

        print("Starting query")
        cursor = connection.cursor()

        # Prepare the list of tags for the IN clause
        flat_tag_list = [tag for sublist in tags.values() for tag in sublist if tag is not None]
        tag_list_str = ", ".join(f"'{tag}'" for tag in flat_tag_list)

        query = f"""
        SELECT
        -- Convert the timestamp to an interval (300 is 5 min, 3600 is hour)
        CAST(FLOOR(CAST(LocalTime AS BIGINT) / 3600) * 3600 AS TIMESTAMP) AS time_interval_start,
        tag,
        AVG(value) AS average_value
        FROM
        historian.ns.measurements
        where tag in ({tag_list_str})
        and LocalDate > '{start_date}'
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

        print(f"Query complete for tags: {tag_list_str}")
        col_names = ["datetime", "tag", "value"]
        raw = pd.DataFrame(result, columns=col_names)
        raw["datetime"] = pd.to_datetime(raw["datetime"])

        well_dfs = {}

        # Process data for each well
        for well, (bhp_tag, PF_Pres_tag, PF_Rate_tag) in tag_dict.items():
            well_df = raw[raw["tag"].isin([bhp_tag, PF_Pres_tag, PF_Rate_tag])]
            if not well_df.empty:
                well_df_pivoted = well_df.pivot(index="datetime", columns="tag", values="value")
                column_mapping = {bhp_tag: "BHP", PF_Pres_tag: "PF_Pres", PF_Rate_tag: "PF_Rate"}
                well_df_pivoted = well_df_pivoted.rename(columns=column_mapping)
                well_dfs[well] = well_df_pivoted

    except Exception as e:
        print(e)
        print("Error querying tags")

    return well_dfs