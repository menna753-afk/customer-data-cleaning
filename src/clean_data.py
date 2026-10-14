from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "marketing_campaign.csv"
OUT_PATH = ROOT / "data" / "processed" / "marketing_campaign_clean.csv"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates(subset=df.columns.drop("ID"))

    df["Marital_Status"] = df["Marital_Status"].replace({"Alone": "Single"})
    df = df[~df["Marital_Status"].isin(["Absurd", "YOLO"])]

    df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"])

    df = df[df["Year_Birth"] >= 1920]
    df = df[(df["Income"] < 200000) | (df["Income"].isna())]

    df["Income"] = df["Income"].fillna(df["Income"].median())

    df = df.drop(columns=["Z_CostContact", "Z_Revenue"])

    current_year = df["Dt_Customer"].dt.year.max()
    df["Age"] = current_year - df["Year_Birth"]

    mnt_cols = [c for c in df.columns if c.startswith("Mnt")]
    df["Total_Spent"] = df[mnt_cols].sum(axis=1)

    purchase_cols = ["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
    df["Total_Purchases"] = df[purchase_cols].sum(axis=1)

    df["Total_Children"] = df["Kidhome"] + df["Teenhome"]
    df["Customer_Since_Days"] = (df["Dt_Customer"].max() - df["Dt_Customer"]).dt.days

    return df.reset_index(drop=True)


def main() -> None:
    raw = pd.read_csv(RAW_PATH, sep=";")
    cleaned = clean(raw)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUT_PATH, index=False)
    print(f"Raw shape:     {raw.shape}")
    print(f"Cleaned shape: {cleaned.shape}")
    print(f"Saved to:      {OUT_PATH}")


if __name__ == "__main__":
    main()
