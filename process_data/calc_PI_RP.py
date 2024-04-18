import pandas as pd
from woffl.flow.inflow import InFlow


def calculate_cumulative_error(group, pres):
    cumulative_error = 0
    for index, row in group.iterrows():
        if index == 0:
            vogel = InFlow(row["WtOilVol"], row["BHP"], pres)
        else:
            calculated_qwf = vogel.oil_flow(row["BHP"], "vogel")
            error = abs(calculated_qwf - row["WtOilVol"])
            cumulative_error += error
    return cumulative_error


def calc_optimal_RP(df):
    unique_wells = df["well"].unique()
    optimal_pres = {}
    for well in unique_wells:
        well_data = df[df["well"] == well]
        min_error = float("inf")
        best_pres = None

        for pres in range(800, 5000, 100):
            error = calculate_cumulative_error(well_data, pres)
            if error < min_error:
                min_error = error
                best_pres = pres

        optimal_pres[well] = best_pres

    df["Optimal_RP"] = df["well"].map(optimal_pres)
    return df
