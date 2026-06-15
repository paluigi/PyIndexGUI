# Export

The export tab lets you save your work to **CSV** or **Excel**. It is populated when you switch to it, showing everything computed so far.

## Exportable artifacts

| Artifact | What it contains |
|----------|------------------|
| **Bilateral Result** | The method, base/comparison periods, and the single index value. |
| **Multilateral Result** | The full index series (`period`, `index_value`). |
| **Balanced Panel** | The balanced, (optionally) imputed product-period panel. |

## Formats

Each artifact offers two buttons:

- **Export CSV** — writes a `.csv` file.
- **Export Excel** — writes an `.xlsx` file.

A native save-file dialog lets you choose the destination and file name. The default file name follows the convention:

```
<artifact>_data.<ext>
```

for example `bilateral_data.csv` or `multilateral_data.xlsx`.

!!! tip "Export the panel too"
    Even if you only computed a single bilateral index, you can still export the balanced panel for further analysis in another tool.

## File-name conventions

| Artifact | Default name |
|----------|--------------|
| Bilateral | `bilateral_data.csv` / `.xlsx` |
| Multilateral | `multilateral_data.csv` / `.xlsx` |
| Balanced | `balanced_data.csv` / `.xlsx` |

That completes the PyIndexGUI workflow.
