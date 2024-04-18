from typing import Dict, List

import pandas as pd


def merge_data(well_list: List[str], raw_tag_data: Dict[str, pd.DataFrame], well_tests: pd.DataFrame) -> pd.DataFrame:
    """
    Merges well test data with corresponding tag data for each well in the provided list.

    Args:
        well_list (List[str]): A list of well identifiers.
        raw_tag_data (Dict[str, pd.DataFrame]): A dictionary where keys are well identifiers and values are DataFrames containing tag data.
        well_tests (pd.DataFrame): A DataFrame containing well test data with columns including 'well' and 'WtDate'.

    Returns:
        pd.DataFrame: A DataFrame containing merged data from well tests and tag data based on the 'WtDate' and 'datetime' columns.

    Raises:
        KeyError: If the 'well' column is missing in well_tests or if well identifiers in well_list are not found in raw_tag_data or well_tests.
    """
    merged_data = pd.DataFrame()
    for well in well_list:
        filtered_tag_data = raw_tag_data[well]
        filtered_tests = well_tests[well_tests["well"] == well]

        # Localize the timezone-naive 'WtDate' column to UTC before removing timezone
        filtered_tests["WtDate"] = filtered_tests["WtDate"].dt.tz_localize("UTC").dt.tz_convert(None)

        # If the index of filtered_tag_data is timezone-aware, convert it to UTC and remove timezone
        if filtered_tag_data.index.tz:
            filtered_tag_data.index = filtered_tag_data.index.tz_convert("UTC").tz_localize(None)
        else:
            # If the index is timezone-naive, assume it is in UTC and remove timezone
            filtered_tag_data.index = filtered_tag_data.index.tz_localize("UTC").tz_localize(None)

        merged_well_data = pd.merge(
            filtered_tests, filtered_tag_data, left_on=["WtDate"], right_on=["datetime"], how="inner"
        )

        merged_data = pd.concat([merged_data, merged_well_data], ignore_index=True)

    return merged_data
