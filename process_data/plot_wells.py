# plot_wells.py

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_well_dataframes(pickle_file):
    with open(pickle_file, "rb") as handle:
        well_dfs = pickle.load(handle)
    return well_dfs


def plot_wells(well_dfs):
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


def plot_liquid_rate(well_dfs, tests):
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


# Load the well dataframes from the pickle file
print("  ")
print("start")
well_dfs = load_well_dataframes("well_dataframes.pkl")

tests = pd.read_pickle("well_tests.pkl")

# Plot each well's data

plot_wells(well_dfs)
coefficients_df = plot_bhp_vs_headerp(well_dfs)
coefficients_df.to_csv("well_coefficients.csv", index=False)

plot_liquid_rate(well_dfs, tests)

print("complete")
