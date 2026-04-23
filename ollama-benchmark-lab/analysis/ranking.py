import pandas as pd


def rank_models(csv_path: str):

    df = pd.read_csv(csv_path)

    return df.groupby("model")["score"].mean().sort_values(ascending=False)