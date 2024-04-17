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
                    # plt.plot(df["BHP"], trendline, color="red", label=f"Trend line (y={slope:.2f}x+{intercept:.2f})")
                    # Add the curve fit equation as text on the plot
                    equation_text = f"y = {slope:.2f}x + {intercept:.2f}"
                    # plt.text(
                    #    0.05, 0.95, equation_text, transform=plt.gca().transAxes, fontsize=12, verticalalignment="top"
                    # )
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


def plot_grid_BHP_HeaderP(well_dfs):
    # Determine the number of rows and columns for the subplot grid

    filtered_well_dfs = {}
    for well, df in well_dfs.items():
        if "BHP" in df.columns and "HeaderP" in df.columns:

            # Drop points with BHP equal to 0
            df = df[(df["BHP"] != 0)]

            # Check if the DataFrame still has points after dropping BHP=0
            if not df.empty:
                filtered_well_dfs[well] = df

    well_dfs = filtered_well_dfs.copy()

    num_wells = len(well_dfs)
    num_columns = int(math.ceil(math.sqrt(num_wells)))
    num_rows = int(math.ceil(num_wells / num_columns))

    # Create a figure with subplots
    fig, axs = plt.subplots(num_rows, num_columns, figsize=(num_columns * 7, num_rows * 5))
    axs = axs.flatten()  # Flatten the array to make it easier to iterate over

    # Iterate over the well DataFrames and their corresponding axes
    for i, (well, df) in enumerate(well_dfs.items()):
        if "BHP" in df.columns and "HeaderP" in df.columns:
            ax = axs[i]

            latest_date = df.index.max()
            days_since = (latest_date - df.index).days

            scatter = ax.scatter(df["BHP"], df["HeaderP"], c=days_since, cmap="viridis")

            # Add a unit slope line to the plot
            # min_val = min(df["BHP"].min(), df["HeaderP"].min())
            # max_val = max(df["BHP"].max(), df["HeaderP"].max())
            # ax.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--", linewidth=1)

            ax.set_title(f"Data for Well: {well}")
            ax.set_xlabel("BHP")
            ax.set_ylabel("Header Pressure")
            ax.legend()
            ax.grid(True)

            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label("Days Since Data Point")

    # If there are any leftover subplots, turn them off
    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    # Adjust the layout so that plots do not overlap
    plt.tight_layout()

    # Save the entire grid plot as a PNG file
    plt.savefig("plots/well_data_grid_plotBHPheader.png")

    # Optionally, display the plot
    # plt.show()

    # Close the plot to free up memory
    plt.close(fig)


def plot_grid_BHP_WHP(well_dfs):
    # Determine the number of rows and columns for the subplot grid

    filtered_well_dfs = {}
    for well, df in well_dfs.items():
        if "BHP" in df.columns and "WHP" in df.columns:
            # Drop points with BHP equal to 0
            df = df[(df["BHP"] != 0)]

            # Check if the DataFrame still has points after dropping BHP=0
            if not df.empty:
                filtered_well_dfs[well] = df

    well_dfs = filtered_well_dfs.copy()

    num_wells = len(well_dfs)
    num_columns = int(math.ceil(math.sqrt(num_wells)))
    num_rows = int(math.ceil(num_wells / num_columns))

    # Create a figure with subplots
    fig, axs = plt.subplots(num_rows, num_columns, figsize=(num_columns * 7, num_rows * 5))
    axs = axs.flatten()  # Flatten the array to make it easier to iterate over

    # Iterate over the well DataFrames and their corresponding axes
    for i, (well, df) in enumerate(well_dfs.items()):
        if "BHP" in df.columns and "WHP" in df.columns:
            ax = axs[i]

            latest_date = df.index.max()
            days_since = (latest_date - df.index).days

            scatter = ax.scatter(df["BHP"], df["WHP"], c=days_since, cmap="viridis")

            # Add a unit slope line to the plot
            # min_val = min(df["BHP"].min(), df["HeaderP"].min())
            # max_val = max(df["BHP"].max(), df["HeaderP"].max())
            # ax.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--", linewidth=1)

            ax.set_title(f"Data for Well: {well}")
            ax.set_xlabel("BHP")
            ax.set_ylabel("Wellhead Pressure")
            ax.legend()
            ax.grid(True)

            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label("Days Since Data Point")

    # If there are any leftover subplots, turn them off
    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    # Adjust the layout so that plots do not overlap
    plt.tight_layout()

    # Save the entire grid plot as a PNG file
    plt.savefig("plots/well_data_grid_plotBHPWHP.png")

    # Optionally, display the plot
    # plt.show()

    # Close the plot to free up memory
    plt.close(fig)
