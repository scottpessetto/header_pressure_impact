from pathlib import Path

import pandas as pd


def process_tests(file: Path) -> pd.DataFrame:
    """
    Processes a CSV file containing well test data, cleans and formats the data.

    This function reads a CSV file, extracts and formats well names, converts date strings to datetime objects,
    and cleans numeric data fields by removing commas and converting them to numeric types, handling missing values.

    Args:
        file (Path): The file path to the CSV file containing the test data.

    Returns:
        pd.DataFrame: A DataFrame with cleaned and formatted well test data including columns for well name,
                      test date, total fluid, and tubing pressure.

    """
    df = pd.read_csv(file)

    df["WtDate"] = pd.to_datetime(df["WtDate"])
    df["well"] = df["EntName1"].str.extract(r"(\w+-\d+)")
    df["well"] = df["well"].str.replace(r"-(0)(?=\d+)", "-", regex=True)
    df["well"] = "MP" + df["well"].astype(str)

    output = df[["well", "WtDate", "WtTotalFluid", "TubingPress"]]
    for column in ["WtTotalFluid", "TubingPress"]:
        output[column] = output[column].str.replace(",", "").fillna(0).astype(float)

    return output


"""
    output["WtTotalFluid"] = output["WtTotalFluid"].str.replace(",", "").fillna(0)
    output["WtTotalFluid"] = pd.to_numeric(output["WtTotalFluid"], errors="coerce").fillna(0)
    output["TubingPress"] = output["TubingPress"].str.replace(",", "").fillna(0)
    output["TubingPress"] = pd.to_numeric(output["TubingPress"], errors="coerce").fillna(0)
    output["WtDate"] = pd.to_datetime(output["WtDate"])

    return output
"""
