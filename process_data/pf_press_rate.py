import numpy as np
import pandas as pd


def bhp_lookup(slope_df):
    """
    Using the line fit average taken from the power fluid pressure versus
    bottom hole pressure data, create an estimated bottom hole pressure for a given power fluid pressure

    Args:
        slope_df (df): dataframe with each well and their respective slope and intercept
                        for the bhp vs pf fit

    Returns:
        Dataframe with an expected BHP for each powerfluid pressure
    """

    new_rows = []

    for index, row in slope_df.iterrows():
        well = row["Well"]
        slope = row["Mean Slope"]
        intercept = row["Mean Intercept"]

        # Generate pf_pres values from 1800 to 3300 with increments of 50
        for pf_pres in range(1800, 3350, 50):
            bhp = slope * pf_pres + intercept
            new_rows.append({"Well": well, "pf_pres": pf_pres, "bhp": bhp})

    # Create a new DataFrame from the new rows
    bhp_lookup = pd.DataFrame(new_rows)

    return bhp_lookup


def interpolate_fluid_newest(well, bhp_value, ipr_df):
    # Filter the ipr_lookup dataframe for the specific well
    well_data = ipr_df[ipr_df["well"] == well]

    print(bhp_value)

    well_data["BHP"] = pd.to_numeric(well_data["BHP"], errors="coerce")
    well_data["Fluid_newest"] = pd.to_numeric(well_data["Fluid_newest"], errors="coerce")

    well_data = well_data.dropna(subset=["BHP", "Fluid_newest"])

    if well_data.empty:
        return np.nan

    interpolated_value = np.interp(bhp_value, well_data["BHP"], well_data["Fluid_newest"])
    print(interpolated_value, bhp_value)

    return interpolated_value


def assign_liquid_rate(ipr_lookup, bhp_lookup):
    """
    Take the bottom hole calculation data and assign a liquid rate for each
    bottom hole pressure

    Args:
        ipr_lookup (df): table for each well with three different estimated liquid rates
        for a given bottom hole pressure [Fluid_newest, Fluid_lowest, Fluid_median]

        bhp_lookup(df): dataframe that serves as a table of expected bhp for a given
        powerfluid rate

    Returns:
        Dataframe that has three possible fluid rates for each BHP that is correlated
        to a power fluid pressure
    """

    bhp_lookup["Fluid_newest_interpolated"] = bhp_lookup.apply(
        lambda row: interpolate_fluid_newest(row["Well"], row["bhp"], ipr_lookup), axis=1
    )

    return bhp_lookup
