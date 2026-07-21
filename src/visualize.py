from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter

sns.set_theme(style="whitegrid")


def format_currency_axis(value: float, position: int) -> str:
    """Format currency values for chart axes."""
    if abs(value) >= 1_000_000:
        return f"£{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"£{value / 1_000:.0f}K"
    return f"£{value:.0f}"


def format_number_axis(value: float, position: int) -> str:
    """Format large whole numbers for chart axes."""
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:.0f}"


def save_figure(fig: plt.Figure, output_path: Path) -> None:
    """Save and close a Matplotlib figure."""
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_monthly_revenue(monthly_df: pd.DataFrame, output_path: Path) -> None:
    """Create the monthly gross revenue chart."""
    plot_df = monthly_df.sort_values("invoice_month").copy()

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.lineplot(data=plot_df, x="invoice_month", y="revenue", marker="o", ax=ax)

    ax.set_title("Monthly Gross Revenue")
    ax.set_xlabel("Invoice Month")
    ax.set_ylabel("Gross Revenue")
    ax.yaxis.set_major_formatter(FuncFormatter(format_currency_axis))
    ax.tick_params(axis="x", rotation=45)

    save_figure(fig, output_path)


def plot_monthly_orders(monthly_df: pd.DataFrame, output_path: Path) -> None:
    """Create the monthly order-volume chart."""
    plot_df = monthly_df.sort_values("invoice_month").copy()

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.lineplot(data=plot_df, x="invoice_month", y="orders", marker="o", ax=ax)

    ax.set_title("Monthly Completed Orders")
    ax.set_xlabel("Invoice Month")
    ax.set_ylabel("Number of Orders")
    ax.yaxis.set_major_formatter(FuncFormatter(format_number_axis))
    ax.tick_params(axis="x", rotation=45)

    save_figure(fig, output_path)


def plot_top_countries(country_df: pd.DataFrame, output_path: Path) -> None:
    """Create the top-country revenue chart."""
    plot_df = country_df.nlargest(10, "revenue").sort_values("revenue").copy()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=plot_df, x="revenue", y="country", ax=ax)

    ax.set_title("Top 10 Countries by Gross Revenue")
    ax.set_xlabel("Gross Revenue")
    ax.set_ylabel("Country")
    ax.xaxis.set_major_formatter(FuncFormatter(format_currency_axis))

    save_figure(fig, output_path)


def plot_top_products(product_df: pd.DataFrame, output_path: Path) -> None:
    """Create the top-product revenue chart."""
    plot_df = product_df.nlargest(10, "revenue").copy()
    plot_df["product_label"] = plot_df["description"].astype("string").str.title().str.slice(0, 40)
    plot_df = plot_df.sort_values("revenue")

    fig, ax = plt.subplots(figsize=(11, 7))
    sns.barplot(data=plot_df, x="revenue", y="product_label", ax=ax)

    ax.set_title("Top 10 Products by Gross Revenue")
    ax.set_xlabel("Gross Revenue")
    ax.set_ylabel("Product")
    ax.xaxis.set_major_formatter(FuncFormatter(format_currency_axis))

    save_figure(fig, output_path)


def plot_order_distribution(order_df: pd.DataFrame, output_path: Path) -> None:
    """Create the completed order-value histogram."""
    upper_limit = order_df["order_revenue"].quantile(0.99)
    plot_df = order_df[order_df["order_revenue"] <= upper_limit].copy()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(data=plot_df, x="order_revenue", bins=40, ax=ax)

    ax.set_title("Distribution of Completed Order Values")
    ax.set_xlabel("Order Revenue")
    ax.set_ylabel("Number of Orders")
    ax.xaxis.set_major_formatter(FuncFormatter(format_currency_axis))

    save_figure(fig, output_path)


def plot_customer_distribution(customer_df: pd.DataFrame, output_path: Path) -> None:
    """Create the customer revenue histogram."""
    upper_limit = customer_df["revenue"].quantile(0.99)
    plot_df = customer_df[customer_df["revenue"] <= upper_limit].copy()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(data=plot_df, x="revenue", bins=40, ax=ax)

    ax.set_title("Distribution of Revenue per Known Customer")
    ax.set_xlabel("Customer Revenue")
    ax.set_ylabel("Number of Customers")
    ax.xaxis.set_major_formatter(FuncFormatter(format_currency_axis))

    save_figure(fig, output_path)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    tables_dir = project_root / "reports" / "tables"
    figures_dir = project_root / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    monthly_df = pd.read_csv(tables_dir / "monthly_kpis.csv", parse_dates=["invoice_month"])
    country_df = pd.read_csv(tables_dir / "country_kpis.csv")
    product_df = pd.read_csv(tables_dir / "product_kpis.csv")
    customer_df = pd.read_csv(tables_dir / "customer_kpis.csv")
    order_df = pd.read_csv(tables_dir / "order_kpis.csv", parse_dates=["order_date"])

    plot_monthly_revenue(monthly_df, figures_dir / "monthly_revenue.png")
    plot_monthly_orders(monthly_df, figures_dir / "monthly_orders.png")
    plot_top_countries(country_df, figures_dir / "top_countries_revenue.png")
    plot_top_products(product_df, figures_dir / "top_products_revenue.png")
    plot_order_distribution(order_df, figures_dir / "order_value_distribution.png")
    plot_customer_distribution(customer_df, figures_dir / "customer_revenue_distribution.png")

    print("Visualizations created successfully.")


if __name__ == "__main__":
    main()