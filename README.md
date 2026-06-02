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

## Live viewer on GitHub

You can preview the report and charts directly from this repository:

- Viewer page (in the repo): https://github.com/yandrapallimansha-mic-23/task-2-data-storytelling-da/blob/main/outputs/viewer.html
- PDF report: https://github.com/yandrapallimansha-mic-23/task-2-data-storytelling-da/blob/main/outputs/task_2_data_visualization_storytelling_report.pdf

If you want this viewer served as a GitHub Pages site (clean URL), I can enable Pages for this repo — I will need a GitHub Personal Access Token (PAT) with `repo` and `admin:repo_hook` (or `repo` scope) to make that change for you. If you prefer, follow these steps locally:

1. In the repository on GitHub, go to Settings → Pages.
2. Under "Source", choose the `main` branch and `/outputs` folder (or the `root`) and save.
3. After a few minutes the site will be available at `https://<username>.github.io/<repo>/outputs/viewer.html` (or at the Pages root depending on configuration).

Tell me if you want me to enable GitHub Pages (paste a PAT), or I can provide the exact steps you can run locally.

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