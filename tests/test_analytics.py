import pandas as pd

from src.analytics import add_priority_score, summarize_reviews


def test_priority_score_is_bounded_and_ordered():
    df = pd.DataFrame({
        "prioridade": ["Baixa", "Média", "Alta"],
        "nota": [5, 3, 1],
        "sentimento": ["Positivo", "Neutro", "Negativo"],
    })
    result = add_priority_score(df)
    assert result["score_prioridade"].between(0, 100).all()
    assert result.iloc[0]["score_prioridade"] < result.iloc[2]["score_prioridade"]


def test_summary_empty_dataframe():
    result = summarize_reviews(pd.DataFrame(columns=["nota", "sentimento"]))
    assert result["total"] == 0
    assert result["percentual_negativo"] == 0.0
