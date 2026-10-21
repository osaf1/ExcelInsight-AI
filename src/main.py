import pandas as pd

from analysis import (
    calculate_financials,
    get_best_product,
    get_best_city,
    get_worst_product,
    get_profit_per_product,
    get_data_summary
)


# Excel-bestand inladen
df = pd.read_excel("data/sales.xlsx")

print("=== ExcelInsight AI ===")
print()

# Eerste 5 rijen
print("Eerste 5 rijen:")
print(df.head())

# Informatie over de data
print()
print("Informatie over de data:")
df.info()

# Ontbrekende gegevens
print()
print("Ontbrekende gegevens:")
print(df.isnull().sum())


# Financiële analyse
omzet, kosten, winst = calculate_financials(df)

print()
print("Financiële analyse:")
print(f"Totale omzet: €{omzet}")
print(f"Totale kosten: €{kosten}")
print(f"Totale winst: €{winst}")


# Productanalyse
product, product_omzet = get_best_product(df)

print()
print("Productanalyse:")
print(f"Beste product: {product}")
print(f"Omzet van dit product: €{product_omzet}")


# Stadanalyse
stad, stad_omzet = get_best_city(df)

print()
print("Stadanalyse:")
print(f"Beste stad: {stad}")
print(f"Omzet in deze stad: €{stad_omzet}")


# Slechtste product
slechtste_product, laagste_omzet = get_worst_product(df)

print()
print("Slechtste product:")
print(f"Product: {slechtste_product}")
print(f"Omzet: €{laagste_omzet}")


# Winst per product
winst_per_product = get_profit_per_product(df)

print()
print("Winst per product:")
print(winst_per_product)

# Data overzicht
summary = get_data_summary(df)

print()
print("Data overzicht:")
print(summary)