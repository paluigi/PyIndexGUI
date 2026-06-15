# Index Calculation

This tab computes price indices from the balanced panel. There are two families: **bilateral** indices (comparing exactly two periods) and **multilateral** indices (using the whole panel).

## Bilateral indices

Bilateral indices compare a **base period** to a **comparison period**. Select both periods from the dropdowns, choose a method, and click **Calculate**.

The result is a single index value (the price level in the comparison period relative to the base period, where base = 1.0).

### Available methods

| Method | Weighted? | Description |
|--------|-----------|-------------|
| Jevons | No | Geometric mean of price relatives. |
| Carli | No | Arithmetic mean of price relatives. |
| Dutot | No | Ratio of arithmetic mean prices. |
| Laspeyres | :material-check: | Base-period quantity basket. |
| Paasche | :material-check: | Current-period quantity basket. |
| Fisher | :material-check: | Geometric mean of Laspeyres and Paasche. |
| Törnqvist | :material-check: | Weighted geometric mean with average expenditure shares. |
| Walsh | :material-check: | Fixed basket using geometric-mean quantities. |

!!! warning "Weighted methods require quantity"
    If no quantity column was imported, the weighted methods (Laspeyres, Paasche, Fisher, Törnqvist, Walsh) are blocked. Use an unweighted method instead, or re-import data with quantities.

!!! info "Exactly two periods"
    A bilateral calculation uses only the two selected periods. You can repeat the calculation with different period pairs.

## Multilateral indices

Multilateral indices use the entire balanced panel to produce a full index series — one index value per period, relative to the first (chronological) period (base = 1.0).

### Available methods

| Method | Needs quantity? | Notes |
|--------|-----------------|-------|
| GEKS-Jevons | No | Unweighted; ideal for web-scraped data without quantities. |
| GEKS-Fisher | :material-check: | GEKS over the Fisher bilateral formula. |
| GEKS-Törnqvist | :material-check: | GEKS over the Törnqvist bilateral formula. |
| Geary-Khamis | :material-check: | Iterative; exposes advanced parameters (below). |
| Time Product Dummy | Optional | Supports a weighted/unweighted toggle. |

### Advanced parameters

**Geary-Khamis** is an iterative method. You can tune its convergence:

| Parameter | Default | Meaning |
|-----------|---------|---------|
| Max iterations | `100` | Upper bound on the number of iterations. |
| Tolerance | `1e-8` | Convergence threshold. |

**Time Product Dummy** has a **Weighted** switch:

- **Weighted (on)** — uses expenditure shares; requires a quantity column.
- **Unweighted (off)** — uses prices only; works without quantities.

### Result

The result table shows `period` and the computed `index_value` for every period.

Continue to [Export](export.md) to save your results.
