"""
Generate benchmark comparison plots from benchmark_report.csv.

Usage:
    uv run python plot_results.py

Output:
    results/speed.png         — duration per method (lower is better)
    results/image_size.png    — Docker image size per method
    results/peak_mem.png      — peak container memory per method
    results/rank.png          — composite rank: speed + memory (lower is better)
"""

from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV_PATH = Path(__file__).parent / "benchmark_report.csv"
OUT_DIR = Path(__file__).parent / "results"
OUT_DIR.mkdir(exist_ok=True)

PALETTE = "#4C72B0"
PALETTE_2 = "#DD8452"

# ---------------------------------------------------------------------------
# Load & clean
# ---------------------------------------------------------------------------

def parse_mib(value: str) -> float | None:
    """Parse a size string like '72.4MiB' or '1.2GiB' to float MiB."""
    try:
        s = str(value).strip()
        if s.endswith("GiB"):
            return float(s[:-3]) * 1024
        if s.endswith("MiB"):
            return float(s[:-3])
        return float(s)
    except (ValueError, AttributeError):
        return None


def load_best_runs(csv_path: Path) -> pd.DataFrame:
    """
    Read csv, keep only PASS rows, parse sizes, and for each
    (method, dataset) keep the single fastest run.
    """
    df = pd.read_csv(csv_path)
    df = df[df["status"] == "PASS"].copy()
    df["duration_s"] = pd.to_numeric(df["duration_s"], errors="coerce")
    df["peak_mem_mib"] = pd.to_numeric(df["peak_mem_mib"], errors="coerce")
    df["image_size_mib"] = df["image_size"].apply(parse_mib)
    # best run = minimum duration per (method, dataset)
    df = df.sort_values("duration_s")
    df = df.drop_duplicates(subset=["method", "dataset"], keep="first")
    return df


# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------

DATASETS = ["2m", "full"]
DATASET_LABELS = {"2m": "2 M rows", "full": "Full dataset (~41 M rows)"}


def _axes_for_datasets(df: pd.DataFrame, width_per_col: float = 6,
                       height_per_row: float = 0.45):
    """Return (fig, axes_dict) where axes_dict maps dataset → ax.

    Height is scaled by the number of methods so bars are always visible.
    """
    present = [d for d in DATASETS if d in df["dataset"].values]
    n = len(present)
    n_methods = df["method"].nunique()
    fig_height = max(3.0, height_per_row * n_methods)
    fig, axes = plt.subplots(1, n, figsize=(width_per_col * n, fig_height),
                             squeeze=False)
    return fig, {d: axes[0, i] for i, d in enumerate(present)}


def _hbar(ax, series: pd.Series, label: str, unit: str, color: str,
          invert: bool = False) -> None:
    """Draw a horizontal bar chart on ax, sorted best-first."""
    s = series.dropna().sort_values(ascending=not invert)
    bars = ax.barh(s.index, s.values, color=color, edgecolor="white", height=0.6)
    ax.set_xlabel(f"{label} ({unit})")
    ax.invert_yaxis()
    ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=8)
    ax.set_xlim(0, s.values.max() * 1.18)
    ax.spines[["top", "right"]].set_visible(False)


# ---------------------------------------------------------------------------
# Individual plots
# ---------------------------------------------------------------------------

def plot_speed(df: pd.DataFrame) -> None:
    fig, axes = _axes_for_datasets(df)
    for dataset, ax in axes.items():
        sub = df[df["dataset"] == dataset].set_index("method")
        _hbar(ax, sub["duration_s"], "Duration", "s", PALETTE)
        ax.set_title(DATASET_LABELS.get(dataset, dataset), fontweight="bold")
    fig.suptitle("Speed — lower is better", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "speed.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUT_DIR / 'speed.png'}")


def plot_image_size(df: pd.DataFrame) -> None:
    fig, axes = _axes_for_datasets(df)
    for dataset, ax in axes.items():
        sub = df[df["dataset"] == dataset].set_index("method")
        _hbar(ax, sub["image_size_mib"], "Image size", "MiB", PALETTE_2)
        ax.set_title(DATASET_LABELS.get(dataset, dataset), fontweight="bold")
    fig.suptitle("Docker image size — lower is better", fontsize=13,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "image_size.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUT_DIR / 'image_size.png'}")


def plot_peak_mem(df: pd.DataFrame) -> None:
    fig, axes = _axes_for_datasets(df)
    for dataset, ax in axes.items():
        sub = df[df["dataset"] == dataset].set_index("method")
        _hbar(ax, sub["peak_mem_mib"], "Peak memory", "MiB", "#55a868")
        ax.set_title(DATASET_LABELS.get(dataset, dataset), fontweight="bold")
    fig.suptitle("Peak container memory — lower is better", fontsize=13,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "peak_mem.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUT_DIR / 'peak_mem.png'}")


def plot_rank(df: pd.DataFrame) -> None:
    """
    Composite rank = rank_by_duration + rank_by_peak_mem.
    Both ranks are 1-based ascending (1 = best). Lower total = better overall.
    """
    fig, axes = _axes_for_datasets(df)
    for dataset, ax in axes.items():
        sub = df[df["dataset"] == dataset].copy()
        sub["rank_speed"] = sub["duration_s"].rank(method="min")
        sub["rank_mem"] = sub["peak_mem_mib"].rank(method="min")
        sub["rank_composite"] = sub["rank_speed"] + sub["rank_mem"]
        sub = sub.set_index("method").sort_values("rank_composite")
        bars = ax.barh(sub.index, sub["rank_composite"],
                       color="#8172b2", edgecolor="white", height=0.6)
        ax.set_xlabel("Composite rank score (lower is better)")
        ax.invert_yaxis()
        ax.bar_label(bars, fmt="%.0f", padding=4, fontsize=8)
        ax.set_xlim(0, sub["rank_composite"].max() * 1.18)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_title(DATASET_LABELS.get(dataset, dataset), fontweight="bold")
    fig.suptitle("Composite rank: speed + memory (lower is better)",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "rank.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUT_DIR / 'rank.png'}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"{CSV_PATH} not found — run 'uv run invoke test-all' first."
        )
    df = load_best_runs(CSV_PATH)
    if df.empty:
        raise ValueError("No passing runs found in benchmark_report.csv.")

    print(f"Loaded {len(df)} best-pass rows across datasets: "
          f"{df['dataset'].unique().tolist()}")

    plot_speed(df)
    plot_image_size(df)
    plot_peak_mem(df)
    plot_rank(df)

    print("\nAll plots saved to results/")
