
import pandas as pd


def get_dataset_info(df):
    return {
        "aantal_rijen": len(df),
        "aantal_kolommen": len(df.columns),
        "kolomnamen": list(df.columns),
        "numerieke_kolommen": list(
            df.select_dtypes(include="number").columns
        ),
        "voorbeeld_data": (
            df.head(5)
            .fillna("")
            .astype(str)
            .to_dict(orient="records")
        )
    }


def get_data_summary(df):
    summary = get_dataset_info(df)

    summary["ontbrekende_waarden"] = (
        df.isna().sum().to_dict()
    )

    summary["statistieken"] = (
        df.describe(include="all")
        .fillna("")
        .astype(str)
        .to_dict()
    )

    return summary


def calculate_column(df, column, operation):
    if column not in df.columns:
        return {"error": f"Kolom '{column}' bestaat niet."}

    data = pd.to_numeric(df[column], errors="coerce")

    if data.notna().sum() == 0:
        return {"error": "Deze kolom bevat geen numerieke waarden."}

    operations = {
        "sum": data.sum,
        "mean": data.mean,
        "min": data.min,
        "max": data.max,
        "count": data.count
    }

    if operation not in operations:
        return {"error": "Onbekende berekening."}

    return {
        "kolom": column,
        "berekening": operation,
        "resultaat": float(operations[operation]())
    }


def group_column(df, group_by, value_column, operation="sum"):
    if group_by not in df.columns or value_column not in df.columns:
        return {"error": "Een of meer kolommen bestaan niet."}

    data = df.copy()
    data[value_column] = pd.to_numeric(
        data[value_column], errors="coerce"
    )

    if operation not in ["sum", "mean", "count", "min", "max"]:
        return {"error": "Onbekende berekening."}

    result = data.groupby(
        group_by, dropna=False
    )[value_column].agg(operation)

    return {
        "groepering": group_by,
        "waarde_kolom": value_column,
        "berekening": operation,
        "resultaten": {
            str(k): float(v) if pd.notna(v) else None
            for k, v in result.items()
        }
    }
