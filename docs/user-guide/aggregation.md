# Aggregation

The aggregation tab collapses your (possibly irregular) observations into regular time periods. This produces a clean panel with one price (and optionally one quantity) per product per period.

## Frequency

Choose how to group observations in time:

| Value | Meaning |
|-------|---------|
| `1d` | Daily |
| `1w` | Weekly |
| `1mo` | Monthly |
| `1q` | Quarterly |
| `1y` | Yearly |

For example, with `1mo`, all observations within the same calendar month are combined into a single monthly value per product.

## Aggregation type

Select how multiple prices within a period are combined:

| Type | Description |
|------|-------------|
| `arithmetic` | Arithmetic mean of prices. |
| `geometric` | Geometric mean of prices. |
| `harmonic` | Harmonic mean of prices. |

### Weighted variants

If you imported a `quantity` column, weighted variants become meaningful:

| Type | Description |
|------|-------------|
| `weighted_arithmetic` | Quantity-weighted arithmetic mean. |
| `weighted_geometric` | Quantity-weighted geometric mean. |
| `weighted_harmonic` | Quantity-weighted harmonic mean. |

!!! danger "Requires quantity data"
    Weighted aggregation is only available when quantity was mapped at import. The app blocks the run and notifies you if quantities are missing.

## Result

After running, the preview shows the aggregated panel with columns:

- `period` — the grouped time period (Date),
- `product_id` — the product,
- `aggregated_price` — the combined price,
- `aggregated_quantity` — the combined quantity (only for weighted types).

The info line reports the number of periods, rows, and products.

Continue to [Panel Balancing](panel-balancing.md).
