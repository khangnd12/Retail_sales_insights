from pathlib import Path
import numpy as np
import pandas as pd


COLUMN_MAPPING = {
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "UnitPrice": "unit_price",
    "CustomerID": "customer_id",
    "Country": "country",
}


def load_data(file_path: Path) -> pd.DataFrame:
    """Load the original retail Excel dataset."""
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    return pd.read_excel(file_path)


def clean_transactions(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the retail transaction data."""
    df = raw_df.copy()
    df = df.rename(columns=COLUMN_MAPPING)

    text_columns = ["invoice_no", "stock_code", "description", "country"]
    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["customer_id"] = df["customer_id"].astype("Int64")

    essential_columns = [
        "invoice_no", "stock_code", "description",
        "quantity", "invoice_date", "unit_price", "country"
    ]

    df = df.dropna(subset=essential_columns).copy()
    df = df[~df["description"].eq("")].copy()
    df = df.drop_duplicates().copy()

    df["is_cancelled"] = df["invoice_no"].str.startswith("C", na=False)

    conditions = [
        df["is_cancelled"],
        df["quantity"] < 0,
        df["unit_price"] <= 0,
    ]
    categories = ["cancelled", "return", "invalid_price"]
    
    df["transaction_type"] = np.select(conditions, categories, default="sale")
    df["line_revenue"] = df["quantity"] * df["unit_price"]

    df["invoice_month"] = df["invoice_date"].dt.to_period("M").dt.to_timestamp()
    df["invoice_year"] = df["invoice_date"].dt.year
    df["invoice_quarter"] = df["invoice_date"].dt.quarter
    df["invoice_weekday"] = df["invoice_date"].dt.day_name()
    df["invoice_hour"] = df["invoice_date"].dt.hour
    df["invoice_day"] = df["invoice_date"].dt.date

    return df


def get_valid_sales(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Return valid completed sales."""
    valid_sales_mask = (
        (transactions_df["quantity"] > 0)
        & (transactions_df["unit_price"] > 0)
        & (~transactions_df["is_cancelled"])
    )
    return transactions_df[valid_sales_mask].copy()


def get_customer_sales(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Return valid sales with known customer IDs."""
    return sales_df.dropna(subset=["customer_id"]).copy()


def validate_data(
    transactions_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    customer_sales_df: pd.DataFrame,
) -> None:
    """Validate the processed datasets."""
    assert transactions_df.duplicated().sum() == 0
    assert transactions_df.columns.is_unique

    assert (sales_df["quantity"] > 0).all()
    assert (sales_df["unit_price"] > 0).all()
    assert (~sales_df["is_cancelled"]).all()
    assert (sales_df["line_revenue"] > 0).all()

    assert customer_sales_df["customer_id"].notna().all()


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    
    raw_path = project_root / "data" / "raw" / "Online Retail.xlsx"
    processed_dir = project_root / "data" / "processed"
    report_dir = project_root / "reports" / "tables"

    processed_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    raw_df = load_data(raw_path)

    transactions_df = clean_transactions(raw_df)
    sales_df = get_valid_sales(transactions_df)
    customer_sales_df = get_customer_sales(sales_df)

    validate_data(transactions_df, sales_df, customer_sales_df)

    transactions_df.to_csv(processed_dir / "clean_transactions.csv", index=False)
    sales_df.to_csv(processed_dir / "valid_sales.csv", index=False)
    customer_sales_df.to_csv(processed_dir / "customer_sales.csv", index=False)

    summary_df = pd.DataFrame({
        "dataset": [
            "Raw transactions",
            "Clean transactions",
            "Valid completed sales",
            "Customer sales",
        ],
        "row_count": [
            len(raw_df),
            len(transactions_df),
            len(sales_df),
            len(customer_sales_df),
        ],
    })

    summary_df["percentage_of_raw"] = (summary_df["row_count"] / len(raw_df) * 100).round(2)
    summary_df.to_csv(report_dir / "cleaning_summary.csv", index=False)

    print("Cleaning completed successfully.")
    print(f"Raw rows: {len(raw_df):,}")
    print(f"Clean transaction rows: {len(transactions_df):,}")
    print(f"Valid sales rows: {len(sales_df):,}")
    print(f"Customer sales rows: {len(customer_sales_df):,}")


if __name__ == "__main__":
    main()