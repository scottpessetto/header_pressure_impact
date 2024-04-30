import math
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from woffl.flow.inflow import InFlow


def plot_bhp_liquidrate(merged_test_scada, RP_guess):
    """
    Plot bottomhole pressure vs liquid rate for each well in a grid of scatter plots,
    fit a trend line, display the equation, and store the coefficients.

    Args:
        merged_test_scada (pd.DataFrame): DataFrame containing the well data with columns 'well', 'BHP', 'WtTotalFluid', and 'WtDate'.

    Returns:
        pd.DataFrame: DataFrame containing the coefficients of the trend lines for each well.
    """
    df = merged_test_scada.copy()
    df["date"] = pd.to_datetime(df["WtDate"])
    current_date = pd.to_datetime("today")
    df["days_since"] = (current_date - df["date"]).dt.days

    unique_wells = df["well"].unique()
    unique_wells.sort()
    num_wells = len(unique_wells)
    num_columns = int(math.ceil(math.sqrt(num_wells)))
    num_rows = int(math.ceil(num_wells / num_columns))

    fig, axs = plt.subplots(num_rows, num_columns, figsize=(num_columns * 7, num_rows * 5))
    axs = axs.flatten()

    coeffs_list = []

    for index, well in enumerate(unique_wells):
        try:
            well_data = df[df["well"] == well]
            well_data = well_data.dropna(subset=["BHP", "WtTotalFluid"])

            """
            well_rp = RP_guess[RP_guess["well"] == well]
            if not well_rp["Optimal_RP"].empty:
                res_p = well_rp["Optimal_RP"].iloc[0]
            else:
                res_p = 1400  # Default value or handle appropriately
            """
            res_p_range = np.linspace(800, 4000, 10)
            min_mse = float("inf")
            optimal_res_p = None

            for res_p in res_p_range:
                vogel = InFlow(well_data["WtTotalFluid"].mean(), well_data["BHP"].mean(), res_p)
                predicted_bhp = [vogel.oil_flow(fluid, "vogel") for fluid in well_data["WtTotalFluid"]]
                mse = np.mean((well_data["BHP"] - predicted_bhp) ** 2)

                if mse < min_mse:
                    min_mse = mse
                    optimal_res_p = res_p

            if len(well_data) > 1:
                scatter = axs[index].scatter(
                    well_data["WtTotalFluid"],
                    well_data["BHP"],
                    c=well_data["days_since"],
                    alpha=0.5,
                    cmap="viridis",
                    label=f"Well {well}",
                )
                y = well_data["BHP"].values
                x = well_data["WtTotalFluid"].values

                slope, intercept = np.polyfit(x, y, 1)

                x_range = np.linspace(x.min(), x.max(), 100)
                y_pred = slope * x_range + intercept

                avg_fluid = well_data["WtTotalFluid"].mean()
                avg_bhp = well_data["BHP"].mean()

                vogel = InFlow(well_data["WtTotalFluid"].mean(), well_data["BHP"].mean(), optimal_res_p)
                qmax = vogel.vogel_qmax(well_data["WtTotalFluid"].mean(), well_data["BHP"].mean(), optimal_res_p)
                bhp_list = []
                fluid_list = []
                for i_bhp in range(0, int(res_p), 10):
                    bhp_list.append(i_bhp)
                    fluid_list.append(vogel.oil_flow(i_bhp, "vogel"))

                axs[index].plot(fluid_list, bhp_list, color="blue", linewidth=3)

                axs[index].plot(x_range, y_pred, color="red", linewidth=2)

                # equation = f"y = {slope:.2f}x + {intercept:.2f}"

                vogel_text = f"Res_P: {optimal_res_p:.2f}, QMax: {qmax:.2f}"

            axs[index].text(
                0.05,
                0.85,
                vogel_text,
                transform=axs[index].transAxes,
                fontsize=12,
                verticalalignment="top",
            )

            # Store coefficients
            coeffs_list.append(
                {"Well": well, "ResP": optimal_res_p, "QMax": qmax, "Avg_fluid": avg_fluid, "Avg_bhp": avg_bhp}
            )

            axs[index].set_ylabel("Bottom Hole Pressure, psi")
            axs[index].set_xlabel("Total Fluid Rate, BPD")
            axs[index].set_title(f"Well {well}")
            axs[index].legend()

            axs[index].set_xlim(left=0)

            # Add colorbar to each subplot
            cbar = fig.colorbar(scatter, ax=axs[index])
            cbar.set_label("Days Since")
        except Exception as e:
            print(f"error with well :{e}")
            continue

    # Hide unused subplots if any
    for i in range(index + 1, len(axs)):
        axs[i].axis("off")

    plt.tight_layout()
    plt.savefig("plots/bhp_liq_grid.png")

    coefficients_df = pd.DataFrame(coeffs_list)
    return coefficients_df
