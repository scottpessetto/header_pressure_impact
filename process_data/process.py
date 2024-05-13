import pickle
from typing import Dict, List, Optional, Tuple

import pandas as pd


def proc_scada(raw_data, tag_dict: Dict[str, List[str]]) -> Dict[str, pd.DataFrame]:
    """
    Processes SCADA data from a pickle file, filters and pivots it based on tags from tag_dict,
    and saves the processed dataframes to a pickle file.

    Args:
        pkl_path (str): The file path to the pickle file containing raw SCADA data.
        tag_dict (Dict[str, Tuple[str, str, str]]): A dictionary mapping well names to tuples of tags
            (BHP tag, header pressure tag, WHP tag).

    Returns:
        None: This function does not return anything but saves the processed dataframes to 'well_dataframes.pkl'.
    """
    try:
        # raw_data = pd.read_pickle(pkl_path)
        data_copy = raw_data.copy()
        data_copy["datetime"] = pd.to_datetime(data_copy["datetime"])

        well_dataframes = {}

        for well_name, (bhp_tag, header_pressure_tag, whp_tag) in tag_dict.items():
            filtered_data = data_copy[data_copy["tag"].isin([bhp_tag, header_pressure_tag, whp_tag])]
            if not filtered_data.empty:
                pivoted_data = filtered_data.pivot(index="datetime", columns="tag", values="value")
                column_mapping = {bhp_tag: "BHP", header_pressure_tag: "HeaderP", whp_tag: "WHP"}
                pivoted_data.rename(columns=column_mapping, inplace=True)
                well_dataframes[well_name] = pivoted_data

        return well_dataframes
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
