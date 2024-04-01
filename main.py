import pandas as pd

from process_data import plot_wells, process, welltests
from pull_data import pull_tags

# jps with gauges and online as of 4-1-24
all_jps = [
    "MPB-28",
    "MPB-30",
    "MPB-32",
    "MPB-35",
    "MPB-37",
    "MPB-39",
    "MPC-23",
    "MPE-19",
    "MPE-24",
    "MPE-31",
    "MPE-35",
    "MPE-37",
    "MPE-41",
    "MPE-42",
    "MPS-05",
    "MPS-17",
    "MPS-22",
    "MPS-45",
    "MPS-57",
    "MPG-16",
    "MPG-18",
    "MPH-19",
    "MPI-15",
    "MPI-17",
    "MPI-27",
    "MPI-29",
    "MPI-31",
    "MPI-33",
    "MPI-36",
    "MPI-40",
    "MPJ-27",
    "MPF-73",
    "MPF-107",
    "MPM-10",
    "MPM-12",
    "MPM-14",
    "MPM-16",
    "MPM-18",
    "MPM-20",
    "MPM-22",
    "MPM-24",
    "MPM-26",
    "MPM-28",
    "MPM-30",
    "MPM-32",
    "MPM-34",
    "MPM-43",
    "MPM-45",
    "MPM-60",
    "MPM-62",
    "MPM-64",
]

tract14 = [
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

f_and_l = [
    "MPF-01",
    "MPF-05",
    "MPF-06",
    "MPF-09",
    "MPF-14",
    "MPF-25",
    "MPF-29",
    "MPF-34",
    "MPF-37",
    "MPF-38",
    "MPF-45",
    "MPF-50",
    "MPF-53",
    "MPF-54",
    "MPF-57",
    "MPF-61",
    "MPF-62",
    "MPF-65",
    "MPF-66",
    "MPF-73",
    "MPF-78",
    "MPF-79",
    "MPF-81",
    "MPF-86",
    "MPF-93",
    "MPF-94",
    "MPF-96",
    "MPF-109",
    "MPF-116",
    "MPF-73",
    "MPF-107",
    "MPL-01",
    "MPL-02",
    "MPL-03",
    "MPL-04",
    "MPL-07",
    "MPL-11",
    "MPL-12",
    "MPL-13",
    "MPL-14",
    "MPL-25",
    "MPL-28",
    "MPL-29",
    "MPL-36",
    "MPL-39",
    "MPL-40",
    "MPL-41",
    "MPL-43",
    "MPL-46",
    "MPL-47",
    "MPL-54",
    "MPL-55",
    "MPL-56",
    "MPL-57",
    "MPL-60",
    "MPL-62",
    "MPL-06",
    "MPL-20",
]

well_list = all_jps

# pull scada data
# IF A TAG IS MISSING IT WILL ERROR OUT THE PROGRAM AND TAKE YOU 30 minutes to find out its a missing tag for a well
tag_dict = pull_tags.gen_tag_dict()
tag_list = pull_tags.get_tags(well_list, tag_dict)
raw_data = pull_tags.query_tag(tag_list)
raw_data.to_pickle("header_data.pkl")

# process scada
process.proc_scada(pkl_path="header_data.pkl", tag_dict=tag_dict)

test = pd.read_pickle("well_dataframes.pkl")

print(test)

# process tests
tests = welltests.process_tests("Well Test 3-22-24.csv")
tests.to_pickle("well_tests.pkl")

# plot
well_dfs = plot_wells.load_well_dataframes("well_dataframes.pkl")
tests = pd.read_pickle("well_tests.pkl")

plot_wells.plot_grid_BHP_WHP(well_dfs)

# plot_wells.plot_wells(well_dfs)
# coefficients_df = plot_wells.plot_bhp_vs_headerp(well_dfs)
# coefficients_df = plot_wells.plot_bhp_vs_headerpGRID(well_dfs)
# coefficients_df.to_csv("well_coefficients.csv", index=False)
# plot_wells.plot_liquid_rate(well_dfs, tests)
# plot_wells.plot_liquid_rate2(well_dfs, tests)
# plot_wells.plot_whp_vs_liquid(well_dfs, tests)

print("fin")
