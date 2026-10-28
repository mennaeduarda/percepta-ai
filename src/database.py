from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

SCHEMA = """
CREATE TABLE IF NOT EXISTS avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurante TEXT NOT NULL,
    nota INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario TEXT NOT NULL,
    categorias TEXT NOT NULL,
    categoria TEXT NOT NULL,
    sentimento TEXT NOT NULL CHECK (sentimento IN ('Positivo', 'Neutro', 'Negativo')),
    prioridade TEXT NOT NULL CHECK (prioridade IN ('Baixa', 'Média', 'Alta')),
    confianca REAL NOT NULL CHECK (confianca >= 0 AND confianca <= 1),
    resumo TEXT NOT NULL,
    recomendacao TEXT NOT NULL,
    origem TEXT NOT NULL DEFAULT 'demo',
    data_avaliacao TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path) -> None:
    with connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)


def save_review(db_path: str | Path, restaurant: str, rating: int, comment: str, result: dict[str, Any]) -> int:
    categories = result.get("categorias", ["Outro"])
    with connect(db_path) as conn:
        cursor = conn.execute(
            """INSERT INTO avaliacoes
            (restaurante, nota, comentario, categorias, categoria, sentimento, prioridade,
             confianca, resumo, recomendacao, origem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                restaurant.strip() or "Restaurante não informado",
                int(rating),
                comment.strip(),
                " | ".join(categories),
                categories[0],
                result["sentimento"],
                result["prioridade"],
                float(result["confianca"]),
                result["resumo"],
                result["recomendacao"],
                "openai" if result.get("origem") == "openai" else "análise",
            ),
        )
        return int(cursor.lastrowid)


def load_reviews(db_path: str | Path) -> pd.DataFrame:
    with connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM avaliacoes ORDER BY data_avaliacao DESC, id DESC", conn)
    return df


def seed_demo_data(db_path: str | Path) -> None:
    """Seed sample reviews only when the database is empty; never deletes user data."""
    samples = [
        ("Sabor da Serra", 1, "O motoboy demorou mais de uma hora e a comida chegou fria.", ["Atraso na entrega", "Comida fria"], "Negativo", "Alta", .95, "Atraso e comida fria foram relatados.", "Investigar tempo de entrega e conservação."),
        ("Sabor da Serra", 2, "Pedi um X-bacon e veio um X-salada. Bem decepcionante.", ["Comida incorreta"], "Negativo", "Alta", .97, "O item entregue difere do pedido.", "Revisar conferência dos pedidos antes do envio."),
        ("Sabor da Serra", 5, "Perfeito como sempre, chegou rápido e quentinho!", ["Elogios / Positivo"], "Positivo", "Baixa", .96, "Cliente elogia a experiência e a temperatura.", "Manter o padrão de preparo e entrega."),
        ("Pizzaria Napoli Express", 3, "A pizza veio amassada e a caixa estava aberta.", ["Embalagem danificada/inadequada"], "Negativo", "Média", .91, "A embalagem chegou danificada.", "Verificar acondicionamento e vedação."),
        ("Pizzaria Napoli Express", 1, "Já é a segunda vez que atrasa mais de 40 minutos.", ["Atraso na entrega"], "Negativo", "Alta", .96, "Cliente relata atrasos recorrentes.", "Analisar recorrência por faixa de horário."),
        ("Pizzaria Napoli Express", 5, "Melhor pizza da região, super recomendo!", ["Elogios / Positivo"], "Positivo", "Baixa", .97, "Cliente elogia a pizza.", "Preservar a qualidade percebida."),
        ("Sushi Cherry Blossom", 2, "O entregador foi grosseiro na entrega.", ["Atendimento do entregador"], "Negativo", "Média", .93, "Cliente relata atendimento inadequado.", "Revisar o relato com a equipe responsável."),
        ("Sushi Cherry Blossom", 2, "O sushi chegou frio, não parecia ter sido feito na hora.", ["Comida fria", "Qualidade da comida"], "Negativo", "Média", .94, "Cliente questiona temperatura e frescor.", "Verificar tempo entre preparo e entrega."),
        ("Sushi Cherry Blossom", 4, "Comida muito boa, só achei a embalagem meio frágil.", ["Embalagem danificada/inadequada"], "Neutro", "Média", .84, "Elogio à comida com ressalva sobre embalagem.", "Avaliar resistência da embalagem."),
        ("Sushi Cherry Blossom", 5, "Sempre impecável, atendimento nota 10.", ["Elogios / Positivo"], "Positivo", "Baixa", .97, "Cliente elogia a experiência.", "Manter o padrão de atendimento."),
        ("Cantina da Praça", 1, "Faltou uma bebida e não consegui falar com o suporte.", ["Pedido incompleto"], "Negativo", "Alta", .95, "Pedido chegou incompleto e suporte não resolveu.", "Conferir itens e revisar fluxo de suporte."),
        ("Cantina da Praça", 2, "A cobrança veio duplicada no meu cartão.", ["Cobrança/pagamento"], "Negativo", "Alta", .96, "Cliente relata cobrança duplicada.", "Encaminhar para verificação de pagamento."),
        ("Burguer Lab", 3, "O hambúrguer estava meio cru no centro.", ["Qualidade da comida"], "Negativo", "Alta", .91, "Cliente relata ponto de preparo inadequado.", "Verificar padrão de preparo e segurança alimentar."),
        ("Burguer Lab", 5, "Chegou antes do prazo e estava delicioso.", ["Elogios / Positivo"], "Positivo", "Baixa", .97, "Cliente elogia sabor e pontualidade.", "Manter consistência no preparo e expedição."),
        ("Cantina da Praça", 2, "Veio sem o molho que pedi.", ["Pedido incompleto"], "Negativo", "Média", .91, "Um item solicitado não foi enviado.", "Reforçar conferência de adicionais."),
        ("Burguer Lab", 4, "A embalagem vazou um pouco, mas a comida estava boa.", ["Embalagem danificada/inadequada"], "Neutro", "Média", .88, "Houve vazamento apesar da avaliação positiva da comida.", "Avaliar vedação dos recipientes."),
    ]
    with connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM avaliacoes").fetchone()[0]
        if count:
            return
        conn.executemany(
            """INSERT INTO avaliacoes
            (restaurante, nota, comentario, categorias, categoria, sentimento, prioridade,
             confianca, resumo, recomendacao, origem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'demo')""",
            [
                (r, n, c, " | ".join(cats), cats[0], s, p, conf, summary, recommendation)
                for r, n, c, cats, s, p, conf, summary, recommendation in samples
            ],
        )
