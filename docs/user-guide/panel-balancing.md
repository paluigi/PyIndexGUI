# Panel Balancing

Most index formulas require a **balanced panel**: every product must be present in *every* period. This tab turns the aggregated panel into a complete one and optionally fills remaining gaps.

## Remove unbalanced products

Click **Remove Unbalanced Products** to keep only those products that appear in all periods. Products with any missing period are dropped entirely.

The info line reports the change, e.g.:

```
Products: 120 → 95 (25 removed)  |  Rows: 570
```

!!! tip "Why balancing matters"
    Bilateral and multilateral index functions compare price relatives or expenditure shares across periods and products. A product missing in one period breaks those pairwise comparisons, so the panel must be complete before [Index Calculation](index-calculation.md).

## Imputation

If you prefer to keep products rather than drop them, you can fill gaps with imputation. Imputation works on the `aggregated_price` (and `aggregated_quantity`, if present) columns.

| Method | Description |
|--------|-------------|
| **Carry Forward** | Fills a missing value with the most recent prior value. |
| **Carry Backward** | Fills a missing value with the next available value. |

1. Run **Remove Unbalanced Products** first (this establishes the complete period structure).
2. Select an imputation method from the dropdown.
3. Click **Apply Imputation**.

!!! note "Order of operations"
    Imputation is applied *after* removing unbalanced products. The info line updates to record which method was applied.

Once the panel is complete, proceed to [Index Calculation](index-calculation.md).
