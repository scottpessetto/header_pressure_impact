import pandas as pd

from process_data import (
    bhp_liq,
    bhp_pf,
    bhp_vs_whp,
    calc_PI_RP,
    coeffs_process,
    merge,
    pf_oil_benefit,
    pf_press_rate,
    plot_jp,
    plot_wells,
    process,
    welltests,
)
from pull_data import jp_data, pull_tags

# well config stores list of wells to analyze
from well_config import B_pad_JPs

well_list = B_pad_JPs

# Specify max allowable reservoir pressure
max_rp = 1800

### Generate JP data ###
# this does any tag in the pw_jetpump_tags.csv need to make it look at the list eventually
tag_dict = jp_data.gen_tag_dict()
tag_list = jp_data.get_tags(well_list, tag_dict)
raw_scada_data = jp_data.query_tag_list(tag_list, tag_dict, start_date="2024-4-1")


# plot the data and calculate BHP/PF coefficients
bhp_pf.plot_grid_bhp_vs_pf_pres(raw_scada_data)
pf_bhp_coeffs = bhp_pf.plot_grid_BHP_PF_Pres_DailyFit(raw_scada_data, filename="plots/BHP_PF_daily_fit_5-23-24")
pf_bhp_coeffs.to_csv(r"results/daily_bhp_pf_RAW_coeffs.csv")
processed_pf_bhp_coeffs = coeffs_process.process_coefficients(pf_bhp_coeffs)
processed_pf_bhp_coeffs.to_csv(r"results/daily_bhp_pf_coeffs.csv")

# calculate IPR for each well
# process tests
test_path = r"fdc_test_data\Well Test 5-23-24.csv"
test_processor = welltests.FDCProcessor(test_path)
well_specific_tests = test_processor.get_welltests()
merged_test_data = merge.merge_data(well_list, raw_scada_data, well_specific_tests)
merged_test_data.to_csv(r"results\B_Pad_merged_tests.csv")
print(merged_test_data)


# estimate reservoir pressure for PI
rp_calc = calc_PI_RP.calc_optimal_RP(merged_test_data, max_pres=max_rp)
rp_calc.to_csv(r"results\B-pad res pressure.csv")

# plot liquid rate vs bhp
vogel_coeffs = bhp_liq.plot_bhp_liquidrate(merged_test_data, rp_calc)

test_coeffs, test_ipr_data = bhp_liq.plot_bhp_liquidrate_r2(
    rp_calc, resp_modifier=150, filename="plots/B-pad IPRs 5-23-24.png"
)
test_coeffs.to_csv(r"results\B-pad vogel_coeffs_test.csv")
test_ipr_data.to_csv(r"results\B-pad ipr_data.csv")

vogel_coeffs.to_csv(r"results\B-pad vogel_coeffs.csv")


# create lookup tables of rates
bhp_lookup_table = pf_press_rate.bhp_lookup(processed_pf_bhp_coeffs)

liq_lookup_table = pf_press_rate.assign_liquid_rate(test_ipr_data, bhp_lookup_table)

liq_lookup_table.to_csv(r"results\PF_bhp_lookup_table.csv")

# Now assign watercut and calculate associated oil rate
rate_lookup_table, sum_df = pf_oil_benefit.calc_oil_rate(liq_lookup_table, merged_test_data)
rate_lookup_table.to_csv(r"results\PF_oil_lookup_table.csv")

pf_oil_benefit.plot_oil_rates(sum_df)
sum_df.to_csv("results/pf_summed oil benefit.csv")

print("fin")
