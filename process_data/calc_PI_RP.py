import pandas as pd
from woffl.flow.inflow import InFlow


def calculate_cumulative_error(group, pres):
    """
    Calculate the cumulative error between calculated and actual well flow rates.
    Using oil_flow for total liquid to avoid WC metering variability

    Args:
        group (pd.DataFrame): Data for a single well.
        pres (float): Assumed reservoir pressure.

    Returns:
        float: The cumulative error for the well group.
    """
    cumulative_error = 0
    vogel = None
    for index, row in group.iterrows():
        if index == 0:
            vogel = InFlow(row["WtTotalFluid"], row["BHP"], pres)
        else:
            if vogel is not None:
                calculated_qwf = vogel.oil_flow(row["BHP"], "vogel")
                error = abs(calculated_qwf - row["WtTotalFluid"])
                cumulative_error += error
            else:
                print("Error: vogel did not intialize")
                break
    return cumulative_error


def calc_optimal_RP(df):
    """
    Calculate the optimal reservoir pressure for each well and compute productivity index.

    Args:
        df (pd.DataFrame): The DataFrame containing well data.

    Returns:
        pd.DataFrame: The DataFrame with added columns for optimal reservoir pressure and productivity index.
    """
    unique_wells = df["well"].unique()
    optimal_pres = {}
    for well in unique_wells:
        well_data = df[df["well"] == well]
        max_bhp = well_data["BHP"].max()

        if pd.isna(max_bhp):
            print(f"Warning: No valid BHP data for well {well}. Skipping this well.")
            continue  # Skip this iteration if max_bhp is NaN

        min_error = float("inf")
        best_pres = None

        start_pres = max_bhp + 100
        end_pres = 5000

        for pres in range(int(start_pres), end_pres, 10):
            error = calculate_cumulative_error(well_data, pres)
            if error < min_error:
                min_error = error
                best_pres = pres

        optimal_pres[well] = best_pres

    df["Optimal_RP"] = df["well"].map(optimal_pres)

    def calc_PI(row):
        return row["WtTotalFluid"] / (row["Optimal_RP"] - row["BHP"])

    df["PI"] = df.apply(calc_PI, axis=1)
    return df
