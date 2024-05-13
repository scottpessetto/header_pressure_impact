import math
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_bhp_vs_headerp(well_dfs):
    """
    Plot BHP versus Header Pressure for each well and fit a linear trend line.

    Args:
        well_dfs (dict of pandas.DataFrame): Dictionary with well identifiers as keys and their data as pandas DataFrames.

    Returns:
        pandas.DataFrame: DataFrame containing the slope and intercept of the fitted line for each well.

    Saves:
        PNG files: Each plot is saved as a PNG file in a directory named 'plots'.
    """
    # Initialize a DataFrame to store the coefficients
    coefficients_list = []

    for well, df in well_dfs.items():

        # Check if both BHP and HeaderP data are available for the well
        if "BHP" in df.columns and "HeaderP" in df.columns:
            df = df[df["BHP"] > 50]
            df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["BHP", "HeaderP"])
            # Fit a linear trend line (1st degree polynomial)
            if df["BHP"].nunique() > 1 and df["HeaderP"].nunique() > 1:
                try:
                    slope, intercept = np.polyfit(df["BHP"], df["HeaderP"], 1)
                    coefficients_list.append({"Well": well, "Slope": slope, "Intercept": intercept})
                    trendline = slope * df["BHP"] + intercept

                    plt.figure(figsize=(10, 5))
                    plt.scatter(df["BHP"], df["HeaderP"], alpha=0.5)
                    plt.plot(df["BHP"], trendline, color="red", label=f"Trend line (y={slope:.2f}x+{intercept:.2f})")
                    # Add the curve fit equation as text on the plot
                    equation_text = f"y = {slope:.2f}x + {intercept:.2f}"
                    plt.text(
                        0.05, 0.95, equation_text, transform=plt.gca().transAxes, fontsize=12, verticalalignment="top"
                    )
                    plt.title(f"BHP vs HeaderP for Well: {well}")
                    plt.xlabel("BHP (Bottom Hole Pressure)")
                    plt.ylabel("HeaderP (Header Pressure)")
                    plt.grid(True)
                    plt.tight_layout()
                    plt.savefig(f"plots/{well}_BHP_vs_HeaderP_plot.png")  # Save the plot as a PNG file
                    # plt.show()
                    plt.close()
                except Exception as e:
                    print(f"error fitting {e}")
                    continue
        else:
            print(f"Data for BHP or HeaderP is missing for well {well}")
    # Create a DataFrame from the list of coefficients
    coefficients_df = pd.DataFrame(coefficients_list)
    return coefficients_df


def plot_grid_BHP_WHP(well_dfs, median_coefficients):
    """
    Plots a grid of BHP vs WHP for each well and overlays a trend line using median coefficients.

    Args:
        well_dfs (dict): Dictionary with well identifiers as keys and their data as pandas DataFrames.
        median_coefficients (pd.DataFrame): DataFrame containing the median slope and intercept for each well.

    Saves:
        PNG file: Grid plot saved as a PNG file in a directory named 'plots'.
    """
    filtered_well_dfs = {}
    for well, df in well_dfs.items():
        if "BHP" in df.columns and "WHP" in df.columns:
            df = df[(df["BHP"] != 0)]
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
        if well in median_coefficients.index:
            slope = median_coefficients.loc[well, "Mean Slope"]
            intercept = median_coefficients.loc[well, "Mean Intercept"]

            # Calculate the trend line using the median slope and intercept
            x_values = np.linspace(df["BHP"].min(), df["BHP"].max(), 100)
            trendline = slope * x_values + intercept

            ax.plot(x_values, trendline, color="red", label=f"Mean trend line (y={slope:.2f}x+{intercept:.2f})")

        scatter = ax.scatter(df["BHP"], df["WHP"], c=(df.index.max() - df.index).days, cmap="viridis")
        ax.set_title(f"Data for Well: {well}")
        ax.set_xlabel("BHP")
        ax.set_ylabel("Wellhead Pressure")
        ax.legend()
        ax.grid(True)

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Days Since Data Point")

    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    plt.tight_layout()
    plt.savefig("plots/well_data_grid_plotBHPWHP.png")
    plt.close(fig)


def plot_grid_BHP_HeaderP_DailyFit(well_dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Plots daily BHP vs HeaderP data for multiple wells and fits a linear regression model to each day's data.
    Additionally, it collects the coefficients of the fitted models.

    WHP is not used due to confusion on whether BHP increased due to WHP or not. Header P is attempting
    to isolate impacts of a more crowded header.

    Args:
        well_dfs (Dict[str, pd.DataFrame]): A dictionary where keys are well names and values are DataFrames
                                            containing BHP and WHP data along with dates.

    Returns:
        pd.DataFrame: A DataFrame containing the well names, dates, slopes, and intercepts of the fitted models.

    Raises:
        ValueError: If any DataFrame is empty after filtering or does not contain the required columns.
    """
    filtered_well_dfs = {}
    coefficients_list = []

    for well, df in well_dfs.items():
        if "BHP" in df.columns and "WHP" in df.columns:
            df = df[(df["BHP"] != 0)]
            df = df.dropna(subset=["BHP"])
            if not df.empty:
                if len(df["BHP"]) > 5:
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

        empty_check = df.dropna(subset=["BHP", "WHP"])
        if empty_check["BHP"].empty:
            continue

        for date, group in df.groupby("Date"):
            group = group.dropna(subset=["BHP", "WHP"])  # Drop rows where BHP or WHP is NaN

            if len(group) > 1:  # Ensure there's enough data to fit the model
                x = group["BHP"].values
                y = group["HeaderP"].values
                slope, intercept = np.polyfit(x, y, 1)
                x_range = np.linspace(x.min(), x.max(), 10)
                y_pred = slope * x_range + intercept

                if slope >= 0.9:
                    ax.plot(x_range, y_pred, label=f'Trend for {date.strftime("%Y-%m-%d")}')
                    valid_slope_found = True
                    coefficients_list.append({"Well": well, "Date": date, "Slope": slope, "Intercept": intercept})

        scatter = ax.scatter(df["BHP"], df["HeaderP"], c=pd.to_datetime(df["Date"]).astype("int64"), cmap="viridis")
        ax.set_title(f"Data for Well: {well}")
        ax.set_xlabel("Bottom Hole Pressure, psi")
        ax.set_ylabel("Well Head Pressure, psi")
        # ax.legend()
        ax.grid(True)
        if not valid_slope_found:
            coefficients_list.append({"Well": well, "Date": pd.NaT, "Slope": 1000000, "Intercept": np.nan})

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Date")

    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    plt.tight_layout()
    plt.savefig("plots/well_data_grid_plotBHP_HeaderP_dailyfit.png")
    plt.close(fig)

    coefficients_df = pd.DataFrame(coefficients_list)
    return coefficients_df


def plot_grid_BHP_WHP_DailyFit(well_dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Plots daily BHP vs WHP data for multiple wells and fits a linear regression model to each day's data.
    Additionally, it collects the coefficients of the fitted models.

    After much investigation and usage, I found that wells with a slope <1 of whp/bhp typically saw no
    real impact from WHP upon investigation and it was just slugging of the BHP irresepective of header P

    Mean values also were the most useful

    Args:
        well_dfs (Dict[str, pd.DataFrame]): A dictionary where keys are well names and values are DataFrames
                                            containing BHP and WHP data along with dates.

    Returns:
        pd.DataFrame: A DataFrame containing the well names, dates, slopes, and intercepts of the fitted models.

    Raises:
        ValueError: If any DataFrame is empty after filtering or does not contain the required columns.
    """
    filtered_well_dfs = {}
    coefficients_list = []

    for well, df in well_dfs.items():
        if "BHP" in df.columns and "WHP" in df.columns:
            df = df[(df["BHP"] != 0)]
            df = df.dropna(subset=["BHP"])
            if not df.empty:
                if len(df["BHP"]) > 5:
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

        empty_check = df.dropna(subset=["BHP", "WHP"])
        if empty_check["BHP"].empty:
            continue

        for date, group in df.groupby("Date"):
            group = group.dropna(subset=["BHP", "WHP"])  # Drop rows where BHP or WHP is NaN

            if len(group) > 1:  # Ensure there's enough data to fit the model
                x = group["BHP"].values
                y = group["WHP"].values
                slope, intercept = np.polyfit(x, y, 1)
                x_range = np.linspace(x.min(), x.max(), 10)
                y_pred = slope * x_range + intercept

                if slope >= 0.9:
                    ax.plot(x_range, y_pred, label=f'Trend for {date.strftime("%Y-%m-%d")}')
                    valid_slope_found = True
                    coefficients_list.append({"Well": well, "Date": date, "Slope": slope, "Intercept": intercept})

        scatter = ax.scatter(df["BHP"], df["WHP"], c=pd.to_datetime(df["Date"]).astype("int64"), cmap="viridis")
        ax.set_title(f"Data for Well: {well}")
        ax.set_xlabel("Bottom Hole Pressure, psi")
        ax.set_ylabel("Well Head Pressure, psi")
        # ax.legend()
        ax.grid(True)
        if not valid_slope_found:
            coefficients_list.append({"Well": well, "Date": pd.NaT, "Slope": 1000000, "Intercept": np.nan})

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Date")

    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    plt.tight_layout()
    plt.savefig("plots/well_data_grid_plotBHP_WHP_dailyfit.png")
    plt.close(fig)

    coefficients_df = pd.DataFrame(coefficients_list)
    return coefficients_df


def plot_grid_BHP_WHP_HourlyFit(well_dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Plots daily BHP vs WHP data for multiple wells and fits a linear regression model to each day's data.
    Additionally, it collects the coefficients of the fitted models.

    Args:
        well_dfs (Dict[str, pd.DataFrame]): A dictionary where keys are well names and values are DataFrames
                                            containing BHP and WHP data along with dates.

    Returns:
        pd.DataFrame: A DataFrame containing the well names, dates, slopes, and intercepts of the fitted models.

    Raises:
        ValueError: If any DataFrame is empty after filtering or does not contain the required columns.
    """
    filtered_well_dfs = {}
    coefficients_list = []
    for well, df in well_dfs.items():
        if "BHP" in df.columns and "WHP" in df.columns:
            df = df[(df["BHP"] != 0)]
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
        if "Date" not in df.columns:
            df["Date"] = df.index.date  # Convert index to date if necessary

        for time, group in df.groupby(pd.Grouper(freq="4h")):
            group = group.dropna(subset=["BHP", "WHP"])  # Drop rows where BHP or WHP is NaN
            if len(group) > 1:  # Ensure there's enough data to fit the model
                x = group["BHP"].values
                y = group["WHP"].values
                slope, intercept = np.polyfit(x, y, 1)
                x_range = np.linspace(x.min(), x.max(), 10)
                y_pred = slope * x_range + intercept

                if slope > 0.9:
                    ax.plot(x_range, y_pred, label=f'Trend for {time.strftime("%Y-%m-%d %H:%M")}')
                    valid_slope_found = True
                    coefficients_list.append({"Well": well, "Date": time, "Slope": slope, "Intercept": intercept})

        scatter = ax.scatter(df["BHP"], df["WHP"], c=pd.to_datetime(df["Date"]).astype("int64"), cmap="viridis")
        ax.set_title(f"Data for Well: {well}")
        ax.set_xlabel("BHP")
        ax.set_ylabel("Wellhead Pressure")
        # ax.legend()
        ax.grid(True)

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Date")
        if not valid_slope_found:
            coefficients_list.append({"Well": well, "Date": pd.NaT, "Slope": 1000000, "Intercept": np.nan})

    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    plt.tight_layout()
    plt.savefig("plots/well_data_grid_plotBHP_WHP_hourlyfit.png")
    plt.close(fig)

    coefficients_df = pd.DataFrame(coefficients_list)
    return coefficients_df
