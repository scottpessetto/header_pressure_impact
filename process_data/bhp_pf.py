import math
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_grid_bhp_vs_pf_pres(well_dfs: Dict[str, pd.DataFrame]):
    """
    Plots a grid of BHP vs WHP for each well and overlays a trend line using median coefficients.

    Args:
        well_dfs (dict): Dictionary with well identifiers as keys and their data as pandas DataFrames.

    Saves:
        PNG file: Grid plot saved as a PNG file in a directory named 'plots'.
    """
    filtered_well_dfs = {}
    for well, df in well_dfs.items():
        if "BHP" in df.columns and "PF_Pres" in df.columns:
            df = df[(df["BHP"] != 0)]
            df = df[(df["PF_Rate"] > 500)]
            df = df[(df["PF_Pres"] > 1500)]
            if not df.empty:
                filtered_well_dfs[well] = df

    well_dfs = filtered_well_dfs.copy()
    num_wells = len(well_dfs)
    num_columns = int(math.ceil(math.sqrt(num_wells)))
    num_rows = int(math.ceil(num_wells / num_columns))

    fig, axs = plt.subplots(num_rows, num_columns, figsize=(num_columns * 7, num_rows * 5))
    axs = axs.flatten()

    for i, (well, df) in enumerate(well_dfs.items()):
        ax = axs[i]

        scatter = ax.scatter(df["PF_Pres"], df["BHP"], c=df["PF_Rate"], cmap="viridis")
        ax.set_title(f"Data for Well: {well}")
        ax.set_xlabel("Power Fluid Pressure")
        ax.set_ylabel("Bottom Hole Pressure")
        ax.legend()
        ax.grid(True)

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Power Fluid Rate")

    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    plt.tight_layout()
    plt.savefig("plots/well_data_grid_plotBHP_PF_pres.png")
    plt.close(fig)


def plot_grid_BHP_PF_Pres_DailyFit(well_dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Plots daily BHP vs Power Pressure data for multiple wells and fits a linear regression model to each day's data.
    Additionally, it collects the coefficients of the fitted models.


    Args:
        well_dfs (Dict[str, pd.DataFrame]): A dictionary where keys are well names and values are DataFrames
                                            containing BHP and Power Pressure and rate data along with dates.

    Returns:
        pd.DataFrame: A DataFrame containing the well names, dates, slopes, and intercepts of the fitted models.

    Raises:
        ValueError: If any DataFrame is empty after filtering or does not contain the required columns.
    """
    filtered_well_dfs = {}
    coefficients_list = []
    for well, df in well_dfs.items():
        if "BHP" in df.columns and "PF_Pres" in df.columns:
            df = df[(df["BHP"] != 0)]
            df = df[(df["PF_Rate"] > 500)]
            df = df[(df["PF_Pres"] > 1500)]
            if not df.empty:
                filtered_well_dfs[well] = df

    well_dfs = filtered_well_dfs.copy()
    num_wells = len(well_dfs)
    num_columns = int(math.ceil(math.sqrt(num_wells)))
    num_rows = int(math.ceil(num_wells / num_columns))

    fig, axs = plt.subplots(num_rows, num_columns, figsize=(num_columns * 7, num_rows * 5))
    axs = axs.flatten()

    for i, (well, df) in enumerate(well_dfs.items()):
        ax = axs[i]
        valid_slope_found = False
        # Assuming 'Date' is a column in df
        if "Date" not in df.columns:
            df["Date"] = df.index.date  # Convert index to date if necessary

        empty_check = df.dropna(subset=["BHP", "PF_Pres"])
        if empty_check["BHP"].empty:
            continue

        for date, group in df.groupby("Date"):
            group = group.dropna(subset=["BHP", "PF_Pres"])  # Drop rows where BHP or WHP is NaN

            if len(group) > 1:  # Ensure there's enough data to fit the model
                y = group["BHP"].values
                x = group["PF_Pres"].values
                slope, intercept = np.polyfit(x, y, 1)
                x_range = np.linspace(x.min(), x.max(), 10)
                y_pred = slope * x_range + intercept

                if slope < 0:
                    ax.plot(x_range, y_pred, label=f'Trend for {date.strftime("%Y-%m-%d")}')
                    valid_slope_found = True
                    coefficients_list.append({"Well": well, "Date": date, "Slope": slope, "Intercept": intercept})

        scatter = ax.scatter(df["PF_Pres"], df["BHP"], c=df["PF_Rate"], cmap="viridis")
        ax.set_title(f"Data for Well: {well}")
        ax.set_xlabel("Power Fluid Pressure, psi")
        ax.set_ylabel("Bottom Hole Pressure, psi")
        # ax.legend()
        ax.grid(True)
        if not valid_slope_found:
            coefficients_list.append({"Well": well, "Date": pd.NaT, "Slope": np.nan, "Intercept": np.nan})

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Power Fluid Rate")

    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    plt.tight_layout()
    plt.savefig("plots/well_data_grid_plotBHP_PFPres_dailyfit.png")
    plt.close(fig)

    coefficients_df = pd.DataFrame(coefficients_list)
    return coefficients_df
