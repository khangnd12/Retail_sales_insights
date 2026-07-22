from pathlib import Path
import numpy as np
import pandas as pd


SEGMENT_RECOMMENDATIONS = {
    "Champions": "Reward and retain these customers with early access, loyalty benefits, and personalized offers.",
    "Loyal Customers": "Encourage repeat purchasing through loyalty rewards, bundles, and relevant cross-selling.",
    "Potential Loyalists": "Use follow-up campaigns and second-purchase incentives to develop these customers into loyal customers.",
    "New Customers": "Provide onboarding messages, product recommendations, and a time-limited second-order offer.",
    "At Risk": "Prioritize reactivation campaigns, especially for historically high-value customers.",
    "Hibernating": "Use low-cost re-engagement campaigns and avoid expensive discounts unless previous value justifies them.",
    "Needs Attention": "Review purchasing patterns and test targeted offers before assigning heavy marketing investment.",
}


def load_customer_sales(file_path: Path) -> pd.DataFrame:
    """Load valid completed sales with known customer IDs."""
    if not file_path.exists():
        raise FileNotFoundError(f"Customer sales file not found: {file_path}")

    df = pd.read_csv(file_path, parse_dates=["invoice_date", "invoice_month"])
    df["customer_id"] = df["customer_id"].astype("Int64")

    return df


def calculate_rfm(customer_sales_df: pd.DataFrame) -> pd.DataFrame:
    """Create customer-level RFM measurements."""
    reference_date = customer_sales_df["invoice_date"].max().normalize() + pd.Timedelta(days=1)

    rfm_df = customer_sales_df.groupby("customer_id", as_index=False).agg(
        last_purchase=("invoice_date", "max"),
        first_purchase=("invoice_date", "min"),
        frequency=("invoice_no", "nunique"),
        monetary=("line_revenue", "sum"),
        units_purchased=("quantity", "sum"),
        unique_products=("stock_code", "nunique"),
        country=("country", "first"),
    )

    rfm_df["recency"] = (reference_date - rfm_df["last_purchase"].dt.normalize()).dt.days
    rfm_df["customer_lifetime_days"] = (
        rfm_df["last_purchase"].dt.normalize() - rfm_df["first_purchase"].dt.normalize()
    ).dt.days

    return rfm_df


def score_rfm(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """Assign quartile scores to RFM measurements."""
    scored_df = rfm_df.copy()

    scored_df["r_score"] = pd.qcut(
        scored_df["recency"].rank(method="first", ascending=True), q=4, labels=[4, 3, 2, 1]
    ).astype(int)

    scored_df["f_score"] = pd.qcut(
        scored_df["frequency"].rank(method="first", ascending=True), q=4, labels=[1, 2, 3, 4]
    ).astype(int)

    scored_df["m_score"] = pd.qcut(
        scored_df["monetary"].rank(method="first", ascending=True), q=4, labels=[1, 2, 3, 4]
    ).astype(int)

    scored_df["rfm_total_score"] = scored_df["r_score"] + scored_df["f_score"] + scored_df["m_score"]
    scored_df["fm_score"] = (scored_df["f_score"] + scored_df["m_score"]) / 2

    return scored_df


def assign_segments(scored_df: pd.DataFrame) -> pd.DataFrame:
    """Assign business-friendly customer segments."""
    segmented_df = scored_df.copy()

    conditions = [
        (segmented_df["r_score"] == 4) & (segmented_df["fm_score"] >= 3.5),
        (segmented_df["r_score"] == 4) & (segmented_df["frequency"] == 1),
        (segmented_df["r_score"] >= 3) & (segmented_df["fm_score"] >= 3),
        (segmented_df["r_score"] >= 3) & (segmented_df["fm_score"] >= 2),
        (segmented_df["r_score"] <= 2) & (segmented_df["fm_score"] >= 3),
        (segmented_df["r_score"] <= 2) & (segmented_df["fm_score"] < 2),
    ]

    labels = [
        "Champions",
        "New Customers",
        "Loyal Customers",
        "Potential Loyalists",
        "At Risk",
        "Hibernating",
    ]

    segmented_df["segment"] = np.select(conditions, labels, default="Needs Attention")
    return segmented_df


def create_segment_summary(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize customer and revenue performance by segment."""
    summary_df = rfm_df.groupby("segment", as_index=False).agg(
        customers=("customer_id", "nunique"),
        revenue=("monetary", "sum"),
        average_recency=("recency", "mean"),
        average_frequency=("frequency", "mean"),
        average_customer_value=("monetary", "mean"),
        median_customer_value=("monetary", "median"),
        average_units=("units_purchased", "mean"),
    )

    summary_df["customer_share_pct"] = (summary_df["customers"] / summary_df["customers"].sum()) * 100
    summary_df["revenue_share_pct"] = (summary_df["revenue"] / summary_df["revenue"].sum()) * 100
    summary_df["recommended_action"] = summary_df["segment"].map(SEGMENT_RECOMMENDATIONS)

    return summary_df.sort_values("revenue", ascending=False).reset_index(drop=True)


def validate_segmentation(rfm_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    """Validate customer segmentation results."""
    assert rfm_df["r_score"].between(1, 4).all()
    assert rfm_df["f_score"].between(1, 4).all()
    assert rfm_df["m_score"].between(1, 4).all()
    assert summary_df["customers"].sum() == len(rfm_df)
    assert np.isclose(summary_df["customer_share_pct"].sum(), 100)
    assert np.isclose(summary_df["revenue_share_pct"].sum(), 100)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    customer_sales_path = project_root / "data" / "processed" / "customer_sales.csv"
    rfm_output_path = project_root / "data" / "processed" / "rfm_customers.csv"
    reports_dir = project_root / "reports" / "tables"

    reports_dir.mkdir(parents=True, exist_ok=True)

    customer_sales_df = load_customer_sales(customer_sales_path)
    rfm_df = calculate_rfm(customer_sales_df)
    rfm_df = score_rfm(rfm_df)
    rfm_df = assign_segments(rfm_df)
    summary_df = create_segment_summary(rfm_df)

    validate_segmentation(rfm_df, summary_df)

    rfm_df.to_csv(rfm_output_path, index=False)
    summary_df.to_csv(reports_dir / "rfm_segment_summary.csv", index=False)

    summary_df[
        [
            "segment",
            "customers",
            "customer_share_pct",
            "revenue",
            "revenue_share_pct",
            "average_recency",
            "average_frequency",
            "average_customer_value",
            "recommended_action",
        ]
    ].to_csv(reports_dir / "segment_recommendations.csv", index=False)

    top_segment = summary_df.iloc[0]

    print("Customer segmentation completed.")
    print(f"Customers: {len(rfm_df):,}")
    print(f"Highest-revenue segment: {top_segment['segment']}")
    print(f"Revenue share: {top_segment['revenue_share_pct']:.2f}%")


if __name__ == "__main__":
    main()