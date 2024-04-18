import pandas as pd

from process_data import bhp_vs_whp, calc_PI_RP, merge, plot_wells, process, welltests
from pull_data import pull_tags

# well config stores list of wells to analyze
from well_config import all_jps, tract14

well_list = tract14

"""
TODO
need to have a 5 second tag whp vs bhp

and then a day tag for well test vs bhp (is there an issue with only six hour tests?)
"""


# IF A TAG IS MISSING IT WILL ERROR OUT THE PROGRAM AND TAKE YOU 30 minutes to find out its a missing tag for a well
tag_dict = pull_tags.gen_tag_dict()
tag_list = pull_tags.get_tags(well_list, tag_dict)
raw_scada_data = pull_tags.query_tag_WT_average(tag_list, tag_dict)

# data for whp vs bhp
data_bhp_whp = pull_tags.query_tag(tag_list, "2024-4-15")
well_scada_data = process.proc_scada(data_bhp_whp, tag_dict=tag_dict)  # make this similar to wt average
coeffs = bhp_vs_whp.plot_bhp_vs_headerp(well_scada_data)
bhp_vs_whp.plot_grid_BHP_WHP(well_scada_data)
bhp_vs_whp.plot_grid_BHP_WHP_dailyFIT(well_scada_data)


# process tests
test_path = r"fdc_test_data\Well Test 1month 4-18-24.csv"
test_processor = welltests.FDCProcessor(test_path)
well_specific_tests = test_processor.get_welltests()
merged_test_data = merge.merge_data(well_list, raw_scada_data, well_specific_tests)
merged_test_data.to_csv(r"results\merged_tests.csv")
print(merged_test_data)


# estimate reservoir pressure for PI
rp_calc = calc_PI_RP.calc_optimal_RP(merged_test_data)
rp_calc.to_csv(r"results\res pressure.csv")


print(coeffs)
"""
# plot
well_dfs = plot_wells.load_well_dataframes("well_dataframes.pkl")
tests = pd.read_pickle("well_tests.pkl")

plot_wells.plot_grid_BHP_HeaderP(well_dfs)

# plot_wells.plot_grid_BHP_WHP(well_dfs)

for well, df in well_dfs.items():
    print(well)
    print(df)

print(tests)

# plot_wells.plot_wells(well_dfs)
# coefficients_df = plot_wells.plot_bhp_vs_headerp(well_dfs)
# coefficients_df = plot_wells.plot_bhp_vs_headerpGRID(well_dfs)
# coefficients_df.to_csv("well_coefficients.csv", index=False)
# plot_wells.plot_liquid_rate(well_dfs, tests)
# plot_wells.plot_liquid_rate2(well_dfs, tests)
# plot_wells.plot_whp_vs_liquid(well_dfs, tests)
"""
print("fin")
