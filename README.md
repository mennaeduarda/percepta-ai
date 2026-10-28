# 🍒 PERCEPTA AI — Customer Feedback Intelligence

**Transformando avaliações de delivery em sinais operacionais com IA generativa.**

O PerceptaAI é um projeto de portfólio que explora como LLMs podem converter comentários livres em dados estruturados para ajudar equipes a identificar falhas, acompanhar padrões e priorizar investigações.

> **Transparência:** a base inicial contém avaliações fictícias. Sem `OPENAI_API_KEY`, a tela de análise usa um classificador heurístico de demonstração, claramente identificado na interface. Com a chave configurada, a classificação usa a API da OpenAI e Structured Outputs. Este projeto não é afiliado ao iFood e não usa dados internos da empresa.

## ✨ Funcionalidades

- Dashboard de indicadores, categorias e sentimentos.
- Priorização explicável baseada em gravidade prevista e nota.
- Análise de comentário via API de LLM com saída estruturada e validação Pydantic.
- Classificação multi-rótulo: um comentário pode mencionar mais de um problema.
- Busca, filtros e exportação CSV.
- Persistência SQLite e carga inicial idempotente.
- Testes unitários para regras de classificação e métricas.
- Modo demonstração sem chave de API.

## 🧱 Arquitetura

```text
sabor-ia/
├── app.py                  # Interface Streamlit
├── src/
│   ├── classifier.py       # LLM, schema Pydantic e fallback de demonstração
│   ├── analytics.py        # Métricas e score explicável
│   └── database.py         # Persistência SQLite e seed idempotente
├── tests/
│   ├── test_classifier.py
│   └── test_analytics.py
├── data/                   # Banco criado localmente (não versionado)
├── .streamlit/config.toml  # Tema da aplicação
├── .env.example
├── .gitignore
└── requirements.txt
```

## 🚀 Executar localmente

Requer Python 3.10 ou superior.

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd sabor-ia

python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

O banco SQLite e os dados fictícios são criados automaticamente na primeira execução.

### Habilitar a API da OpenAI

Defina a variável de ambiente `OPENAI_API_KEY` antes de iniciar o Streamlit.

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="sua-chave"
$env:OPENAI_MODEL="gpt-4o-mini"
streamlit run app.py
```

macOS/Linux:
```bash
export OPENAI_API_KEY="sua-chave"
export OPENAI_MODEL="gpt-4o-mini"
streamlit run app.py
```

A chave nunca deve ser colocada no código ou commitada no Git. O modelo configurado por padrão é `gpt-4o-mini`; altere `OPENAI_MODEL` caso queira usar outro modelo disponível na sua conta.

## 🧪 Testes

```bash
pytest -q
```

Os testes atuais cobrem regras heurísticas, validação de entradas e cálculos de prioridade. Eles não medem a qualidade real de um LLM; isso exige um conjunto de referência rotulado e uma avaliação offline.

## ☁️ Publicar no Streamlit Community Cloud

1. Envie o repositório para o GitHub.
2. Entre em https://share.streamlit.io/ e conecte sua conta GitHub.
3. Crie uma aplicação apontando para `app.py`.
4. Em **Advanced settings → Secrets**, adicione:

```toml
OPENAI_API_KEY = "sua-chave"
OPENAI_MODEL = "gpt-4o-mini"
```

5. Faça o deploy e teste a página **Analisar comentário**.

A demonstração inicial funciona sem chave. Para proteger custos e evitar uso indevido, considere deixar a análise via API desabilitada no demo público ou adicionar limites de uso antes de divulgar a chave. Nunca inclua a chave no repositório. O armazenamento efêmero do ambiente de demonstração não deve ser tratado como banco de produção.

## 🔬 Como funciona a classificação

1. O comentário e a nota são enviados para o classificador.
2. O modelo recebe instruções para usar somente evidências do comentário e ignorar instruções embutidas no texto analisado.
3. O resultado segue um schema Pydantic: categorias, sentimento, prioridade, confiança estimada, resumo e recomendação.
4. A resposta estruturada é validada antes de ser apresentada.
5. A camada analítica gera um score de prioridade transparente a partir da prioridade e da nota.

A confiança retornada pelo modelo é uma estimativa declarada, **não uma probabilidade calibrada**. O score de prioridade é uma regra de negócio demonstrativa, não um modelo estatístico treinado.

## 📈 Próximos passos técnicos

- [ ] Montar conjunto rotulado maior, com exemplos ambíguos e multilabel.
- [ ] Criar avaliação offline com precision, recall e F1 por categoria.
- [ ] Comparar modelos e versões de prompt com custo, latência e qualidade.
- [ ] Adicionar retry com backoff, timeouts e tratamento de rate limits.
- [ ] Implementar limites de tamanho, rate limiting e proteção contra abuso no demo público.
- [ ] Adicionar logging estruturado sem registrar dados pessoais desnecessários.
- [ ] Criar pipeline de CI para rodar testes a cada pull request.
- [ ] Separar dados de demonstração de armazenamento persistente em produção.

## 🧰 Stack

Python · OpenAI API · Structured Outputs · Pydantic · Streamlit · Plotly · Pandas · SQLite · Pytest

## 📄 Licença

MIT — veja `LICENSE`.
