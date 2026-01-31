import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Dashboard de Execução PEF", layout="wide")

st.title("📊 Dashboard de Execução do PEF")

# =============================
# LEITURA DA BASE
# =============================
df = pd.read_excel("BASE_DE_TESTE_PYTHON_READY.xlsx")

df["MES"] = pd.to_datetime(df["MES"])

# =============================
# FILTRO
# =============================
meses = sorted(df["MES"].unique())

mes_escolhido = st.selectbox(
    "Selecione o mês",
    meses,
    format_func=lambda x: x.strftime("%m/%Y")
)

df_mes = df[df["MES"] == mes_escolhido].copy()

# =============================
# RISCO CONSOLIDADO
# =============================
def valor_valido(x):
    return pd.notna(x) and str(x).strip() != ""

def risco_consolidado(row):
    if valor_valido(row["RISCO_SEM_4"]):
        return row["RISCO_SEM_4"], "SEM_4"
    elif valor_valido(row["RISCO_SEM_3"]):
        return row["RISCO_SEM_3"], "SEM_3"
    elif valor_valido(row["RISCO_SEM_2"]):
        return row["RISCO_SEM_2"], "SEM_2"
    elif valor_valido(row["RISCO_SEM_1"]):
        return row["RISCO_SEM_1"], "SEM_1"
    else:
        return "NÃO", None

df_mes[["RISCO_CONSOLIDADO", "SEMANA_RISCO"]] = (
    df_mes.apply(risco_consolidado, axis=1, result_type="expand")
)

# =============================
# STATUS PEF FINAL
# =============================
df_mes["STATUS_PEF_FINAL"] = np.where(
    (df_mes["PREV_SEM_4"] >= df_mes["PEF_DO_MES"]) & pd.notna(df_mes["PREV_SEM_4"]),
    "DENTRO DO PLANEJADO",
    "FORA DO PLANEJADO"
)

# =============================
# KPI EXECUÇÃO FINAL
# =============================
df_mes["KPI_EXEC_FINAL_PCT"] = np.where(
    (df_mes["PEF_DO_MES"] > 0) & pd.notna(df_mes["PREV_SEM_4"]),
    (df_mes["PREV_SEM_4"] / df_mes["PEF_DO_MES"]) * 100,
    np.nan
).round(2)

# =============================
# KPIs TOPO
# =============================
col1, col2, col3 = st.columns(3)

col1.metric(
    "Execução Média (%)",
    f"{df_mes['KPI_EXEC_FINAL_PCT'].mean():.1f}%"
)

col2.metric(
    "Contratos em Risco",
    int((df_mes["RISCO_CONSOLIDADO"] == "SIM").sum())
)

col3.metric(
    "Contratos Fora do Planejado",
    int((df_mes["STATUS_PEF_FINAL"] == "FORA DO PLANEJADO").sum())
)

st.divider()

# =============================
# TABELA
# =============================
st.subheader("📋 Visão por Contrato")

st.dataframe(
    df_mes[
        [
            "CONTRATO_SUPER_1",
            "PEF_DO_MES",
            "PREV_SEM_4",
            "KPI_EXEC_FINAL_PCT",
            "STATUS_PEF_FINAL",
            "RISCO_CONSOLIDADO"
        ]
    ].sort_values("KPI_EXEC_FINAL_PCT", ascending=False),
    use_container_width=True
)
