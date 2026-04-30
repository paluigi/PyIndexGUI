# PyIndexGUI

A desktop GUI for the [PyIndexNum](https://github.com/luigipalumbo/pyindexnum) economic index number library, built with [Flet](https://flet.dev/).

## Features

The app exposes the full PyIndexNum pipeline through a tabbed interface:

1. **Data Import** — Load CSV/Excel files, map columns to standard names, standardize data types
2. **Aggregation** — Aggregate time series data by frequency (daily, weekly, monthly, etc.) with configurable aggregation methods
3. **Panel Balancing** — Remove unbalanced products or apply carry-forward/backward imputation
4. **Index Calculation** — Compute bilateral indices (Jevons, Carli, Dutot, Laspeyres, Paasche, Fisher, Tornqvist, Walsh) and multilateral indices (GEKS-Fisher, GEKS-Tornqvist, Geary-Khamis, Time Product Dummy)
5. **Export** — Export results and balanced panels to CSV or Excel

## Run

```bash
uv run flet run
```

## Build

```bash
flet build linux -v
```

## Change Log

- **0.1.0** — Complete rewrite: OOP architecture, full PyIndexNum pipeline integration, 5-tab UI, bilateral and multilateral index calculation, export support.
