import math
import pickle

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


def plot_grid_BHP_WHP_dailyFIT(well_dfs):
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
        # Assuming 'Date' is a column in df
        if "Date" not in df.columns:
            df["Date"] = df.index.date  # Convert index to date if necessary

        for date, group in df.groupby("Date"):
            group = group.dropna(subset=["BHP", "WHP"])  # Drop rows where BHP or WHP is NaN
            if len(group) > 1:  # Ensure there's enough data to fit the model
                x = group["BHP"].values
                y = group["WHP"].values
                slope, intercept = np.polyfit(x, y, 1)
                x_range = np.linspace(x.min(), x.max(), 100)
                y_pred = slope * x_range + intercept
                ax.plot(x_range, y_pred, label=f'Trend for {date.strftime("%Y-%m-%d")}')

        scatter = ax.scatter(df["BHP"], df["WHP"], c=pd.to_datetime(df["Date"]).astype("int64"), cmap="viridis")
        ax.set_title(f"Data for Well: {well}")
        ax.set_xlabel("BHP")
        ax.set_ylabel("Wellhead Pressure")
        ax.legend()
        ax.grid(True)

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Date")

    for j in range(i + 1, len(axs)):
        axs[j].axis("off")

    plt.tight_layout()
    plt.savefig("plots/well_data_grid_plotBHPWHP_dailyfit.png")
    plt.close(fig)
