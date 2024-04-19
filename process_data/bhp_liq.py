import math
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_bhp_liquidrate(merged_test_scada):
    """
    Plot bottomhole pressure vs liquid rate for each well in a grid of scatter plots.

    Args:
        merged_test_scada (pd.DataFrame): DataFrame containing the well data with columns 'well', 'BHP', and 'WtTotalFluid'.

    Returns:
        None: This function plots the graphs.
    """
    df = merged_test_scada.copy()

    df["date"] = pd.to_datetime(df["WtDate"])

    current_date = pd.to_datetime("today")
    df["days_since"] = (current_date - df["date"]).dt.days

    unique_wells = df["well"].unique()

    # Determine the layout of the subplot grid
    num_wells = len(unique_wells)
    num_columns = int(math.ceil(math.sqrt(num_wells)))
    num_rows = int(math.ceil(num_wells / num_columns))

    fig, axs = plt.subplots(num_rows, num_columns, figsize=(num_columns * 7, num_rows * 5))
    axs = axs.flatten()

    for index, well in enumerate(unique_wells):
        well_data = df[df["well"] == well]

        # Create scatter plot BHP vs WtTotalFluid colored by days since
        scatter = axs[index].scatter(
            well_data["BHP"],
            well_data["WtTotalFluid"],
            c=well_data["days_since"],
            alpha=0.5,
            cmap="viridis",
            label=f"Well {well}",
        )
        axs[index].set_xlabel("Bottom Hole Pressure, psi")
        axs[index].set_ylabel("Total Fluid Rate, BPD")
        axs[index].set_title(f"Well {well}")
        axs[index].legend()

        # Add colorbar to each subplot
        cbar = fig.colorbar(scatter, ax=axs[index])
        cbar.set_label("Days Since")

    # Hide unused subplots if any
    for i in range(index + 1, len(axs)):
        axs[i].axis("off")

    plt.tight_layout()
    plt.savefig("plots/bhp_liq_grid.png")
