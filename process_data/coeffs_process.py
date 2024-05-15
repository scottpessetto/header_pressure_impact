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

    Mean slope is the most accurate to use for the wells

    Args:
        group (pd.DataFrame): The DataFrame group for a single well.

    Returns:
        pd.Series: A Series containing the mean slope and mean intercept for the group.
    """
    # Filter out rows where Slope is less than 0
    filtered_group = group[group["Slope"] < 0.9]
    # filtered_group = group.copy()

    # Sort the group by 'Slope'
    sorted_group = filtered_group.sort_values(by="Slope")

    # Calculate median slope and intercept
    # median_slope = sorted_group["Slope"].median()
    # median_intercept = sorted_group["Intercept"].median()
    median_slope = sorted_group["Slope"].median()
    median_intercept = sorted_group["Intercept"].median()

    if sorted_group["Slope"].count() > 3:
        mean_slope = sorted_group["Slope"].mean()
        mean_intercept = sorted_group["Intercept"].mean()
    else:
        mean_slope = int(1000000)
        mean_intercept = int(0)

    return pd.Series({"Mean Slope": mean_slope, "Mean Intercept": mean_intercept})
