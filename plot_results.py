import matplotlib.pyplot as plt
import pandas as pd


def plot_excel_data(filename, sheet_name, column_name=None, bins=10):
    """
    Reads an Excel file into a pandas DataFrame and plots the data in bins.

    Parameters:
    - filename: str, the path to the Excel file.
    - sheet_name: int or str, the sheet to read from the Excel file (default is the first sheet).
    - column_name: str, the name of the column to plot. If None, the first column is used.
    - bins: int, the number of bins to use in the histogram.

    Returns:
    - None, but displays a histogram of the data.
    """
    # Read the Excel file
    df = pd.read_excel(filename, sheet_name=sheet_name)

    # Check if column_name is provided, otherwise use the first column
    if column_name is None:
        column_name = df.columns[0]

    filtered_data = df[column_name][df[column_name] <= 1000]

    # Plot the data
    plt.hist(filtered_data, bins=bins, edgecolor="black")
    plt.title(f"Histogram of {column_name} (<= 1000)")
    plt.xlabel(column_name)
    plt.ylabel("Frequency")
    plt.show()


filename = r"results\BHP_WHP Impact Fieldwide.xlsx"
sheet = "processed_daily_whp_bhp_coeffs"
column_name = "Mean Slope"

plot_excel_data(filename, sheet, column_name)
