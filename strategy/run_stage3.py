# run_stage3.py
import pandas as pd
from datetime import datetime

# Input/Output paths
STAGE2_CSV = "trade_suggestions_stage2.csv"
STAGE3_CSV = "trade_suggestions_stage3.csv"
STAGE3_JSON = "trade_suggestions_stage3.json"

# Filtering thresholds (tweak as needed)
MIN_WIN_PROB = 40.0  # minimum win probability (%)
MIN_RR_RATIO = 1.2
ALLOWED_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}  # only keep strong setups


def run_stage2():
    """Load results from Stage 2 CSV."""
    try:
        df = pd.read_csv(STAGE2_CSV)
        return df
    except FileNotFoundError:
        print(f"[ERROR] Stage-2 output not found: {STAGE2_CSV}")
        return pd.DataFrame()


def filter_and_rank(df: pd.DataFrame) -> pd.DataFrame:
    """Apply Stage-3 filters and rank suggestions."""
    if df.empty:
        return df

    # Apply filters
    filtered = df[
        (df["win_probability"] >= MIN_WIN_PROB)
        & (df["rr_ratio_live"] >= MIN_RR_RATIO)
        & (df["confidence"].isin(ALLOWED_CONFIDENCE))
    ].copy()

    if filtered.empty:
        return filtered

    # Rank: first by confidence, then win prob, then rr ratio
    confidence_order = {"HIGH": 2, "MEDIUM": 1, "LOW": 0}
    filtered["conf_rank"] = filtered["confidence"].map(confidence_order)

    ranked = filtered.sort_values(
        by=["conf_rank", "win_probability", "rr_ratio_live"],
        ascending=[False, False, False],
    ).drop(columns=["conf_rank"])

    return ranked


def save_results(df: pd.DataFrame):
    """Save Stage-3 results to CSV and JSON."""
    if df.empty:
        print("[INFO] No trades passed Stage-3 filters.")
        return

    now = datetime.utcnow().isoformat()
    df["filtered_at"] = now

    # Save CSV
    df.to_csv(STAGE3_CSV, index=False)

    # Save JSON
    df.to_json(STAGE3_JSON, orient="records", date_format="iso")

    print(f"[OK] Saved {len(df)} trades -> {STAGE3_CSV}, {STAGE3_JSON}")


if __name__ == "__main__":
    stage2_results = run_stage2()
    final_suggestions = filter_and_rank(stage2_results)
    print(final_suggestions)
    save_results(final_suggestions)
