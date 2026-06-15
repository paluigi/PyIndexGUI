import flet as ft
import polars as pl

from pyindexnum.utils import (
    standardize_columns,
    aggregate_time,
    remove_unbalanced,
    carry_forward_imputation,
    carry_backward_imputation,
    get_summary,
)
from pyindexnum.bilateral import (
    jevons,
    carli,
    dutot,
    laspeyres,
    paasche,
    fisher,
    tornqvist,
    walsh,
)
from pyindexnum.multilateral import (
    geks_fisher,
    geks_jevons,
    geks_tornqvist,
    geary_khamis,
    time_product_dummy,
)

BILATERAL_FUNCS = {
    "Jevons": jevons,
    "Carli": carli,
    "Dutot": dutot,
    "Laspeyres": laspeyres,
    "Paasche": paasche,
    "Fisher": fisher,
    "Tornqvist": tornqvist,
    "Walsh": walsh,
}
BILATERAL_WEIGHTED = {"Laspeyres", "Paasche", "Fisher", "Tornqvist", "Walsh"}

MULTILATERAL_FUNCS = {
    "GEKS-Jevons": geks_jevons,
    "GEKS-Fisher": geks_fisher,
    "GEKS-Tornqvist": geks_tornqvist,
    "Geary-Khamis": geary_khamis,
    "Time Product Dummy": time_product_dummy,
}
MULTILATERAL_NEEDS_QUANTITY = {"GEKS-Fisher", "GEKS-Tornqvist", "Geary-Khamis"}

FREQ_OPTIONS = ["1d", "1w", "1mo", "1q", "1y"]
AGG_OPTIONS_UNWEIGHTED = ["arithmetic", "geometric", "harmonic"]
AGG_OPTIONS_WEIGHTED = [
    "weighted_arithmetic",
    "weighted_geometric",
    "weighted_harmonic",
]

__version__ = "0.1.0"
APP_NAME = "pyindexgui"
APP_DESCRIPTION = "GUI for the PyIndexNum economic index number library"
APP_AUTHORS = "Luigi Palumbo and Mengting Yu"
APP_COPYRIGHT = "Copyright (C) 2023-2026 by Luigi Palumbo and Mengting Yu"
APP_REPO_URL = "https://github.com/paluigi/PyIndexGUI"


class PyIndexApp:

    async def main(self, page: ft.Page):
        self.page = page
        page.title = "PyIndex"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window.width = 1200
        page.window.height = 800

        self.raw_df = None
        self.standardized_df = None
        self.has_quantity = False
        self.aggregated_df = None
        self.available_periods = []
        self.balanced_df = None
        self.bilateral_result = None
        self.bilateral_info = {}
        self.multilateral_result = None
        self.multilateral_method = None

        self._build_import_tab()
        self._build_aggregation_tab()
        self._build_balancing_tab()
        self._build_index_tab()
        self._build_export_tab()
        self._build_info_tab()

        self._tabs = ft.Tabs(
            selected_index=0,
            length=6,
            animation_duration=200,
            expand=True,
            on_change=self._handle_tab_change,
            content=ft.Column(
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Data Import", icon=ft.Icons.UPLOAD_FILE),
                            ft.Tab(label="Aggregation", icon=ft.Icons.DATE_RANGE),
                            ft.Tab(label="Panel Balancing", icon=ft.Icons.BALANCE),
                            ft.Tab(label="Index Calculation", icon=ft.Icons.CALCULATE),
                            ft.Tab(label="Export", icon=ft.Icons.DOWNLOAD),
                            ft.Tab(label="Info", icon=ft.Icons.INFO),
                        ],
                    ),
                    ft.TabBarView(
                        controls=[
                            self._import_content,
                            self._agg_content,
                            self._bal_content,
                            self._idx_content,
                            self._exp_content,
                            self._info_content,
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
            ),
        )
        page.add(self._tabs)

    # ── Helpers ──────────────────────────────────────────────────────────

    def _show_snack(self, message: str, color=ft.Colors.BLUE):
        self.page.show_dialog(ft.SnackBar(content=ft.Text(message, color=color)))

    def _df_to_table(self, df: pl.DataFrame, max_rows: int = 50) -> ft.DataTable:
        preview = df.head(max_rows)
        # Cast date/time columns to strings for readable display
        preview = preview.with_columns(
            [
                pl.col(c).cast(pl.Utf8)
                for c in preview.columns
                if preview.schema[c].is_temporal()
            ]
        )
        cols = [ft.DataColumn(ft.Text(c)) for c in preview.columns]
        rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(v))) for v in row])
            for row in preview.to_numpy().tolist()
        ]
        return ft.DataTable(columns=cols, rows=rows)

    def _invalidate_from(self, tab_index: int):
        if tab_index <= 0:
            self.standardized_df = None
            self.has_quantity = False
        if tab_index <= 1:
            self.aggregated_df = None
            self.available_periods = []
        if tab_index <= 2:
            self.balanced_df = None
        if tab_index <= 3:
            self.bilateral_result = None
            self.bilateral_info = {}
            self.multilateral_result = None
            self.multilateral_method = None

    async def _handle_tab_change(self, e):
        idx = e.control.selected_index
        if idx == 5:
            self.page.update()
            return
        if idx >= 1 and self.standardized_df is None:
            e.control.selected_index = 0
        elif idx >= 2 and self.aggregated_df is None:
            e.control.selected_index = 1
        elif idx >= 3 and self.balanced_df is None:
            e.control.selected_index = 2
        elif idx == 4 and (
            self.bilateral_result is None and self.multilateral_result is None
        ):
            e.control.selected_index = 3
        if e.control.selected_index == 4:
            self._refresh_export_tab()
        if e.control.selected_index == 3 and self.balanced_df is not None:
            self._populate_period_dropdowns()
        self.page.update()

    def _populate_period_dropdowns(self):
        opts = [ft.dropdown.Option(str(p)) for p in self.available_periods]
        if self._bi_base_dd.options != opts:
            self._bi_base_dd.options = opts
            self._bi_comp_dd.options = opts

    # ── Tab 0: Data Import ──────────────────────────────────────────────

    def _build_import_tab(self):
        self._load_btn = ft.Button(
            "Load Data", icon=ft.Icons.UPLOAD_FILE, on_click=self._handle_load
        )
        self._date_fmt = ft.TextField(label="Date format", value="%Y-%m-%d", width=200)
        self._raw_preview = ft.Column()
        self._mapping_section = ft.Column(visible=False)
        self._import_summary = ft.Text(size=14, weight=ft.FontWeight.BOLD)

        self._map_dd = {}
        for name, req in [
            ("date", True),
            ("price", True),
            ("product_id", True),
            ("quantity", False),
        ]:
            dd = ft.Dropdown(
                label=f"Map {name} {'(required)' if req else '(optional)'}",
                width=300,
                disabled=True,
                options=[ft.dropdown.Option("None")],
            )
            self._map_dd[name] = dd

        self._std_btn = ft.Button(
            "Standardize Columns",
            icon=ft.Icons.CHECK,
            on_click=self._handle_standardize,
            disabled=True,
        )

        self._mapping_section.controls = [
            ft.Text("Column Mapping", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self._date_fmt,
            *[dd for dd in self._map_dd.values()],
            self._std_btn,
        ]

        self._import_content = ft.Container(
            padding=20,
            content=ft.Column(
                [
                    self._load_btn,
                    ft.Divider(),
                    self._raw_preview,
                    ft.Divider(),
                    self._mapping_section,
                    ft.Divider(),
                    self._import_summary,
                ],
                scroll=ft.ScrollMode.ALWAYS,
                expand=True,
            ),
        )

    async def _handle_load(self, e):
        files = await ft.FilePicker().pick_files(
            allow_multiple=False,
            allowed_extensions=["csv", "xlsx", "xls"],
        )
        if not files:
            return
        path = files[0].path
        ext = path.lower().rsplit(".", 1)[-1]
        try:
            if ext == "csv":
                self.raw_df = pl.read_csv(path)
            elif ext in ("xlsx", "xls"):
                self.raw_df = pl.read_excel(path)
            else:
                self._show_snack(f"Unsupported file type: .{ext}", ft.Colors.RED)
                return
        except Exception as err:
            self._show_snack(f"Error loading file: {err}", ft.Colors.RED)
            return

        self._raw_preview.controls = [self._df_to_table(self.raw_df, 5)]
        for dd in self._map_dd.values():
            dd.options = [ft.dropdown.Option("None")] + [
                ft.dropdown.Option(c) for c in self.raw_df.columns
            ]
            dd.disabled = False
        self._std_btn.disabled = False
        self._mapping_section.visible = True
        self._import_summary.value = ""
        self._invalidate_from(0)
        self._show_snack(f"Loaded {len(self.raw_df)} rows")
        self.page.update()

    async def _handle_standardize(self, e):
        mapping = {}
        for name, dd in self._map_dd.items():
            val = dd.value
            if val and val != "None":
                mapping[name] = val
            elif name in ("date", "price", "product_id"):
                self._show_snack(
                    f"Required field '{name}' is not mapped", ft.Colors.RED
                )
                return

        try:
            self.standardized_df = standardize_columns(
                self.raw_df,
                date_col=mapping["date"],
                price_col=mapping["price"],
                id_col=mapping["product_id"],
                quantity_col=mapping.get("quantity"),
                date_format=self._date_fmt.value,
            )
        except Exception as err:
            self._show_snack(f"Standardization error: {err}", ft.Colors.RED)
            return

        self.has_quantity = "quantity" in self.standardized_df.columns
        summary = get_summary(self.standardized_df)
        self._import_summary.value = (
            f"Products: {summary['n_products']}  |  "
            f"Date range: {summary['start_date']} to {summary['end_date']}  |  "
            f"Quantity: {'Yes' if self.has_quantity else 'No'}"
        )
        self._invalidate_from(1)
        self._show_snack("Columns standardized", ft.Colors.GREEN)
        self.page.update()

    # ── Tab 1: Aggregation ──────────────────────────────────────────────

    def _build_aggregation_tab(self):
        self._freq_dd = ft.Dropdown(
            label="Frequency",
            width=200,
            value="1mo",
            options=[ft.dropdown.Option(f) for f in FREQ_OPTIONS],
        )
        self._agg_type_dd = ft.Dropdown(
            label="Aggregation type",
            width=250,
            value="arithmetic",
            options=[ft.dropdown.Option(a) for a in AGG_OPTIONS_UNWEIGHTED],
        )
        self._agg_btn = ft.Button(
            "Run Aggregation", icon=ft.Icons.PLAY_ARROW, on_click=self._handle_aggregate
        )
        self._agg_info = ft.Text("", italic=True)
        self._agg_preview = ft.Column()

        self._agg_content = ft.Container(
            padding=20,
            content=ft.Column(
                [
                    ft.Text("Time Aggregation", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([self._freq_dd, self._agg_type_dd]),
                    self._agg_info,
                    self._agg_btn,
                    ft.Divider(),
                    self._agg_preview,
                ],
                scroll=ft.ScrollMode.ALWAYS,
                expand=True,
            ),
        )

    async def _handle_aggregate(self, e):
        freq = self._freq_dd.value
        agg_type = self._agg_type_dd.value
        if not freq or not agg_type:
            self._show_snack("Select frequency and aggregation type", ft.Colors.RED)
            return
        if agg_type.startswith("weighted_") and not self.has_quantity:
            self._show_snack(
                "Weighted aggregation requires quantity data", ft.Colors.RED
            )
            return

        try:
            self.aggregated_df = aggregate_time(
                self.standardized_df,
                date_col="date",
                price_col="price",
                id_col="product_id",
                quantity_col="quantity" if self.has_quantity else None,
                agg_type=agg_type,
                freq=freq,
            )
        except Exception as err:
            self._show_snack(f"Aggregation error: {err}", ft.Colors.RED)
            return

        periods = self.aggregated_df["period"].unique().sort().to_list()
        self.available_periods = periods
        self._agg_preview.controls = [self._df_to_table(self.aggregated_df, 20)]
        self._agg_info.value = (
            f"Periods: {len(periods)}  |  Rows: {len(self.aggregated_df)}  |  "
            f"Products: {self.aggregated_df['product_id'].n_unique()}"
        )
        self._invalidate_from(2)
        self._show_snack("Aggregation complete", ft.Colors.GREEN)
        self.page.update()

    # ── Tab 2: Panel Balancing ──────────────────────────────────────────

    def _build_balancing_tab(self):
        self._bal_preview = ft.Column()
        self._bal_info = ft.Text("", italic=True)
        self._remove_unbal_btn = ft.Button(
            "Remove Unbalanced Products",
            icon=ft.Icons.FILTER_ALT,
            on_click=self._handle_remove_unbalanced,
        )
        self._imputation_dd = ft.Dropdown(
            label="Imputation method",
            width=250,
            value="none",
            options=[
                ft.dropdown.Option("none"),
                ft.dropdown.Option("Carry Forward"),
                ft.dropdown.Option("Carry Backward"),
            ],
        )
        self._impute_btn = ft.Button(
            "Apply Imputation",
            icon=ft.Icons.AUTO_FIX_HIGH,
            on_click=self._handle_imputation,
        )

        self._bal_content = ft.Container(
            padding=20,
            content=ft.Column(
                [
                    ft.Text("Panel Balancing", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self._remove_unbal_btn,
                    ft.Divider(),
                    ft.Text("Imputation", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([self._imputation_dd, self._impute_btn]),
                    ft.Divider(),
                    self._bal_info,
                    self._bal_preview,
                ],
                scroll=ft.ScrollMode.ALWAYS,
                expand=True,
            ),
        )

    async def _handle_remove_unbalanced(self, e):
        if self.aggregated_df is None:
            self._show_snack("Run aggregation first", ft.Colors.RED)
            return
        try:
            n_before = self.aggregated_df["product_id"].n_unique()
            self.balanced_df = remove_unbalanced(self.aggregated_df)
            n_after = self.balanced_df["product_id"].n_unique()
        except Exception as err:
            self._show_snack(f"Error: {err}", ft.Colors.RED)
            return

        removed = n_before - n_after
        self._bal_info.value = f"Products: {n_before} → {n_after} ({removed} removed)  |  Rows: {len(self.balanced_df)}"
        self._bal_preview.controls = [self._df_to_table(self.balanced_df, 20)]
        self._invalidate_from(3)
        self._show_snack(f"Removed {removed} unbalanced products", ft.Colors.GREEN)
        self.page.update()

    async def _handle_imputation(self, e):
        if self.balanced_df is None:
            self._show_snack("Remove unbalanced products first", ft.Colors.RED)
            return
        method = self._imputation_dd.value
        if method == "none":
            self._show_snack("Select an imputation method", ft.Colors.RED)
            return

        value_cols = ["aggregated_price"]
        if "aggregated_quantity" in self.balanced_df.columns:
            value_cols.append("aggregated_quantity")

        try:
            if method == "Carry Forward":
                self.balanced_df = carry_forward_imputation(
                    self.balanced_df, value_cols
                )
            else:
                self.balanced_df = carry_backward_imputation(
                    self.balanced_df, value_cols
                )
        except Exception as err:
            self._show_snack(f"Imputation error: {err}", ft.Colors.RED)
            return

        self._bal_preview.controls = [self._df_to_table(self.balanced_df, 20)]
        self._bal_info.value += f"  |  Imputed ({method})"
        self._show_snack(f"{method} imputation applied", ft.Colors.GREEN)
        self.page.update()

    # ── Tab 3: Index Calculation ────────────────────────────────────────

    def _build_index_tab(self):
        self._bi_base_dd = ft.Dropdown(label="Base period", width=200)
        self._bi_comp_dd = ft.Dropdown(label="Comparison period", width=200)
        self._bi_method_dd = ft.Dropdown(
            label="Method",
            width=200,
            options=[ft.dropdown.Option(m) for m in BILATERAL_FUNCS],
        )
        self._bi_btn = ft.Button(
            "Calculate", icon=ft.Icons.PLAY_ARROW, on_click=self._handle_bilateral
        )
        self._bi_result = ft.Text("", size=18, weight=ft.FontWeight.BOLD)

        self._ml_method_dd = ft.Dropdown(
            label="Method",
            width=250,
            options=[ft.dropdown.Option(m) for m in MULTILATERAL_FUNCS],
        )
        self._ml_weighted_sw = ft.Switch(label="Weighted", value=True)
        self._ml_max_iter = ft.TextField(label="Max iterations", value="100", width=100)
        self._ml_tol = ft.TextField(label="Tolerance", value="1e-8", width=150)
        self._ml_params = ft.Row([self._ml_max_iter, self._ml_tol], visible=False)
        self._ml_btn = ft.Button(
            "Calculate", icon=ft.Icons.PLAY_ARROW, on_click=self._handle_multilateral
        )
        self._ml_result = ft.Column()

        self._idx_content = ft.Container(
            padding=20,
            content=ft.Column(
                [
                    ft.Text("Bilateral Indices", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("Compare exactly 2 periods.", italic=True, size=12),
                    ft.Row(
                        [
                            self._bi_base_dd,
                            self._bi_comp_dd,
                            self._bi_method_dd,
                            self._bi_btn,
                        ]
                    ),
                    self._bi_result,
                    ft.Divider(),
                    ft.Text("Multilateral Indices", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([self._ml_method_dd, self._ml_weighted_sw]),
                    self._ml_params,
                    self._ml_btn,
                    self._ml_result,
                ],
                scroll=ft.ScrollMode.ALWAYS,
                expand=True,
            ),
        )

    async def _handle_bilateral(self, e):
        if self.balanced_df is None:
            self._show_snack("Complete panel balancing first", ft.Colors.RED)
            return
        base = self._bi_base_dd.value
        comp = self._bi_comp_dd.value
        method = self._bi_method_dd.value
        if not base or not comp or not method:
            self._show_snack(
                "Select base, comparison period, and method", ft.Colors.RED
            )
            return
        if base == comp:
            self._show_snack("Base and comparison periods must differ", ft.Colors.RED)
            return
        if method in BILATERAL_WEIGHTED and not self.has_quantity:
            self._show_snack(f"{method} requires quantity data", ft.Colors.RED)
            return

        try:
            base_dt = pl.Series("period", [base, comp]).str.strptime(
                pl.Date, "%Y-%m-%d"
            )
            filtered = self.balanced_df.filter(pl.col("period").is_in(base_dt))
            rename = {"period": "date", "aggregated_price": "price"}
            if "aggregated_quantity" in filtered.columns:
                rename["aggregated_quantity"] = "quantity"
            bilateral_df = filtered.rename(rename)
            self.bilateral_result = BILATERAL_FUNCS[method](bilateral_df)
        except Exception as err:
            self._show_snack(f"Bilateral error: {err}", ft.Colors.RED)
            return

        self.bilateral_info = {"method": method, "base": base, "comp": comp}
        self._bi_result.value = (
            f"{method} Index ({base} → {comp}): {self.bilateral_result:.6f}"
        )
        self._show_snack("Bilateral index calculated", ft.Colors.GREEN)
        self.page.update()

    async def _handle_multilateral(self, e):
        if self.balanced_df is None:
            self._show_snack("Complete panel balancing first", ft.Colors.RED)
            return
        method = self._ml_method_dd.value
        if not method:
            self._show_snack("Select a method", ft.Colors.RED)
            return
        if method in MULTILATERAL_NEEDS_QUANTITY and not self.has_quantity:
            self._show_snack(f"{method} requires quantity data", ft.Colors.RED)
            return

        try:
            func = MULTILATERAL_FUNCS[method]
            if method == "Geary-Khamis":
                self.multilateral_result = func(
                    self.balanced_df,
                    max_iter=int(self._ml_max_iter.value),
                    tol=float(self._ml_tol.value),
                )
            elif method == "Time Product Dummy":
                self.multilateral_result = func(
                    self.balanced_df,
                    weighted=self._ml_weighted_sw.value,
                )
            else:
                self.multilateral_result = func(self.balanced_df)
        except Exception as err:
            self._show_snack(f"Multilateral error: {err}", ft.Colors.RED)
            return

        self.multilateral_method = method
        self._ml_result.controls = [self._df_to_table(self.multilateral_result)]
        self._show_snack(f"{method} calculated", ft.Colors.GREEN)
        self.page.update()

    # ── Tab 4: Export ────────────────────────────────────────────────────

    def _build_export_tab(self):
        self._exp_results = ft.Column()
        self._exp_content = ft.Container(
            padding=20,
            content=ft.Column(
                [
                    ft.Text("Results & Export", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self._exp_results,
                ],
                scroll=ft.ScrollMode.ALWAYS,
                expand=True,
            ),
        )

    # ── Tab 5: Info ─────────────────────────────────────────────────────

    def _build_info_tab(self):
        self._info_content = ft.Container(
            padding=20,
            content=ft.Column(
                [
                    ft.Text("About", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        f"{APP_NAME} v{__version__}", size=16, weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(APP_DESCRIPTION, italic=True),
                    ft.Divider(),
                    ft.Text(f"Authors: {APP_AUTHORS}"),
                    ft.Text(f"Version: {__version__}"),
                    ft.Text(APP_COPYRIGHT, size=12),
                    ft.Divider(),
                    ft.Button(
                        APP_REPO_URL,
                        icon=ft.Icons.OPEN_IN_NEW,
                        url=APP_REPO_URL,
                    ),
                ],
                scroll=ft.ScrollMode.ALWAYS,
                expand=True,
            ),
        )

    def _refresh_export_tab(self):
        controls = []
        if self.bilateral_result is not None:
            info = self.bilateral_info
            controls += [
                ft.Text("Bilateral Result", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"{info['method']}: {self.bilateral_result:.6f}  ({info['base']} → {info['comp']})"
                ),
                ft.Row(
                    [
                        ft.Button(
                            "Export CSV",
                            icon=ft.Icons.DOWNLOAD,
                            data=("bilateral", "csv"),
                            on_click=self._handle_export,
                        ),
                        ft.Button(
                            "Export Excel",
                            icon=ft.Icons.DOWNLOAD,
                            data=("bilateral", "xlsx"),
                            on_click=self._handle_export,
                        ),
                    ]
                ),
                ft.Divider(),
            ]
        if self.multilateral_result is not None:
            controls += [
                ft.Text("Multilateral Result", size=16, weight=ft.FontWeight.BOLD),
                self._df_to_table(self.multilateral_result),
                ft.Row(
                    [
                        ft.Button(
                            "Export CSV",
                            icon=ft.Icons.DOWNLOAD,
                            data=("multilateral", "csv"),
                            on_click=self._handle_export,
                        ),
                        ft.Button(
                            "Export Excel",
                            icon=ft.Icons.DOWNLOAD,
                            data=("multilateral", "xlsx"),
                            on_click=self._handle_export,
                        ),
                    ]
                ),
                ft.Divider(),
            ]
        if self.balanced_df is not None:
            controls += [
                ft.Text("Balanced Panel", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Button(
                            "Export CSV",
                            icon=ft.Icons.DOWNLOAD,
                            data=("balanced", "csv"),
                            on_click=self._handle_export,
                        ),
                        ft.Button(
                            "Export Excel",
                            icon=ft.Icons.DOWNLOAD,
                            data=("balanced", "xlsx"),
                            on_click=self._handle_export,
                        ),
                    ]
                ),
            ]
        self._exp_results.controls = controls

    async def _handle_export(self, e):
        target, fmt = e.control.data
        ext = "csv" if fmt == "csv" else "xlsx"
        result = await ft.FilePicker().save_file(
            allowed_extensions=[ext],
            file_name=f"{target}_data.{ext}",
        )
        if not result or not result.path:
            return
        try:
            if target == "bilateral":
                info = self.bilateral_info
                df = pl.DataFrame(
                    {
                        "method": [info["method"]],
                        "base_period": [str(info["base"])],
                        "comparison_period": [str(info["comp"])],
                        "index_value": [self.bilateral_result],
                    }
                )
            elif target == "multilateral":
                df = self.multilateral_result
            else:
                df = self.balanced_df

            if fmt == "csv":
                df.write_csv(result.path)
            else:
                df.write_excel(result.path)
        except Exception as err:
            self._show_snack(f"Export error: {err}", ft.Colors.RED)
            return
        self._show_snack(f"Exported to {result.path}", ft.Colors.GREEN)


if __name__ == "__main__":
    ft.run(main=PyIndexApp().main)
