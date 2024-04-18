# drop negatives
# take median slope
# take median intercept
import pandas as pd


def process_coefficients(coefficients_df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the coefficients DataFrame to group by well name, filter, sort, and calculate median values.

    Args:
        coefficients_df (pd.DataFrame): DataFrame containing well names, dates, slopes, and intercepts.

    Returns:
        pd.DataFrame: A DataFrame with the median slope and median intercept for each well.
    """
    # Group by 'Well' and apply processing to each group
    result = coefficients_df.groupby("Well").apply(lambda group: process_group(group))

    # Reset index to turn the multi-index into columns
    result = result.reset_index()

    return result


def process_group(group: pd.DataFrame) -> pd.Series:
    """
    Helper function to process each group: filters, sorts, and calculates medians.

    Args:
        group (pd.DataFrame): The DataFrame group for a single well.

    Returns:
        pd.Series: A Series containing the median slope and median intercept for the group.
    """
    # Filter out rows where Slope is less than 0
    filtered_group = group[group["Slope"] >= 0]

    # Sort the group by 'Slope'
    sorted_group = filtered_group.sort_values(by="Slope")

    # Calculate median slope and intercept
    # median_slope = sorted_group["Slope"].median()
    # median_intercept = sorted_group["Intercept"].median()
    median_slope = sorted_group["Slope"].mean()
    median_intercept = sorted_group["Intercept"].mean()

    return pd.Series({"Median Slope": median_slope, "Median Intercept": median_intercept})