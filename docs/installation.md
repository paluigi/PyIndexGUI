# Installation

PyIndexGUI runs as a local desktop application. Follow the steps below to get it on your machine.

## Prerequisites

- **Python 3.10 or newer**
- **[uv](https://docs.astral.sh/uv/)** — the fast Python package manager used for dependency management and running the app.

Install `uv` if you don't have it yet (see the [official instructions](https://docs.astral.sh/uv/getting-started/installation/)).

## Get the source

Clone the repository:

```bash
git clone https://github.com/paluigi/PyIndexGUI.git
cd PyIndexGUI
```

## Install dependencies

PyIndexGUI depends on the [PyIndexNum](https://github.com/luigipalumbo/pyindexnum) library (`>=0.2.0`) and [Flet](https://flet.dev/). With `uv`, installing everything is a single command:

```bash
uv sync
```

This creates a virtual environment and installs all project dependencies from `pyproject.toml`.

!!! info "Why uv?"
    `uv` keeps the environment reproducible and lockfile-managed. All commands throughout this documentation assume `uv` is the runner.

Once the environment is ready, head over to [Running the App](running.md).
