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
    plt.savefig("plots/B-pad bhp_liq_grid.png")

    coefficients_df = pd.DataFrame(coeffs_list)
    return coefficients_df


def plot_bhp_liquidrate_r2(RP_guess, resp_modifier):
    """
    Plot bottomhole pressure vs liquid rate for each well in a grid of scatter plots,
    fit a trend line, display the equation, and store the coefficients.

    Args:
        merged_test_scada (pd.DataFrame): DataFrame containing the well data with columns 'well', 'BHP', 'WtTotalFluid', and 'WtDate'.

    Returns:
        pd.DataFrame: DataFrame containing the coefficients of the trend lines for each well.
    """
    df = RP_guess.copy()
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

    ipr_list = []

    for index, well in enumerate(unique_wells):
        try:
            well_data = df[df["well"] == well]
            well_data = well_data.dropna(subset=["BHP", "WtTotalFluid"])

            optimal_res_p = well_data["Optimal_RP"].iloc[0] + resp_modifier

            scatter = axs[index].scatter(
                well_data["WtTotalFluid"],
                well_data["BHP"],
                c=well_data["days_since"],
                alpha=0.5,
                cmap="viridis",
            )
            well_data = well_data.sort_values(by="days_since")
            # create a vogel object with the optimal RP but use the most recent fluid and bhp data
            vogel1 = InFlow(well_data["WtTotalFluid"].iloc[0], well_data["BHP"].iloc[0], optimal_res_p)
            qmax1 = vogel1.vogel_qmax(well_data["WtTotalFluid"].iloc[0], well_data["BHP"].iloc[0], optimal_res_p)
            bhp_list1 = []
            fluid_list1 = []
            for i_bhp in range(0, int(optimal_res_p), 10):
                bhp_list1.append(i_bhp)
                # using oil flow but it is total fluid
                fluid_list1.append(vogel1.oil_flow(i_bhp, "vogel"))

            axs[index].plot(fluid_list1, bhp_list1, color="blue", linewidth=3, label="Most Recent BHP IPR")

            # plot with the lowest bhp data point
            well_data2 = well_data.sort_values(by="BHP")
            vogel2 = InFlow(well_data2["WtTotalFluid"].iloc[0], well_data2["BHP"].iloc[0], optimal_res_p)
            qmax2 = vogel2.vogel_qmax(well_data2["WtTotalFluid"].iloc[0], well_data2["BHP"].iloc[0], optimal_res_p)
            bhp_list2 = []
            fluid_list2 = []
            for i_bhp in range(0, int(optimal_res_p), 10):
                bhp_list2.append(i_bhp)
                # using oil flow but it is total fluid
                fluid_list2.append(vogel2.oil_flow(i_bhp, "vogel"))

            axs[index].plot(fluid_list2, bhp_list2, color="red", linewidth=3, label="Lowest BHP IPR")

            # Plot with the median
            # Calculate the median BHP
            median_bhp = well_data2["BHP"].median()
            # Find the row in well_data2 that is closest to the median BHP
            closest_median_row = well_data2.iloc[(well_data2["BHP"] - median_bhp).abs().argsort()[:1]]
            # Extract values from the closest row
            median_bhp_value = closest_median_row["BHP"].values[0]
            median_fluid_rate = closest_median_row["WtTotalFluid"].values[0]
            # Create an InFlow object using the median BHP and associated WtTotalFluid
            median_vogel = InFlow(median_fluid_rate, median_bhp_value, optimal_res_p)
            # Calculate Qmax for the median BHP
            median_qmax = median_vogel.vogel_qmax(median_fluid_rate, median_bhp_value, optimal_res_p)
            # Generate a flow curve for the median BHP (example range and step can be adjusted)
            median_bhp_list = []
            median_fluid_list = []
            for i_bhp in range(0, int(optimal_res_p), 10):
                median_bhp_list.append(i_bhp)
                median_fluid_list.append(median_vogel.oil_flow(i_bhp, "vogel"))

            # Plot the median flow curve
            axs[index].plot(median_fluid_list, median_bhp_list, color="green", linewidth=3, label="Median BHP IPR")

            # Store coefficients
            coeffs_list.append(
                {
                    "Well": well,
                    "ResP": optimal_res_p,
                    "QMax Oldest BHP": qmax1,
                    "QMax Lowest BHP": qmax2,
                    "QMax Mediam": median_qmax,
                    "Most_recent_fluid": well_data["WtTotalFluid"].iloc[0],
                    "Most_recent_bhp": well_data["BHP"].iloc[0],
                    "Lowest BHP_fluid": well_data2["WtTotalFluid"].iloc[0],
                    "Lowest BHP bhp": well_data2["BHP"].iloc[0],
                }
            )
            ipr_list.append(
                {
                    "well": well,
                    "BHP oldest": bhp_list1,
                    "BHP lowest": bhp_list2,
                    "BHP Median": median_bhp_list,
                    "Fluid oldest": fluid_list1,
                    "Fluid lowest bhp": fluid_list2,
                    "Fluid Median BHP": median_fluid_list,
                }
            )
            axs[index].set_ylabel("Bottom Hole Pressure, psi")
            axs[index].set_xlabel("Total Fluid Rate, BPD")
            axs[index].set_title(f"Well {well}")
            axs[index].legend()

            axs[index].set_xlim(left=0)

            # Add colorbar to each subplot
            cbar = fig.colorbar(scatter, ax=axs[index])
            cbar.set_label("Days Since Well Test")
        except Exception as e:
            print(f"error with well {well} :{e}")
            continue

    # Hide unused subplots if any
    for i in range(index + 1, len(axs)):
        axs[i].axis("off")

    plt.tight_layout()
    plt.savefig("plots/B-pad bhp_liq_grid_latest_test.png")

    coefficients_df = pd.DataFrame(coeffs_list)
    ipr_data = pd.DataFrame(ipr_list)

    # Assuming ipr_data is your DataFrame from the function above

    # Explode each list column into its own DataFrame
    df_bhp_oldest = ipr_data.explode("BHP oldest").rename(columns={"BHP oldest": "BHP"})
    # df_bhp_lowest = ipr_data.explode("BHP lowest").rename(columns={"BHP lowest": "BHP_lowest"})
    # df_bhp_median = ipr_data.explode("BHP Median").rename(columns={"BHP Median": "BHP_median"})
    df_fluid_oldest = ipr_data.explode("Fluid oldest").rename(columns={"Fluid oldest": "Fluid_newest"})
    df_fluid_lowest = ipr_data.explode("Fluid lowest bhp").rename(columns={"Fluid lowest bhp": "Fluid_lowest"})
    df_fluid_median = ipr_data.explode("Fluid Median BHP").rename(columns={"Fluid Median BHP": "Fluid_median"})

    # Combine the exploded DataFrames
    # Ensure all DataFrames have the 'well' column for a proper join
    df_combined = pd.concat(
        [
            df_bhp_oldest[["well", "BHP"]],
            df_fluid_oldest["Fluid_newest"],
            df_fluid_lowest["Fluid_lowest"],
            df_fluid_median["Fluid_median"],
        ],
        axis=1,
    )

    # Now df_combined should have the structure you want

    return coefficients_df, df_combined
