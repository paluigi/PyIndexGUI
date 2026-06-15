# PyIndexGUI

PyIndexGUI is a desktop graphical user interface for the [PyIndexNum](https://github.com/luigipalumbo/pyindexnum) economic index number library. It exposes the full PyIndexNum pipeline — from raw data import to multilateral index calculation and export — through an intuitive tabbed interface, built with [Flet](https://flet.dev/).

## Features

The app guides you through a complete price-index workflow in six tabs:

1. **Data Import** — Load CSV/Excel files, map columns to standard names, standardize data types.
2. **Aggregation** — Aggregate time series by frequency (daily, weekly, monthly, …) with configurable methods.
3. **Panel Balancing** — Remove unbalanced products or apply carry-forward/backward imputation.
4. **Index Calculation** — Compute bilateral and multilateral price indices.
5. **Export** — Save results and balanced panels to CSV or Excel.
6. **Info** — Version, authors, copyright, and a link to the GitHub repository.

## Next steps

- :material-download: Get the app running — see [Installation](installation.md) and [Running the App](running.md).
- :material-play-circle: Learn the workflow — start with the [User Guide](user-guide/index.md).
