from typing import Any, Tuple

import matplotlib.pyplot as plt
import pandas as pd


def mean_of_interquartile_range(series: pd.Series) -> float:
    """
    Calculate the mean of the interquartile range (IQR) for a given pandas Series.

    Args:
        series (pd.Series): The input series from which to calculate the IQR mean.

    Returns:
        float: The mean value of the interquartile range.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr_data = series[(series >= q1) & (series <= q3)]
    return iqr_data.mean()


def calc_oil_rate(liq_lookup_table: pd.DataFrame, test_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Pivot the test data to return average values of the test after removing top and bottom quartile.
    Merge the average well test data into the lookup table and calculate the oil rate.

    Args:
        liq_lookup_table (pd.DataFrame): DataFrame with columns "Well", "pf_pres", "bhp", "Fluid_newest_interpolated".
        test_data (pd.DataFrame): DataFrame with all the test columns taken from the merged test data function.

    Returns:
        pd.DataFrame: Updated liq_lookup_table with the addition of watercut column and calculated oil rate.
    """

    test_data["WtOilVol"] = pd.to_numeric(test_data["WtOilVol"], errors="coerce")
    test_data["WtWaterCut"] = pd.to_numeric(test_data["WtWaterCut"], errors="coerce")

    # Drop rows with NaN values in the relevant columns
    test_data = test_data.dropna(subset=["WtOilVol", "WtWaterCut"])

    avgeraged_data = test_data.groupby("well").agg({"WtOilVol": "mean", "WtWaterCut": "mean"}).reset_index()

    updated_liq_lookup_table = pd.merge(liq_lookup_table, avgeraged_data, how="left", left_on="Well", right_on="well")

    updated_liq_lookup_table["Oil_newest_ipr"] = (
        updated_liq_lookup_table["Fluid_newest_interpolated"] * (100 - updated_liq_lookup_table["WtWaterCut"]) / 100
    )

    updated_liq_lookup_table["Oil_lowest_ipr"] = (
        updated_liq_lookup_table["Fluid_lowest_interpolated"] * (100 - updated_liq_lookup_table["WtWaterCut"]) / 100
    )

    updated_liq_lookup_table["Oil_median_ipr"] = (
        updated_liq_lookup_table["Fluid_median_interpolated"] * (100 - updated_liq_lookup_table["WtWaterCut"]) / 100
    )

    sum_df = updated_liq_lookup_table[["pf_pres", "Oil_newest_ipr", "Oil_lowest_ipr", "Oil_median_ipr"]]

    summed_df = sum_df.groupby("pf_pres").sum().reset_index()

    return updated_liq_lookup_table, summed_df


def plot_oil_rates(summed_df: pd.DataFrame):
    """
    Plot the oil rates against pf_pres.

    Args:
        summed_df (pd.DataFrame): DataFrame with summed oil rates and pf_pres.
    """
    fig, axs = plt.subplots(1, 3, figsize=(20, 5))

    axs[0].plot(summed_df["pf_pres"], summed_df["Oil_newest_ipr"], marker="o")
    axs[0].set_title("PF Pressure vs Newest BHP IPR")
    axs[0].set_xlabel("Power Fluid Pressure, psi")
    axs[0].set_ylabel("Oil Rate, bopd")
    axs[0].grid(True)

    axs[1].plot(summed_df["pf_pres"], summed_df["Oil_lowest_ipr"], marker="o")
    axs[1].set_title("PF Pressure vs Lowest BHP IPR")
    axs[1].set_xlabel("Power Fluid Pressure, psi")
    axs[1].set_ylabel("Oil Rate, bopd")
    axs[1].grid(True)

    axs[2].plot(summed_df["pf_pres"], summed_df["Oil_median_ipr"], marker="o")
    axs[2].set_title("PF Pressure vs Median BHP IPR")
    axs[2].set_xlabel("Power Fluid Pressure, psi")
    axs[2].set_ylabel("Oil Rate, bopd")
    axs[2].grid(True)

    plt.tight_layout()
    plt.savefig("plots/pf_oil_benefit.png")
