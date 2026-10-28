from __future__ import annotations

import pandas as pd

PRIORITY_BASE = {"Baixa": 20, "Média": 55, "Alta": 85}


def add_priority_score(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with transparent, rule-based priority score (0–100)."""
    out = df.copy()
    if out.empty:
        out["score_prioridade"] = pd.Series(dtype="int64")
        out["prioridade"] = pd.Series(dtype="object")
        return out
    base = out["prioridade"].map(PRIORITY_BASE).fillna(20).astype(float)
    rating_penalty = (5 - pd.to_numeric(out["nota"], errors="coerce").fillna(3)).clip(0, 4) * 5
    out["score_prioridade"] = (base + rating_penalty).clip(0, 100).round().astype(int)
    out["prioridade"] = out["score_prioridade"].apply(
        lambda score: "Alta" if score >= 80 else ("Média" if score >= 45 else "Baixa")
    )
    return out


def summarize_reviews(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total": 0, "nota_media": None, "percentual_negativo": 0.0}
    return {
        "total": int(len(df)),
        "nota_media": round(float(df["nota"].mean()), 2),
        "percentual_negativo": round(float((df["sentimento"] == "Negativo").mean()), 4),
    }
