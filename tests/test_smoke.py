"""Smoke tests for the PyIndexGUI application.

These tests do not exercise the running GUI. They verify that the app module
and its dependencies import cleanly and that every tab's control tree can be
constructed without a live Flet session. This catches two whole classes of
regressions that a bare ``import`` cannot:

1. Broken imports (e.g. a renamed function in the ``pyindexnum`` library).
2. Invalid control construction (e.g. passing an unsupported keyword to a
   Flet control), which only surfaces when a tab is built.
"""

import main


def test_module_imports():
    """The app module and its dependencies import without error."""
    assert main.__version__
    assert main.APP_NAME


def test_index_registries_populated():
    """All bilateral and multilateral methods are wired up."""
    assert "Dutot" in main.BILATERAL_FUNCS
    assert "GEKS-Jevons" in main.MULTILATERAL_FUNCS
    # Every registered name must point to a callable.
    for func in main.BILATERAL_FUNCS.values():
        assert callable(func)
    for func in main.MULTILATERAL_FUNCS.values():
        assert callable(func)
    # Methods that require quantity must be a subset of all methods.
    assert main.MULTILATERAL_NEEDS_QUANTITY <= set(main.MULTILATERAL_FUNCS)


def test_app_builds_all_tabs():
    """Every tab's controls can be built without a live page."""
    app = main.PyIndexApp()
    app._build_import_tab()
    app._build_aggregation_tab()
    app._build_balancing_tab()
    app._build_index_tab()
    app._build_export_tab()
    app._build_info_tab()

    assert app._import_content is not None
    assert app._agg_content is not None
    assert app._bal_content is not None
    assert app._idx_content is not None
    assert app._exp_content is not None
    assert app._info_content is not None
