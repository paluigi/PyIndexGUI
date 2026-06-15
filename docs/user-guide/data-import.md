# Data Import

The first tab loads your data file and maps its columns to the standard names the rest of the pipeline expects.

## Loading a file

Click **Load Data** and choose a file. The following formats are supported:

- **CSV** (`.csv`)
- **Excel** (`.xlsx`, `.xls`)

The first few rows are shown in a preview table so you can confirm the contents.

## Column mapping

Because source files use different column names, you map them to the standard fields:

| Standard field | Required | Meaning |
|----------------|----------|---------|
| `date` | :material-check: | Observation date/timestamp. |
| `price` | :material-check: | Observed price. |
| `product_id` | :material-check: | Product/item identifier. |
| `quantity` | optional | Quantity sold (enables weighted methods). |

Each field has a dropdown populated with your file's actual column names. Select `None` for the optional quantity column if your data does not contain quantities.

## Date format

Provide the [strptime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) pattern matching your date column. The default is:

```
%Y-%m-%d
```

Common alternatives:

| Format string | Example match |
|---------------|---------------|
| `%d/%m/%Y` | `15/06/2026` |
| `%m/%d/%Y` | `06/15/2026` |
| `%Y%m%d` | `20260615` |

## Standardize

Click **Standardize Columns**. The app validates and converts the mapped columns to the expected types and shows a summary:

- number of **products**,
- the **date range** of the data,
- whether **quantity** data is available.

!!! warning "Weighted methods need quantity"
    If your file has no quantity column, weighted aggregation and weighted index methods (Laspeyres, Paasche, Fisher, Törnqvist, Walsh, GEKS-Fisher, GEKS-Törnqvist, Geary-Khamis) will be unavailable downstream.

## Recommended input shape

Use **one row per product per observation date**. For example:

| date | product_id | price | quantity |
|------|------------|-------|----------|
| 2026-01-01 | A | 100 | 10 |
| 2026-01-01 | B | 200 | 20 |
| 2026-02-01 | A | 110 | 12 |
| 2026-02-01 | B | 190 | 18 |

Once the summary appears, continue to [Aggregation](aggregation.md).
