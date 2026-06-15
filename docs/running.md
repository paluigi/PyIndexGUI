# Running the App

## Development mode

To launch PyIndexGUI during development (with hot reload), run:

```bash
uv run flet run
```

The desktop window opens at **1200×800** with the *Data Import* tab selected.

## Packaging a standalone executable

To produce a self-contained executable you can distribute, use Flet's build command:

```bash
flet build <platform> -v
```

Replace `<platform>` with one of:

| Platform | Command |
|----------|---------|
| Linux | `flet build linux -v` |
| Windows | `flet build windows -v` |
| macOS | `flet build macos -v` |

The resulting binary does not require an end user to install Python or any dependencies.

!!! tip "First build"
    The first build downloads the Flet packaging toolchain and may take several minutes. Subsequent builds are faster.

## The Info tab

At any point — even before loading any data — you can open the **Info** tab (the last tab) to view the current application version, the authors, the copyright notice, and a clickable link to the [GitHub repository](https://github.com/paluigi/PyIndexGUI).

## Next step

You're ready to use the app. Continue to the [User Guide](user-guide/index.md).
