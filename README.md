# Task 2: Data Visualization and Storytelling

This project turns a Superstore-style sales dataset into a visual story that highlights performance, profitability, and the effect of discounting.

## What is included

- A reproducible Python script that generates a sales dataset.
- Four presentation-ready charts.
- A PDF report with executive summary, storyboard, and interview answers.
- A Tableau or Power BI friendly CSV file for building an interactive dashboard.

## Files

- `generate_story.py` - creates the dataset, charts, and PDF report.
- `data/superstore.csv` - generated sales dataset.
- `outputs/charts/` - exported charts used in the report.
- `outputs/task_2_data_visualization_storytelling_report.pdf` - final visual report.

## How to run

1. Open a terminal in this folder.
2. Run:

```powershell
"d:/data analyst task's/Task 2 Data Visualization and Storytelling/.venv/Scripts/python.exe" generate_story.py
```

3. Open the generated PDF in `outputs/`.

## Story angle

The report tells this story:

1. Sales are growing, but profit is more uneven than revenue.
2. A few regions drive most of the revenue.
3. Technology is the strongest profit category, while Furniture is more vulnerable to discounting.
4. Deep discounts reduce profit and create avoidable losses.

## Suggested dashboard layout for Tableau or Power BI

1. Top row: KPI cards for Sales, Profit, Margin, Orders, and Avg Discount.
2. Middle row: monthly sales/profit trend and sales by region.
3. Bottom row: profit by category and discount impact.
4. Final callout: key recommendation such as reducing high-discount activity in low-margin categories.

## Interview prep

Use the PDF section titled "Interview Questions and Answers" to review the common concepts:

- Why visualization matters.
- When to use pie charts versus bar charts.
- How to avoid misleading visuals.
- Best practices in dashboard design.
- Common tools such as Tableau, Power BI, Excel, and Python.