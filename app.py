import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(page_title="Dashboard de Execução do PEF", layout="wide")
st.title("📊 Dashboard de Execução do PEF")

# =====================================================
# LEITURA DA BASE
# =====================================================
df = pd.read_excel("BASE_DE_TESTE_PYTHON_READY.xlsx")
df["MES"] = pd.to_datetime(df["MES"])

# =====================================================
# FILTRO DE MÊS
# =====================================================
mes_escolhido = st.selectbox(
    "Selecione o mês",
    sorted(df["MES"].unique()),
    format_func=lambda x: x.strftime("%m/%Y")
)
df = df[df["MES"] == mes_escolhido].copy()

# =====================================================
# REGRAS DE COR – SEMANAS
# =====================================================
def cor_semana_1(row):
    if pd.isna(row["PREV_SEM_1"]) or pd.isna(row["PEF_DO_MES"]):
        return "black"
    return "green" if row["PREV_SEM_1"] >= row["PEF_DO_MES"] else "red"

def cor_semana(row, atual, anterior):
    if pd.isna(row[atual]) or pd.isna(row[anterior]):
        return "black"
    return "green" if row[atual] >= row[anterior] else "red"

df["COR_SEM_1"] = df.apply(cor_semana_1, axis=1)
df["COR_SEM_2"] = df.apply(lambda r: cor_semana(r, "PREV_SEM_2", "PREV_SEM_1"), axis=1)
df["COR_SEM_3"] = df.apply(lambda r: cor_semana(r, "PREV_SEM_3", "PREV_SEM_2"), axis=1)
df["COR_SEM_4"] = df.apply(lambda r: cor_semana(r, "PREV_SEM_4", "PREV_SEM_3"), axis=1)

# =====================================================
# RISCO DE GLOSA (PRIORIDADE)
# =====================================================
def risco_por_prioridade(row):
    for col in ["RISCO_SEM_4", "RISCO_SEM_3", "RISCO_SEM_2", "RISCO_SEM_1"]:
        if pd.notna(row[col]) and str(row[col]).strip() != "":
            return row[col]
    return "NÃO"

df["RISCO_FINAL"] = df.apply(risco_por_prioridade, axis=1)
df["RISCO_TXT"] = np.where(df["RISCO_FINAL"] == "SIM", "🔴 SIM", "🟢 NÃO")

# =====================================================
# AVALIAÇÃO MENSAL
# =====================================================
df["RESULTADO_PEF"] = np.where(
    df["PREV_SEM_4"] >= df["PEF_DO_MES"],
    "DENTRO DO PREVISTO",
    "FORA DO PREVISTO"
)

# =====================================================
# HTML DA TABELA (REAL)
# =====================================================
rows_html = ""

for _, r in df.iterrows():
    rows_html += f"""
    <tr>
        <td>{r['CONTRATO_SUPER_1']}</td>
        <td style="color:{r['COR_SEM_1']}">R$ {r['PREV_SEM_1']:,.2f}</td>
        <td style="color:{r['COR_SEM_2']}">R$ {r['PREV_SEM_2']:,.2f}</td>
        <td style="color:{r['COR_SEM_3']}">R$ {r['PREV_SEM_3']:,.2f}</td>
        <td style="color:{r['COR_SEM_4']}">R$ {r['PREV_SEM_4']:,.2f}</td>
        <td>{r['RISCO_TXT']}</td>
        <td>R$ {r['PEF_DO_MES']:,.2f}</td>
        <td>{r['RESULTADO_PEF']}</td>
    </tr>
    """

html = f"""
<style>
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    background-color: #ffffff;
    color: #000000;
}}

th {{
    background-color: #f2f2f2;
    padding: 8px;
    text-align: left;
    color: #000000;
    border-bottom: 1px solid #cccccc;
}}

td {{
    padding: 8px;
    border-bottom: 1px solid #dddddd;
    background-color: #ffffff;
    color: #000000;
}}

tr:hover {{
    background-color: #f9f9f9;
}}
</style>

<table>
<tr>
    <th>Contratos</th>
    <th>Semana 1</th>
    <th>Semana 2</th>
    <th>Semana 3</th>
    <th>Semana 4</th>
    <th>Risco de Glosa</th>
    <th>Previsão do mês - PEF</th>
    <th>Resultado do Planejamento PEF</th>
</tr>
{rows_html}
</table>
"""

components.html(html, height=600, scrolling=True)
