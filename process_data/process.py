import pickle

import pandas as pd


def proc_scada(pkl_path, tag_dict):
    raw = pd.read_pickle(pkl_path)
    df2 = raw.copy()
    df2["datetime"] = pd.to_datetime(df2["datetime"])

    well_dfs = {}

    # Iterate over the tag_dict to filter df2 and create a dataframe for each well
    for well, (bhp_tag, headerP_tag, whp_tag) in tag_dict.items():
        # Filter df2 for the current well's BHP and header pressure tags
        well_df = df2[(df2["tag"] == bhp_tag) | (df2["tag"] == headerP_tag) | (df2["tag"] == whp_tag)]

        # If the resulting dataframe is not empty, add it to the well_dfs dictionary
        if not well_df.empty:
            well_df_pivoted = well_df.pivot(index="datetime", columns="tag", values="value")

            # Relabel the columns using the tag_dict
            column_mapping = {bhp_tag: "BHP", headerP_tag: "HeaderP", whp_tag: "WHP"}
            well_df_pivoted = well_df_pivoted.rename(columns=column_mapping)

            well_dfs[well] = well_df_pivoted

    with open("well_dataframes.pkl", "wb") as handle:
        pickle.dump(well_dfs, handle, protocol=pickle.HIGHEST_PROTOCOL)
