import pandas as pd

from process_data import plot_wells, process, welltests
from pull_data import pull_tags

# well config stores list of wells to analyze
from well_config import all_jps, tract14

well_list = all_jps


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

plot_wells.plot_grid_BHP_HeaderP(well_dfs)

plot_wells.plot_grid_BHP_WHP(well_dfs)

# plot_wells.plot_wells(well_dfs)
# coefficients_df = plot_wells.plot_bhp_vs_headerp(well_dfs)
# coefficients_df = plot_wells.plot_bhp_vs_headerpGRID(well_dfs)
# coefficients_df.to_csv("well_coefficients.csv", index=False)
# plot_wells.plot_liquid_rate(well_dfs, tests)
# plot_wells.plot_liquid_rate2(well_dfs, tests)
# plot_wells.plot_whp_vs_liquid(well_dfs, tests)

print("fin")
