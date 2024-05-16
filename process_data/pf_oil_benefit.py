from typing import Any

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


def calc_oil_rate(liq_lookup_table: pd.DataFrame, test_data: pd.DataFrame) -> pd.DataFrame:
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

    updated_liq_lookup_table["Oil Predicted"] = (
        updated_liq_lookup_table["Fluid_newest_interpolated"] * (100 - updated_liq_lookup_table["WtWaterCut"]) / 100
    )

    return updated_liq_lookup_table
