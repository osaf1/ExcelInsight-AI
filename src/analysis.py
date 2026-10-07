import pandas as pd


def calculate_financials(df):
    totale_omzet = df["Omzet"].sum()
    totale_kosten = df["Kosten"].sum()
    totale_winst = totale_omzet - totale_kosten

    return totale_omzet, totale_kosten, totale_winst


def get_best_product(df):
    product_omzet = df.groupby("Product")["Omzet"].sum()

    beste_product = product_omzet.idxmax()
    hoogste_omzet = product_omzet.max()

    return beste_product, hoogste_omzet


def get_best_city(df):
    stad_omzet = df.groupby("Stad")["Omzet"].sum()

    beste_stad = stad_omzet.idxmax()
    hoogste_omzet = stad_omzet.max()

    return beste_stad, hoogste_omzet


def get_worst_product(df):
    product_omzet = df.groupby("Product")["Omzet"].sum()

    slechtste_product = product_omzet.idxmin()
    laagste_omzet = product_omzet.min()

    return slechtste_product, laagste_omzet


def get_profit_per_product(df):
    product_winst = df.groupby("Product").apply(
        lambda x: x["Omzet"].sum() - x["Kosten"].sum(),
        include_groups=False
    )

    return product_winst