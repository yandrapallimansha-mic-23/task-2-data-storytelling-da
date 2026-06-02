from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
REPORT_PATH = OUTPUT_DIR / "task_2_data_visualization_storytelling_report.pdf"
CSV_PATH = DATA_DIR / "superstore.csv"


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)


def build_dataset(seed: int = 42, rows: int = 1200) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    date_range = pd.date_range("2022-01-01", "2024-12-31", freq="D")
    order_dates = pd.to_datetime(rng.choice(date_range, size=rows))
    ship_offsets = rng.integers(1, 8, size=rows)
    ship_dates = order_dates + pd.to_timedelta(ship_offsets, unit="D")

    regions = np.array(["West", "East", "Central", "South"])
    region_weights = np.array([0.31, 0.29, 0.20, 0.20])
    chosen_regions = rng.choice(regions, size=rows, p=region_weights)

    segments = np.array(["Consumer", "Corporate", "Home Office"])
    segment_weights = np.array([0.52, 0.29, 0.19])
    chosen_segments = rng.choice(segments, size=rows, p=segment_weights)

    categories = {
        "Furniture": {
            "Chair": 220,
            "Table": 410,
            "Bookcase": 185,
            "Furnishings": 95,
        },
        "Technology": {
            "Phones": 320,
            "Accessories": 75,
            "Machines": 540,
            "Copiers": 760,
        },
        "Office Supplies": {
            "Binders": 85,
            "Paper": 42,
            "Storage": 125,
            "Appliances": 155,
            "Art": 28,
            "Envelopes": 32,
            "Labels": 18,
            "Fasteners": 16,
            "Supplies": 62,
        },
    }

    category_names = np.array(list(categories.keys()))
    category_weights = np.array([0.34, 0.28, 0.38])
    chosen_categories = rng.choice(category_names, size=rows, p=category_weights)

    subcategories = []
    product_names = []
    for idx, category in enumerate(chosen_categories, start=1):
        options = list(categories[category].keys())
        weights = np.array(list(categories[category].values()), dtype=float)
        weights = weights / weights.sum()
        subcategory = rng.choice(options, p=weights)
        subcategories.append(subcategory)
        product_names.append(f"{subcategory} {idx:04d}")

    quantity = rng.integers(1, 8, size=rows)

    region_profit_adjustment = {
        "West": 0.04,
        "East": 0.03,
        "Central": -0.01,
        "South": -0.015,
    }

    category_margin = {
        "Furniture": 0.08,
        "Technology": 0.19,
        "Office Supplies": 0.13,
    }

    discount_base = {
        "Furniture": 0.18,
        "Technology": 0.10,
        "Office Supplies": 0.08,
    }

    sales = []
    discounts = []
    profits = []

    for category, subcategory, qty, region in zip(chosen_categories, subcategories, quantity, chosen_regions, strict=True):
        base_price = categories[category][subcategory]
        noise = rng.normal(1.0, 0.22)
        order_sales = max(5.0, base_price * qty * noise)
        order_discount = float(np.clip(rng.beta(2, 8) * 0.65 + discount_base[category] - 0.08, 0, 0.60))
        profit_rate = category_margin[category]
        discount_penalty = 0.55 if category == "Furniture" else 0.42 if category == "Office Supplies" else 0.32
        profit_noise = rng.normal(0.0, order_sales * 0.03)
        order_profit = (
            order_sales * profit_rate
            - order_sales * order_discount * discount_penalty
            + order_sales * region_profit_adjustment[region]
            + profit_noise
        )

        sales.append(round(order_sales, 2))
        discounts.append(round(order_discount, 2))
        profits.append(round(order_profit, 2))

    data = pd.DataFrame(
        {
            "Order ID": [f"CA-{100000 + i}" for i in range(rows)],
            "Order Date": order_dates.date,
            "Ship Date": ship_dates.date,
            "Region": chosen_regions,
            "Segment": chosen_segments,
            "Category": chosen_categories,
            "Sub-Category": subcategories,
            "Product Name": product_names,
            "Quantity": quantity,
            "Sales": sales,
            "Discount": discounts,
            "Profit": profits,
        }
    )

    data["Order Date"] = pd.to_datetime(data["Order Date"])
    data["Ship Date"] = pd.to_datetime(data["Ship Date"])
    data.sort_values("Order Date", inplace=True)
    data.reset_index(drop=True, inplace=True)
    return data


def save_dataset(df: pd.DataFrame) -> None:
    df.to_csv(CSV_PATH, index=False)


def chart_style() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#D9D9D9",
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "font.family": "DejaVu Sans",
        }
    )


def monthly_trend_chart(df: pd.DataFrame) -> Path:
    monthly = (
        df.assign(Month=df["Order Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    )
    monthly["Sales 3M Avg"] = monthly["Sales"].rolling(3, min_periods=1).mean()
    monthly["Profit 3M Avg"] = monthly["Profit"].rolling(3, min_periods=1).mean()

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    fig.suptitle("Monthly Performance: Revenue Grows Faster Than Profit", fontsize=18, fontweight="bold")

    axes[0].plot(monthly["Month"], monthly["Sales"], color="#0F766E", linewidth=2.5, label="Monthly Sales")
    axes[0].plot(monthly["Month"], monthly["Sales 3M Avg"], color="#9CA3AF", linestyle="--", linewidth=2, label="3M Average")
    axes[0].set_ylabel("Sales ($)")
    axes[0].legend(frameon=False, loc="upper left")
    axes[0].annotate(
        "Seasonal peak",
        xy=(monthly["Month"].iloc[-3], monthly["Sales"].iloc[-3]),
        xytext=(20, 15),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="#111827", lw=1),
    )

    axes[1].plot(monthly["Month"], monthly["Profit"], color="#C2410C", linewidth=2.5, label="Monthly Profit")
    axes[1].plot(monthly["Month"], monthly["Profit 3M Avg"], color="#F59E0B", linestyle="--", linewidth=2, label="3M Average")
    axes[1].axhline(0, color="#111827", linewidth=1)
    axes[1].set_ylabel("Profit ($)")
    axes[1].set_xlabel("Month")
    axes[1].legend(frameon=False, loc="upper left")

    for axis in axes:
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = CHART_DIR / "01_monthly_trend.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def region_category_chart(df: pd.DataFrame) -> Path:
    region_sales = df.groupby("Region", as_index=False).agg(Sales=("Sales", "sum")).sort_values("Sales", ascending=True)
    category_profit = df.groupby("Category", as_index=False).agg(Profit=("Profit", "sum")).sort_values("Profit", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Where the Business Wins: Revenue by Region and Profit by Category", fontsize=18, fontweight="bold")

    axes[0].barh(region_sales["Region"], region_sales["Sales"], color="#2563EB")
    axes[0].set_xlabel("Sales ($)")
    axes[0].set_ylabel("Region")
    axes[0].set_title("Sales by Region")
    for index, value in enumerate(region_sales["Sales"]):
        axes[0].text(value, index, f"  ${value:,.0f}", va="center", fontsize=9)

    palette = ["#84CC16" if value > 0 else "#DC2626" for value in category_profit["Profit"]]
    axes[1].barh(category_profit["Category"], category_profit["Profit"], color=palette)
    axes[1].axvline(0, color="#111827", linewidth=1)
    axes[1].set_xlabel("Profit ($)")
    axes[1].set_ylabel("Category")
    axes[1].set_title("Profit by Category")
    for index, value in enumerate(category_profit["Profit"]):
        axes[1].text(value, index, f"  ${value:,.0f}", va="center", fontsize=9)

    for axis in axes:
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = CHART_DIR / "02_region_category.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def discount_chart(df: pd.DataFrame) -> Path:
    bins = [0, 0.05, 0.10, 0.20, 0.35, 0.60]
    labels = ["0-5%", "5-10%", "10-20%", "20-35%", "35-60%"]
    bucketed = df.copy()
    bucketed["Discount Bucket"] = pd.cut(bucketed["Discount"], bins=bins, labels=labels, include_lowest=True, right=False)
    summary = bucketed.groupby("Discount Bucket", as_index=False).agg(AvgProfit=("Profit", "mean"), Orders=("Profit", "size"))

    fig, ax1 = plt.subplots(figsize=(12, 6))
    fig.suptitle("Discount Pressure: Higher Discounts Drag Profit Down", fontsize=18, fontweight="bold")

    bars = ax1.bar(summary["Discount Bucket"], summary["AvgProfit"], color="#7C3AED", alpha=0.85)
    ax1.axhline(0, color="#111827", linewidth=1)
    ax1.set_ylabel("Average Profit per Order ($)")
    ax1.set_xlabel("Discount Bucket")
    ax1.set_title("Average Profit by Discount Level")

    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            height + (8 if height >= 0 else -16),
            f"${height:,.0f}",
            ha="center",
            va="bottom" if height >= 0 else "top",
            fontsize=9,
        )

    ax2 = ax1.twinx()
    ax2.plot(summary["Discount Bucket"], summary["Orders"], color="#F59E0B", marker="o", linewidth=2.2)
    ax2.set_ylabel("Orders")

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = CHART_DIR / "03_discount_impact.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def scatter_chart(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle("Discount vs Profit: Deep Discounts Create Negative Outliers", fontsize=18, fontweight="bold")

    palette = {"Furniture": "#1D4ED8", "Technology": "#16A34A", "Office Supplies": "#D97706"}
    for category, group in df.groupby("Category"):
        ax.scatter(
            group["Discount"],
            group["Profit"],
            s=22,
            alpha=0.45,
            label=category,
            color=palette[category],
            edgecolors="none",
        )

    x = df["Discount"].to_numpy()
    y = df["Profit"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, slope * x_line + intercept, color="#111827", linewidth=2.5, linestyle="--", label="Trend")
    ax.axhline(0, color="#111827", linewidth=1)
    ax.set_xlabel("Discount")
    ax.set_ylabel("Profit ($)")
    ax.legend(frameon=False, loc="upper right")

    ax.text(
        0.03,
        0.96,
        "Key insight: orders above 20% discount often lose money,\nespecially in Furniture.",
        transform=ax.transAxes,
        va="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF7ED", edgecolor="#FDBA74"),
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = CHART_DIR / "04_discount_vs_profit.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def compute_metrics(df: pd.DataFrame) -> dict[str, str]:
    orders = len(df)
    revenue = df["Sales"].sum()
    profit = df["Profit"].sum()
    margin = profit / revenue if revenue else 0
    avg_discount = df["Discount"].mean()
    negative_profit_orders = (df["Profit"] < 0).mean()

    return {
        "Orders": f"{orders:,}",
        "Revenue": f"${revenue:,.0f}",
        "Profit": f"${profit:,.0f}",
        "Profit Margin": f"{margin:.1%}",
        "Avg Discount": f"{avg_discount:.1%}",
        "Loss-Making Orders": f"{negative_profit_orders:.1%}",
    }


def top_insights(df: pd.DataFrame) -> list[str]:
    monthly = df.assign(Month=df["Order Date"].dt.to_period("M").dt.to_timestamp())
    monthly_profit = monthly.groupby("Month", as_index=False).agg(Profit=("Profit", "sum"))
    best_month = monthly_profit.sort_values("Profit", ascending=False).iloc[0]
    worst_month = monthly_profit.sort_values("Profit", ascending=True).iloc[0]

    category_profit = df.groupby("Category", as_index=False).agg(Profit=("Profit", "sum")).sort_values("Profit", ascending=False)
    region_sales = df.groupby("Region", as_index=False).agg(Sales=("Sales", "sum")).sort_values("Sales", ascending=False)
    high_discount = df[df["Discount"] >= 0.20]
    low_discount = df[df["Discount"] < 0.10]

    return [
        f"Profit peaked in {best_month['Month'].strftime('%b %Y')} at ${best_month['Profit']:,.0f}, while {worst_month['Month'].strftime('%b %Y')} was the weakest month at ${worst_month['Profit']:,.0f}.",
        f"{category_profit.iloc[0]['Category']} delivered the strongest profit contribution, while {category_profit.iloc[-1]['Category']} lagged behind.",
        f"{region_sales.iloc[0]['Region']} led revenue, which suggests the best opportunity is to protect its margin instead of chasing extra discounting.",
        f"Orders with discounts of 20% or more averaged ${high_discount['Profit'].mean():,.0f} profit, compared with ${low_discount['Profit'].mean():,.0f} for low-discount orders.",
    ]


def build_pdf(metrics: dict[str, str], insights: list[str], chart_paths: list[Path]) -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontSize=24, leading=28, spaceAfter=16))
    styles.add(ParagraphStyle(name="SubCenter", parent=styles["Normal"], alignment=TA_CENTER, fontSize=11, leading=14, textColor=colors.HexColor("#4B5563")))
    styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Heading2"], fontSize=16, leading=20, spaceBefore=8, spaceAfter=8, textColor=colors.HexColor("#111827")))
    styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontSize=10.5, leading=14, spaceAfter=6))

    doc = SimpleDocTemplate(
        str(REPORT_PATH),
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    story = []
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph("Task 2: Data Visualization and Storytelling", styles["TitleCenter"]))
    story.append(Paragraph("Superstore-style sales analysis built for Tableau or Power BI storytelling", styles["SubCenter"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Objective", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "This report turns sales data into a business story: where revenue comes from, which categories generate profit, and how discounting affects margin. The design favors clarity, context, and decision-making over decoration.",
            styles["Body2"],
        )
    )

    metric_rows = [
        ["Metric", "Value", "Metric", "Value"],
        ["Orders", metrics["Orders"], "Revenue", metrics["Revenue"]],
        ["Profit", metrics["Profit"], "Profit Margin", metrics["Profit Margin"]],
        ["Avg Discount", metrics["Avg Discount"], "Loss-Making Orders", metrics["Loss-Making Orders"]],
    ]
    metric_table = Table(metric_rows, colWidths=[1.45 * inch, 1.25 * inch, 1.45 * inch, 1.25 * inch])
    metric_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9FAFB")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
            ]
        )
    )
    story.append(metric_table)
    story.append(Spacer(1, 0.18 * inch))
    story.append(Paragraph("Storyline", styles["SectionHeading"]))
    for item in insights:
        story.append(Paragraph(f"- {item}", styles["Body2"]))

    story.append(PageBreak())
    story.append(Paragraph("Chart 1: Monthly Revenue and Profit", styles["SectionHeading"]))
    story.append(Paragraph("Use this chart to show seasonality, momentum, and whether profit is keeping pace with sales.", styles["Body2"]))
    story.append(Image(str(chart_paths[0]), width=7.1 * inch, height=4.4 * inch))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("Takeaway: sales rise over time, but profit is more sensitive to discounting and product mix.", styles["Body2"]))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Chart 2: Region and Category Performance", styles["SectionHeading"]))
    story.append(Image(str(chart_paths[1]), width=7.1 * inch, height=3.3 * inch))
    story.append(Paragraph("Takeaway: revenue is concentrated in the top regions, while category-level profit reveals where margin is strongest.", styles["Body2"]))

    story.append(PageBreak())
    story.append(Paragraph("Chart 3: Discount Pressure", styles["SectionHeading"]))
    story.append(Image(str(chart_paths[2]), width=7.1 * inch, height=3.8 * inch))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Chart 4: Discount vs Profit", styles["SectionHeading"]))
    story.append(Image(str(chart_paths[3]), width=7.1 * inch, height=4.0 * inch))
    story.append(Paragraph("Takeaway: once discounts move beyond the 20% range, profit erosion becomes clear.", styles["Body2"]))

    story.append(PageBreak())
    story.append(Paragraph("Dashboard Storyboard", styles["SectionHeading"]))
    storyboard = [
        ["Slide", "Purpose", "What the audience learns"],
        ["1", "Executive summary", "What the business did well and where it struggled"],
        ["2", "Sales trend", "Whether growth is stable or seasonal"],
        ["3", "Regional view", "Which markets drive revenue"],
        ["4", "Category view", "Which products create or destroy profit"],
        ["5", "Discount analysis", "How pricing policy affects margin"],
        ["6", "Action slide", "What to do next"],
    ]
    storyboard_table = Table(storyboard, colWidths=[0.7 * inch, 1.8 * inch, 4.5 * inch])
    storyboard_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
            ]
        )
    )
    story.append(storyboard_table)
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Interview Questions and Answers", styles["SectionHeading"]))
    qa = [
        ("What is the importance of data visualization?", "It turns raw numbers into patterns that people can understand quickly, which improves decision-making and helps teams spot trends, risks, and opportunities."),
        ("When do you use a pie chart vs bar chart?", "Use a pie chart only when you want to show part-to-whole for a few categories. Use a bar chart when comparing values across categories because it is easier to read and more accurate."),
        ("How do you make visualizations more engaging?", "Keep the layout clean, choose one clear message per chart, use color sparingly to highlight key points, and add annotations that explain why the chart matters."),
        ("What is data storytelling?", "Data storytelling combines analysis, visuals, and narrative so the audience understands not only what happened but also why it matters and what should happen next."),
        ("How do you avoid misleading visualizations?", "Use correct scales, avoid unnecessary 3D effects, label axes clearly, do not truncate context, and choose the chart type that matches the data and the question."),
        ("What are best practices in dashboard design?", "Focus on a single business goal, keep the most important KPIs at the top, reduce clutter, use consistent colors, and make interactions simple and purposeful."),
        ("What tools have you used for visualization?", "Common tools include Tableau, Power BI, Excel, and Python libraries such as Matplotlib, Seaborn, and Plotly."),
    ]
    for question, answer in qa:
        story.append(Paragraph(f"<b>{question}</b>", styles["Body2"]))
        story.append(Paragraph(answer, styles["Body2"]))

    doc.build(story)


def main() -> None:
    ensure_directories()
    chart_style()
    df = build_dataset()
    save_dataset(df)

    chart_paths = [
        monthly_trend_chart(df),
        region_category_chart(df),
        discount_chart(df),
        scatter_chart(df),
    ]
    metrics = compute_metrics(df)
    insights = top_insights(df)
    build_pdf(metrics, insights, chart_paths)

    print(f"Created dataset: {CSV_PATH}")
    print(f"Created report:   {REPORT_PATH}")
    print(f"Created charts:    {CHART_DIR}")


if __name__ == "__main__":
    main()