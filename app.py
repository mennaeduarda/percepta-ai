from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.analytics import add_priority_score, summarize_reviews
from src.classifier import classify_review, is_live_ai_available
from src.database import init_db, load_reviews, seed_demo_data, save_review

# Streamlit Community Cloud stores credentials in st.secrets, while local runs
# commonly use environment variables. Bridge the two without exposing secrets.
try:
    if not os.getenv("OPENAI_API_KEY") and st.secrets.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    if not os.getenv("OPENAI_MODEL") and st.secrets.get("OPENAI_MODEL"):
        os.environ["OPENAI_MODEL"] = st.secrets["OPENAI_MODEL"]
except Exception:
    # st.secrets can be unavailable when no secrets file is configured locally.
    pass

st.set_page_config(
    page_title="SaborIA | Customer Intelligence",
    page_icon="🍒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #101014; color: #f7f4f4; }
[data-testid="stSidebar"] { background: #19191f; border-right: 1px solid #33313a; }
h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -0.04em; }
.hero { padding: 1.2rem 0 .7rem 0; }
.eyebrow { color: #ff657d; text-transform: uppercase; font-size: .75rem; font-weight: 700; letter-spacing: .16em; }
.hero-title { font-family: 'Manrope',sans-serif; font-size: clamp(2rem,4vw,3.4rem); font-weight: 800; line-height: 1.03; color: #fff; }
.hero-title span { color: #ff657d; }
.hero-copy { color: #b9b4bf; max-width: 760px; font-size: 1rem; margin-top: .8rem; }
div[data-testid="stMetric"] { background: #1b1b22; border: 1px solid #34313b; padding: 1rem 1.1rem; border-radius: 16px; }
div[data-testid="stMetricLabel"] { color: #c5bfca; }
div[data-testid="stMetricValue"] { color: #fff; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; border: 1px solid #ff657d; background: #ff657d; color: #171217; font-weight: 700; }
.stButton > button:hover, .stDownloadButton > button:hover { background: #ff8b9c; border-color: #ff8b9c; color: #171217; }
section[data-testid="stMain"] .block-container { padding-top: 2rem; max-width: 1440px; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color: #34313b; border-radius: 14px; }
.small-muted { color: #a9a3b0; font-size: .85rem; }
</style>
""", unsafe_allow_html=True)

DB_PATH = os.getenv("SABORIA_DB_PATH", str(ROOT / "data" / "sabor_ia.db"))
init_db(DB_PATH)
seed_demo_data(DB_PATH)
df = load_reviews(DB_PATH)
if not df.empty:
    df = add_priority_score(df)

with st.sidebar:
    st.markdown("## 🍒 SaborIA")
    st.caption("Customer Intelligence")
    st.divider()
    page = st.radio("Navegação", ["Visão geral", "Analisar comentário", "Explorar avaliações", "Sobre o projeto"], label_visibility="collapsed")
    st.divider()
    if is_live_ai_available():
        st.success("IA conectada · OpenAI API")
    else:
        st.info("Modo demonstração ativo")
        st.caption("Configure OPENAI_API_KEY para habilitar a classificação via LLM.")
    st.caption("Projeto demonstrativo · dados fictícios")

if page == "Visão geral":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">Customer feedback intelligence</div>
      <div class="hero-title">Ouça melhor.<br><span>Decida mais rápido.</span></div>
      <div class="hero-copy">Transforme avaliações de delivery em sinais operacionais: descubra o que está dando errado, identifique padrões e priorize o que merece atenção.</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("Ainda não há avaliações disponíveis.")
        st.stop()

    restaurants = ["Todos os restaurantes"] + sorted(df["restaurante"].dropna().unique().tolist())
    selected_restaurant = st.selectbox("Restaurante", restaurants)
    filtered = df if selected_restaurant == "Todos os restaurantes" else df[df["restaurante"] == selected_restaurant]

    total = len(filtered)
    avg_rating = float(filtered["nota"].mean()) if total else 0
    issues = int((filtered["categoria"] != "Elogios / Positivo").sum()) if total else 0
    critical = int((filtered["prioridade"] == "Alta").sum()) if total else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avaliações analisadas", f"{total:,}".replace(",", "."))
    c2.metric("Nota média", f"{avg_rating:.1f} / 5")
    c3.metric("Relatos com problemas", issues, f"{issues / total:.0%} do total" if total else None)
    c4.metric("Alta prioridade", critical)

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("O que mais aparece")
        category_counts = filtered["categoria"].value_counts().rename_axis("Categoria").reset_index(name="Quantidade")
        if not category_counts.empty:
            fig = px.bar(category_counts, x="Quantidade", y="Categoria", orientation="h",
                         text="Quantidade", color="Quantidade",
                         color_continuous_scale=["#6e3342", "#ff657d"])
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False, xaxis_title="", yaxis_title="", margin=dict(l=0,r=15,t=10,b=10),
                height=360
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Distribuição de sentimento")
        sentiments = filtered["sentimento"].value_counts().rename_axis("Sentimento").reset_index(name="Quantidade")
        if not sentiments.empty:
            fig2 = px.pie(sentiments, names="Sentimento", values="Quantidade",
                          hole=.66, color="Sentimento",
                          color_discrete_map={"Positivo":"#75d6a2","Neutro":"#e7bd67","Negativo":"#ff657d"})
            fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=10), height=360,
                               legend=dict(orientation="h", y=-.08))
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🚨 Atenção primeiro")
    urgent = filtered.sort_values(["score_prioridade", "data_avaliacao"], ascending=[False, False]).head(5)
    if urgent.empty:
        st.caption("Nenhuma avaliação encontrada.")
    else:
        for _, row in urgent.iterrows():
            with st.container(border=True):
                a, b = st.columns([5, 1])
                a.markdown(f"**{row['restaurante']}** · {row['categoria']}")
                a.write(row["comentario"])
                a.caption(f"Nota {int(row['nota'])}/5 · {row['sentimento']} · {row['data_avaliacao']}")
                b.markdown(f"**{row['prioridade']}**")
                b.caption(f"Score {row['score_prioridade']}/100")

elif page == "Analisar comentário":
    st.markdown('<div class="eyebrow">LLM-powered triage</div>', unsafe_allow_html=True)
    st.title("Analise uma avaliação")
    st.write("Cole um comentário para identificar os problemas, o sentimento e a urgência. Com a chave configurada, a análise é feita pela API da OpenAI; sem ela, usamos um classificador simples de demonstração.")
    with st.form("review_form"):
        comment = st.text_area("Comentário do cliente", placeholder="Ex.: O pedido demorou muito, chegou frio e ainda veio faltando uma bebida...", height=150)
        rating = st.slider("Nota atribuída", 1, 5, 2)
        restaurant = st.text_input("Restaurante (opcional)", placeholder="Ex.: Cantina da Praça")
        submitted = st.form_submit_button("✨ Analisar avaliação", use_container_width=True)
    if submitted:
        if len(comment.strip()) < 5:
            st.error("Digite um comentário com pelo menos 5 caracteres.")
        else:
            with st.spinner("Interpretando o comentário..."):
                try:
                    result = classify_review(comment.strip(), rating)
                    live = is_live_ai_available()
                    st.session_state["last_analysis"] = (comment.strip(), rating, restaurant.strip(), result.model_dump(), live)
                except Exception as exc:
                    st.error(f"Não foi possível concluir a análise: {exc}")
                    st.caption("Confira a conexão e a configuração da chave de API.")
    if "last_analysis" in st.session_state:
        saved_comment, saved_rating, saved_restaurant, result, live = st.session_state["last_analysis"]
        st.divider()
        st.markdown("### Resultado da análise")
        st.caption("Classificação via OpenAI API" if live else "Classificação heurística de demonstração — não representa uma previsão de LLM")
        m1, m2, m3 = st.columns(3)
        m1.metric("Sentimento", result["sentimento"])
        m2.metric("Prioridade", result["prioridade"])
        m3.metric("Confiança estimada", f"{result['confianca']:.0%}")
        st.markdown("**Categorias identificadas**")
        st.write(", ".join(result["categorias"]))
        st.markdown("**Resumo**")
        st.write(result["resumo"])
        st.markdown("**Ação recomendada**")
        st.info(result["recomendacao"])
        if st.button("Salvar análise no histórico"):
            save_review(DB_PATH, saved_restaurant or "Restaurante não informado", saved_rating, saved_comment, result)
            st.success("Análise salva no histórico.")

elif page == "Explorar avaliações":
    st.title("Explorar avaliações")
    st.write("Filtre os registros, inspecione os comentários e exporte os dados para análise.")
    search = st.text_input("Buscar no comentário ou restaurante", placeholder="Digite uma palavra-chave...")
    categories = sorted(df["categoria"].dropna().unique().tolist()) if not df.empty else []
    chosen_categories = st.multiselect("Categorias", categories, default=categories)
    min_rating = st.slider("Nota mínima", 1, 5, 1)
    view = df.copy()
    if search:
        mask = view["comentario"].str.contains(search, case=False, na=False) | view["restaurante"].str.contains(search, case=False, na=False)
        view = view[mask]
    if chosen_categories:
        view = view[view["categoria"].isin(chosen_categories)]
    view = view[view["nota"] >= min_rating]
    cols = ["data_avaliacao", "restaurante", "nota", "sentimento", "categoria", "prioridade", "comentario"]
    st.caption(f"{len(view)} registro(s)")
    st.dataframe(view[cols], use_container_width=True, hide_index=True)
    st.download_button("⬇️ Exportar CSV", view[cols].to_csv(index=False).encode("utf-8-sig"),
                       file_name="sabor_ia_avaliacoes.csv", mime="text/csv")

else:
    st.title("Sobre o SaborIA")
    st.write("O SaborIA é um projeto de portfólio que explora como LLMs podem converter avaliações textuais em sinais estruturados para apoiar decisões operacionais.")
    st.markdown("""
    **Pipeline**
    1. Entrada de comentário e nota.
    2. Classificação estruturada do comentário.
    3. Validação e normalização das categorias.
    4. Pontuação de prioridade combinando nota, gravidade e recorrência futura.
    5. Persistência e visualização dos resultados.

    **Tecnologias:** Python, Streamlit, Plotly, Pandas, SQLite, Pydantic e OpenAI API.

    **Limitações:** os registros de demonstração são fictícios; o modo heurístico serve apenas para testar a interface. Resultados de LLM devem ser avaliados com um conjunto rotulado antes de qualquer uso operacional.
    """)
    st.markdown("[Documentação da API OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs) · [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)")
