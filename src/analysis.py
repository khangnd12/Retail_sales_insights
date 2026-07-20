from pathlib import Path
import pandas as pd


def load_processed_data(file_path: Path) -> pd.DataFrame:
    """Load a processed retail CSV file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Processed file not found: {file_path}")

    date_columns = ["invoice_date", "invoice_month"]
    df = pd.read_csv(file_path, parse_dates=date_columns)

    if "customer_id" in df.columns:
        df["customer_id"] = df["customer_id"].astype("Int64")

    return df


def calculate_overall_kpis(
    transactions_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    customer_sales_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate the main business KPIs."""
    gross_revenue = sales_df["line_revenue"].sum()
    completed_orders = sales_df["invoice_no"].nunique()
    units_sold = sales_df["quantity"].sum()
    unique_customers = customer_sales_df["customer_id"].nunique()

    average_order_value = gross_revenue / completed_orders
    average_items_per_order = units_sold / completed_orders
    known_customer_revenue = customer_sales_df["line_revenue"].sum()
    average_revenue_per_customer = known_customer_revenue / unique_customers
    
    all_invoices = transactions_df["invoice_no"].nunique()
    cancelled_invoices = transactions_df.loc[
        transactions_df["is_cancelled"], "invoice_no"
    ].nunique()
    cancellation_rate = (cancelled_invoices / all_invoices) * 100

    return pd.DataFrame({
        "metric": [
            "Gross revenue",
            "Completed orders",
            "Units sold",
            "Unique known customers",
            "Average order value",
            "Average items per order",
            "Average revenue per known customer",
            "Cancelled invoices",
            "Cancellation rate (%)",
        ],
        "value": [
            gross_revenue,
            completed_orders,
            units_sold,
            unique_customers,
            average_order_value,
            average_items_per_order,
            average_revenue_per_customer,
            cancelled_invoices,
            cancellation_rate,
        ],
    })


def calculate_order_kpis(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Create one row per completed order."""
    return sales_df.groupby("invoice_no", as_index=False).agg(
        order_revenue=("line_revenue", "sum"),
        units=("quantity", "sum"),
        product_lines=("stock_code", "size"),
        unique_products=("stock_code", "nunique"),
        customer_id=("customer_id", "first"),
        country=("country", "first"),
        order_date=("invoice_date", "min"),
    )


def calculate_monthly_kpis(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly sales KPIs."""
    monthly_df = (
        sales_df.groupby("invoice_month", as_index=False)
        .agg(
            revenue=("line_revenue", "sum"),
            orders=("invoice_no", "nunique"),
            customers=("customer_id", "nunique"),
            units_sold=("quantity", "sum"),
        )
        .sort_values("invoice_month")
        .reset_index(drop=True)
    )

    monthly_df["average_order_value"] = monthly_df["revenue"] / monthly_df["orders"]
    monthly_df["items_per_order"] = monthly_df["units_sold"] / monthly_df["orders"]
    monthly_df["revenue_growth_pct"] = monthly_df["revenue"].pct_change().mul(100)

    return monthly_df


def calculate_country_kpis(
    sales_df: pd.DataFrame, order_df: pd.DataFrame
) -> pd.DataFrame:
    """Calculate country-level performance."""
    country_df = sales_df.groupby("country", as_index=False).agg(
        revenue=("line_revenue", "sum"),
        orders=("invoice_no", "nunique"),
        customers=("customer_id", "nunique"),
        units_sold=("quantity", "sum"),
    )

    order_metrics = order_df.groupby("country", as_index=False).agg(
        average_order_value=("order_revenue", "mean"),
        median_order_value=("order_revenue", "median"),
    )

    country_df = country_df.merge(order_metrics, on="country", how="left")
    country_df["revenue_share_pct"] = (country_df["revenue"] / country_df["revenue"].sum()) * 100

    return country_df.sort_values("revenue", ascending=False).reset_index(drop=True)


def calculate_product_kpis(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate product-level performance."""
    product_df = sales_df.groupby(["stock_code", "description"], as_index=False).agg(
        revenue=("line_revenue", "sum"),
        units_sold=("quantity", "sum"),
        orders=("invoice_no", "nunique"),
        customers=("customer_id", "nunique"),
    )

    product_df["average_selling_price"] = product_df["revenue"] / product_df["units_sold"]
    product_df["revenue_share_pct"] = (product_df["revenue"] / product_df["revenue"].sum()) * 100

    return product_df.sort_values("revenue", ascending=False).reset_index(drop=True)


def calculate_customer_kpis(customer_sales_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate customer-level performance."""
    customer_df = customer_sales_df.groupby("customer_id", as_index=False).agg(
        revenue=("line_revenue", "sum"),
        orders=("invoice_no", "nunique"),
        units_purchased=("quantity", "sum"),
        unique_products=("stock_code", "nunique"),
        first_purchase=("invoice_date", "min"),
        last_purchase=("invoice_date", "max"),
        country=("country", "first"),
    )

    customer_df["average_order_value"] = customer_df["revenue"] / customer_df["orders"]
    customer_df["revenue_share_pct"] = (customer_df["revenue"] / customer_df["revenue"].sum()) * 100

    return customer_df.sort_values("revenue", ascending=False).reset_index(drop=True)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    processed_dir = project_root / "data" / "processed"
    reports_dir = project_root / "reports" / "tables"

    reports_dir.mkdir(parents=True, exist_ok=True)

    transactions_df = load_processed_data(processed_dir / "clean_transactions.csv")
    sales_df = load_processed_data(processed_dir / "valid_sales.csv")
    customer_sales_df = load_processed_data(processed_dir / "customer_sales.csv")

    order_df = calculate_order_kpis(sales_df)
    overall_df = calculate_overall_kpis(transactions_df, sales_df, customer_sales_df)
    monthly_df = calculate_monthly_kpis(sales_df)
    country_df = calculate_country_kpis(sales_df, order_df)
    product_df = calculate_product_kpis(sales_df)
    customer_df = calculate_customer_kpis(customer_sales_df)

    outputs = {
        "overall_kpis.csv": overall_df,
        "monthly_kpis.csv": monthly_df,
        "country_kpis.csv": country_df,
        "product_kpis.csv": product_df,
        "customer_kpis.csv": customer_df,
        "order_kpis.csv": order_df,
    }

    for filename, dataframe in outputs.items():
        dataframe.to_csv(reports_dir / filename, index=False)

    print("Business analysis completed.")
    print(f"Gross revenue: £{sales_df['line_revenue'].sum():,.2f}")
    print(f"Completed orders: {sales_df['invoice_no'].nunique():,}")


if __name__ == "__main__":
    main()