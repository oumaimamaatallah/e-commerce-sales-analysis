# Setup

Python 3.11, 3.12 or 3.13 and a browser are the only prerequisites. Windows, macOS and Linux use the same launcher. No API key, database server, Node.js or Power BI installation is required. Internet is required to install packages, then the included dataset runs offline.

`python run.py` creates an isolated `.venv` beside the code. Use `python run.py --port 8502` if port 8501 is occupied or another project is running. Stop with Ctrl+C. The launcher binds to the local machine.

## Manual install

```sh
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` on macOS/Linux. If PowerShell blocks activation, use `.venv\Scripts\python.exe` directly instead of `python` below.

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For tests: install `requirements-dev.txt`, then run `python -m pytest -q`. The repository's CI runs these tests on Windows, Ubuntu and macOS with Python 3.12, plus Ubuntu with Python 3.11 and 3.13.

## Dependencies

Direct dependencies are **Streamlit 1.66.1** (app), **pandas 3.1.0** (tables), and **Plotly 7.1.0** (charts). Tests add **pytest 9.1.1**. SQLite, CSV handling and the data generator use Python's standard library. Every transitive dependency is pinned in `requirements.txt` and `requirements-dev.txt`, including platform and Python-version markers. The `.in` files list the direct dependencies.

## Docker

With Docker Engine or Docker Desktop running:

```sh
docker build -t retail-analysis .
docker run --rm -p 127.0.0.1:8501:8501 retail-analysis
```

Open http://localhost:8501. The image uses Python 3.12, runs as a non-root user and includes a health check. Docker is optional; the container build and startup are checked in CI.

## Different data

Copy the four CSV files described in [model.md](model.md) to a separate folder. Set `DATA_DIR` to its absolute path before starting the app or export script. PowerShell: `$env:DATA_DIR = 'C:\path\to\data'`; macOS/Linux: `export DATA_DIR=/path/to/data`. Rows are validated before joining. To use the sample again, unset the variable.

Regenerate the sample with `python scripts/generate_data.py`. This overwrites `data/*.csv`; `--output another-folder --seed 42` writes elsewhere.

To share a private repository, invite the reviewer as a collaborator or send them a source ZIP. They can extract it and run the same command; the app itself never needs GitHub credentials.
