import pandas as pd

from process_data import plot_wells, process, welltests
from pull_data import pull_tags

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

# pull scada data
tag_dict = pull_tags.gen_tag_dict()
tag_list = pull_tags.get_tags(well_list, tag_dict)
raw_data = pull_tags.query_tag(tag_list)
raw_data.to_pickle("header_data.pkl")

# process scada
process.proc_scada(pkl_path="header_data.pkl", tag_dict=tag_dict)

# process tests
tests = welltests.process_tests("Well Test 2-29-24.csv")
tests.to_pickle("well_tests.pkl")

# plot
well_dfs = plot_wells.load_well_dataframes("well_dataframes.pkl")
tests = pd.read_pickle("well_tests.pkl")

plot_wells.plot_wells(well_dfs)
coefficients_df = plot_wells.plot_bhp_vs_headerp(well_dfs)
coefficients_df.to_csv("well_coefficients.csv", index=False)
plot_wells.plot_liquid_rate(well_dfs, tests)
plot_wells.plot_liquid_rate2(well_dfs, tests)
plot_wells.plot_whp_vs_liquid(well_dfs, tests)

print("fin")
