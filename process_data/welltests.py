import pandas as pd


class FDCProcessor:
    def __init__(self, test_path):
        self.test_path = test_path

        self.latest_entries = None

    def get_welltests(self):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(self.test_path)

        # Ensure that 'WtDate' is a datetime type for proper comparison
        df["WtDate"] = pd.to_datetime(df["WtDate"])

        # Sort the DataFrame by 'EntName1' and 'WtDate' to ensure the latest dates are last
        df = df.sort_values(by=["EntName1", "WtDate"])

        # latest_entries["well"] = latest_entries["EntName1"].str[3:9]
        # Extract the well name and remove any trailing letters
        df["well"] = df["EntName1"].str.extract(r"(\w+-\d+)")

        # Remove the leading zeros
        df["well"] = df["well"].str.replace(r"-(0)(?=\d+)", "-", regex=True)
        df["well"] = "MP" + df["well"]

        df = df.drop(
            [
                "BHP",
                "RouteGroupName",
                "EntName1",
                "WtHours",
                "Choke",
                "ChangeUser",
                "Textbox29",
                "WtSeparatorTemp",
                "WtLinePressVal",
                "WtEspFrequency",
                "Textbox26",
                "WtEspAmps",
                "WtWaterCutShakeout",
                "SolidsPct",
            ],
            axis=1,
        )
        for column in [
            "IA",
            "WtOilVol",
            "WtGasVol",
            "WtGasRate",
            "WtGasLiftVol",
            "WtWaterVol",
            "WtrLift",
            "WtTotalFluid",
        ]:
            df[column] = df[column].str.replace(",", "").fillna(0).astype(float)

        # Store the result in the instance variable
        # df = df[df["well"] == well]

        return df
