from src.classifier import classify_demo, classify_review


def test_demo_detects_delay_and_cold_food():
    result = classify_demo("O pedido atrasou e chegou frio.", 1)
    assert "Atraso na entrega" in result.categorias
    assert "Comida fria" in result.categorias
    assert result.sentimento == "Negativo"


def test_demo_positive_review():
    result = classify_demo("Perfeito, estava delicioso e recomendo!", 5)
    assert "Elogios / Positivo" in result.categorias
    assert result.sentimento == "Positivo"


def test_empty_comment_is_rejected():
    try:
        classify_review("   ", 3)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_rating_is_rejected():
    try:
        classify_review("O pedido chegou.", 8)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
