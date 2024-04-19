# plot_wells.py

import math
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_well_dataframes(pickle_file):
    """
    Load well data from a pickle file into a dictionary of pandas DataFrames.

    Args:
        pickle_file (str): The path to the pickle file containing the well data.

    Returns:
        dict: A dictionary where each key is a well identifier and each value is a pandas DataFrame containing data for that well.
    """
    with open(pickle_file, "rb") as handle:
        well_dfs = pickle.load(handle)
    return well_dfs


def plot_wells(well_dfs):
    """
    Generate and save a line plot for each well's data.

    Args:
        well_dfs (dict of pandas.DataFrame): A dictionary containing well identifiers as keys and their corresponding data as pandas DataFrames.

    Saves:
        PNG files: Each plot is saved as a PNG file in a directory named 'plots'.
    """
    for well, df in well_dfs.items():
        plt.figure(figsize=(10, 5))
        for column in df.columns:
            plt.plot(df.index, df[column], label=column)
        plt.title(f"Data for Well: {well}")
        plt.xlabel("Datetime")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"plots/{well}_plot.png")  # Save the plot as a PNG file
        # plt.show()
        plt.close()


def plot_grid(well_dfs):
    """
    Create a grid of plots for all wells, each subplot representing one well.

    Args:
        well_dfs (dict of pandas.DataFrame): A dictionary where each key is a well identifier and each value is a DataFrame with the well's data.

    Saves:
        PNG file: A single image file containing all the plots in a grid layout.
    """
    # Determine the number of rows and columns for the subplot grid
    num_wells = len(well_dfs)
    num_columns = int(math.ceil(math.sqrt(num_wells)))
    num_rows = int(math.ceil(num_wells / num_columns))

    # Create a figure with subplots
    fig, axs = plt.subplots(num_rows, num_columns, figsize=(num_columns * 7, num_rows * 5))
    axs = axs.flatten()  # Flatten the array to make it easier to iterate over

    # Iterate over the well DataFrames and their corresponding axes
    for i, (well, df) in enumerate(well_dfs.items()):
        ax = axs[i]
        for column in df.columns:
            ax.plot(df.index, df[column], label=column)
        ax.set_title(f"Data for Well: {well}")
        ax.set_xlabel("Datetime")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True)

    # If there are any leftover subplots, turn them off
    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    # Adjust the layout so that plots do not overlap
    plt.tight_layout()

    # Save the entire grid plot as a PNG file
    plt.savefig("plots/well_data_grid_plot.png")

    # Optionally, display the plot
    # plt.show()

    # Close the plot to free up memory
    plt.close(fig)


def plot_liquid_rate(well_dfs, tests):
    """
    Plot liquid rate data for each well along with test data points.

    Args:
        well_dfs (dict of pandas.DataFrame): Dictionary with well identifiers as keys and their data as pandas DataFrames.
        tests (pandas.DataFrame): DataFrame containing test data with columns 'WtDate', 'well', and 'WtTotalFluid'.

    Saves:
        PNG files: Each plot is saved as a PNG file in a directory named 'plots'.
    """
    tests["WtDate"] = tests["WtDate"].dt.tz_localize(None)
    for well, df in well_dfs.items():
        plt.figure(figsize=(10, 5))
        df.index = df.index.tz_localize(None)

        for column in df.columns:
            plt.plot(df.index, df[column], label=column)

        test_data = tests[(tests["well"] == well) & (tests["WtDate"].between(df.index.min(), df.index.max()))]

        if not test_data.empty:
            plt.scatter(test_data["WtDate"], test_data["WtTotalFluid"], color="red", label="WtTotalFluid", zorder=5)

        plt.title(f"Data for Well: {well}")
        plt.xlabel("Datetime")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"plots/{well}_plot_liquid.png")  # Save the plot as a PNG file
        # plt.show()
        plt.close()


def plot_liquid_rate2(well_dfs, tests):
    """
    Plot liquid rate data for each well with a secondary axis for test data points.

    Args:
        well_dfs (dict of pandas.DataFrame): Dictionary with well identifiers as keys and their data as pandas DataFrames.
        tests (pandas.DataFrame): DataFrame containing test data with columns 'WtDate', 'well', and 'WtTotalFluid'.

    Saves:
        PNG files: Each plot is saved as a PNG file in a directory named 'plots', showing dual y-axes for well data and test data.
    """
    tests["WtDate"] = tests["WtDate"].dt.tz_localize(None)

    for well, df in well_dfs.items():
        plt.figure(figsize=(10, 5))
        df.index = df.index.tz_localize(None)

        # Create the primary y-axis for the liquid rate data
        ax1 = plt.gca()  # Get the current axes instance

        for column in df.columns:
            ax1.plot(df.index, df[column], label=column)

        # Set labels and title for the primary y-axis
        ax1.set_xlabel("Datetime")
        ax1.set_ylabel("Value")
        ax1.set_title(f"Data for Well: {well}")
        ax1.grid(True)

        # Create the secondary y-axis for the WtTotalFluid data
        ax2 = ax1.twinx()  # Create a second y-axis that shares the same x-axis

        # Filter the test data for the current well and within the date range
        test_data = tests[(tests["well"] == well) & (tests["WtDate"].between(df.index.min(), df.index.max()))]

        if not test_data.empty:
            # Plot the WtTotalFluid data on the secondary y-axis
            ax2.scatter(test_data["WtDate"], test_data["WtTotalFluid"], color="red", label="WtTotalFluid", zorder=5)
            ax2.set_ylabel("WtTotalFluid")  # Label for the secondary y-axis

        # Add legends for both y-axes
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

        plt.tight_layout()

        # Save the plot as a PNG file
        plt.savefig(f"plots/{well}_plot_liquid2.png")

        # Uncomment the next line if you want to display the plot
        # plt.show()

        plt.close()


def plot_whp_vs_liquid(well_dfs, tests):
    """
    Plot wellhead pressure versus total fluid for each well during test periods.

    Args:
        well_dfs (dict of pandas.DataFrame): Dictionary with well identifiers as keys and their data as pandas DataFrames.
        tests (pandas.DataFrame): DataFrame containing test data with columns 'WtDate', 'well', 'TubingPress', and 'WtTotalFluid'.

    Saves:
        PNG files: Each plot is saved as a PNG file in a directory named 'plots'.
    """
    # Initialize a DataFrame to store the coefficients
    # coefficients_list = []

    tests["WtDate"] = tests["WtDate"].dt.tz_localize(None)

    # well dfs, just informs what to plot
    for well, df in well_dfs.items():
        plt.figure(figsize=(10, 5))
        test_data = tests[(tests["well"] == well) & (tests["WtDate"].between(df.index.min(), df.index.max()))]

        if not test_data.empty:
            plt.scatter(test_data["TubingPress"], test_data["WtTotalFluid"])

        plt.title(f"Data for Well: {well}")
        plt.xlabel("wellhead pressure during test")
        plt.ylabel("Total Fluid")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"plots/{well}_whp_liq.png")  # Save the plot as a PNG file
        # plt.show()
        plt.close()
