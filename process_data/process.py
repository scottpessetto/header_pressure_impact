import pickle

import pandas as pd

raw = pd.read_pickle("header_data.pkl")


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
tag_dict = {well: tags for well, tags in tag_dict.items() if well in well_list}

df2 = raw.copy()
df2["datetime"] = pd.to_datetime(df2["datetime"])


well_dfs = {}

# Iterate over the tag_dict to filter df2 and create a dataframe for each well
for well, (bhp_tag, headerP_tag) in tag_dict.items():
    # Filter df2 for the current well's BHP and header pressure tags
    well_df = df2[(df2["tag"] == bhp_tag) | (df2["tag"] == headerP_tag)]

    # If the resulting dataframe is not empty, add it to the well_dfs dictionary
    if not well_df.empty:
        well_df_pivoted = well_df.pivot(index="datetime", columns="tag", values="value")

        # Relabel the columns using the tag_dict
        column_mapping = {bhp_tag: "BHP", headerP_tag: "HeaderP"}
        well_df_pivoted = well_df_pivoted.rename(columns=column_mapping)

        well_dfs[well] = well_df_pivoted

mpi_33 = well_dfs.get("MPI-33", None)
if mpi_33 is not None:
    print("sorted")
    print(mpi_33)
else:
    print("No data found for well ")


with open("well_dataframes.pkl", "wb") as handle:
    pickle.dump(well_dfs, handle, protocol=pickle.HIGHEST_PROTOCOL)
