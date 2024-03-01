import re

import pandas as pd


def process_tests(file):
    df = pd.read_csv(file)

    df["WtDate"] = pd.to_datetime(df["WtDate"])
    df["well"] = df["EntName1"].str.extract(r"(\w+-\d+)")
    df["well"] = df["well"].str.replace(r"-(0)(?=\d+)", "-", regex=True)
    df["well"] = "MP" + df["well"].astype(str)

    output = df[["well", "WtDate", "WtTotalFluid", "TubingPress"]]
    output["WtTotalFluid"] = output["WtTotalFluid"].str.replace(",", "").fillna(0)
    output["WtTotalFluid"] = pd.to_numeric(output["WtTotalFluid"], errors="coerce").fillna(0)
    output["TubingPress"] = output["TubingPress"].str.replace(",", "").fillna(0)
    output["TubingPress"] = pd.to_numeric(output["TubingPress"], errors="coerce").fillna(0)
    output["WtDate"] = pd.to_datetime(output["WtDate"])

    return output