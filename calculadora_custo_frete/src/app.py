from __future__ import annotations

from datetime import date
from pathlib import Path
import io
import json
import math

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
RULES_PATH = DATA_DIR / "tabela_regras_frete.csv"
HISTORY_PATH = DATA_DIR / "historico_cotacoes_ficticio.csv"

st.set_page_config(
    page_title="Calculadora de Frete | Simulador",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODAIS = ["Rodoviário", "Aéreo", "Marítimo", "Ferroviário"]
TIPOS_CARGA = ["Geral", "Frágil", "Refrigerada", "Perigosa"]
MOEDAS = {"BRL": "R$", "USD": "US$", "EUR": "€"}

@st.cache_data
def carregar_regras() -> pd.DataFrame:
    regras = pd.read_csv(RULES_PATH)
    obrigatorias = {
        "modal", "tipo_carga", "taxa_fixa_brl", "taxa_kg_brl", "taxa_km_brl",
        "adicional_combustivel_pct", "frete_minimo_brl", "manuseio_especial_brl"
    }
    faltantes = obrigatorias - set(regras.columns)
    if faltantes:
        raise ValueError(f"Colunas ausentes na tabela de regras: {sorted(faltantes)}")
    if regras.duplicated(["modal", "tipo_carga"]).any():
        raise ValueError("Há combinações duplicadas de modal e tipo de carga na tabela.")
    if regras[list(obrigatorias - {"modal", "tipo_carga"})].isna().any().any():
        raise ValueError("A tabela de regras contém valores vazios.")
    return regras

def calcular_frete(
    peso_kg: float,
    distancia_km: float,
    modal: str,
    tipo_carga: str,
    volume_m3: float = 0.0,
    pedagios_brl: float = 0.0,
    seguro_pct: float = 0.5,
    urgencia_pct: float = 0.0,
    desconto_pct: float = 0.0,
    adicional_manual_brl: float = 0.0,
    regras: pd.DataFrame | None = None,
) -> dict:
    """Calcula estimativa transparente a partir de uma regra modal/tipo de carga."""
    if regras is None:
        regras = carregar_regras()
    if peso_kg <= 0:
        raise ValueError("O peso deve ser maior que zero.")
    if distancia_km <= 0:
        raise ValueError("A distância deve ser maior que zero.")
    if volume_m3 < 0 or pedagios_brl < 0 or adicional_manual_brl < 0:
        raise ValueError("Volume, pedágios e adicionais não podem ser negativos.")
    if not 0 <= seguro_pct <= 100:
        raise ValueError("O percentual de seguro deve ficar entre 0 e 100.")
    if not 0 <= urgencia_pct <= 300:
        raise ValueError("A urgência deve ficar entre 0 e 300%.")
    if not 0 <= desconto_pct <= 80:
        raise ValueError("O desconto deve ficar entre 0 e 80%.")

    filtro = regras[(regras["modal"] == modal) & (regras["tipo_carga"] == tipo_carga)]
    if filtro.empty:
        raise ValueError(f"Não existe regra para {modal} / {tipo_carga}.")
    regra = filtro.iloc[0]

    # Peso cubado é uma aproximação configurável; o fator é definido na interface.
    fator_cubagem = 200.0
    peso_cubado = volume_m3 * fator_cubagem
    peso_taxavel = max(float(peso_kg), peso_cubado)

    subtotal_base = (
        float(regra["taxa_fixa_brl"])
        + peso_taxavel * float(regra["taxa_kg_brl"])
        + float(distancia_km) * float(regra["taxa_km_brl"])
    )
    adicional_combustivel = subtotal_base * float(regra["adicional_combustivel_pct"])
    manuseio = float(regra["manuseio_especial_brl"])
    seguro = subtotal_base * (seguro_pct / 100.0)
    urgencia = (subtotal_base + adicional_combustivel) * (urgencia_pct / 100.0)
    subtotal_antes_minimo = subtotal_base + adicional_combustivel + manuseio + seguro + urgencia + pedagios_brl + adicional_manual_brl
    frete_minimo = float(regra["frete_minimo_brl"])
    ajuste_minimo = max(0.0, frete_minimo - subtotal_antes_minimo)
    subtotal_com_minimo = subtotal_antes_minimo + ajuste_minimo
    desconto = subtotal_com_minimo * (desconto_pct / 100.0)
    total = max(0.0, subtotal_com_minimo - desconto)

    return {
        "modal": modal,
        "tipo_carga": tipo_carga,
        "peso_real_kg": round(float(peso_kg), 2),
        "volume_m3": round(float(volume_m3), 3),
        "fator_cubagem_kg_m3": fator_cubagem,
        "peso_cubado_kg": round(peso_cubado, 2),
        "peso_taxavel_kg": round(peso_taxavel, 2),
        "distancia_km": round(float(distancia_km), 2),
        "taxa_fixa_brl": round(float(regra["taxa_fixa_brl"]), 2),
        "componente_peso_brl": round(peso_taxavel * float(regra["taxa_kg_brl"]), 2),
        "componente_distancia_brl": round(float(distancia_km) * float(regra["taxa_km_brl"]), 2),
        "subtotal_base_brl": round(subtotal_base, 2),
        "adicional_combustivel_brl": round(adicional_combustivel, 2),
        "manuseio_especial_brl": round(manuseio, 2),
        "seguro_brl": round(seguro, 2),
        "urgencia_brl": round(urgencia, 2),
        "pedagios_brl": round(float(pedagios_brl), 2),
        "adicional_manual_brl": round(float(adicional_manual_brl), 2),
        "ajuste_frete_minimo_brl": round(ajuste_minimo, 2),
        "subtotal_antes_desconto_brl": round(subtotal_com_minimo, 2),
        "desconto_brl": round(desconto, 2),
        "desconto_pct": float(desconto_pct),
        "total_estimado_brl": round(total, 2),
        "frete_minimo_brl": round(frete_minimo, 2),
        "taxa_combustivel_pct": round(float(regra["adicional_combustivel_pct"]) * 100, 2),
        "taxa_kg_brl": float(regra["taxa_kg_brl"]),
        "taxa_km_brl": float(regra["taxa_km_brl"]),
    }

def brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def preparar_csv(resultado: dict) -> bytes:
    return pd.DataFrame([resultado]).to_csv(index=False).encode("utf-8-sig")

def adicionar_historico(resultado: dict, nome_cliente: str, origem: str, destino: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    arquivo = OUTPUT_DIR / "historico_estimativas.csv"
    registro = {
        "data_calculo": date.today().isoformat(),
        "cliente": nome_cliente.strip(),
        "origem": origem.strip(),
        "destino": destino.strip(),
        **resultado,
    }
    novo = pd.DataFrame([registro])
    if arquivo.exists():
        antigo = pd.read_csv(arquivo)
        novo = pd.concat([antigo, novo], ignore_index=True)
    novo.to_csv(arquivo, index=False, encoding="utf-8-sig")

def main():
    st.title("🚚 Calculadora Interativa de Custo de Frete")
    st.caption("Simulador educacional com regras transparentes e dados fictícios. Não substitui uma cotação comercial.")
    try:
        regras = carregar_regras()
    except Exception as exc:
        st.error(f"Não foi possível carregar a tabela de regras: {exc}")
        st.stop()

    with st.sidebar:
        st.header("⚙️ Parâmetros da simulação")
        st.write("Preencha os dados da operação. Os valores são estimativas em reais.")
        modal = st.selectbox("Modal de transporte", MODAIS)
        tipo_carga = st.selectbox("Tipo de carga", TIPOS_CARGA)
        peso = st.number_input("Peso real (kg)", min_value=0.1, max_value=100000.0, value=500.0, step=50.0)
        distancia = st.number_input("Distância (km)", min_value=1.0, max_value=50000.0, value=350.0, step=25.0)
        volume = st.number_input("Volume da carga (m³)", min_value=0.0, max_value=1000.0, value=1.0, step=0.5)
        st.caption("Peso taxável = maior entre peso real e volume × fator de cubagem (200 kg/m³ neste exemplo).")
        pedagios = st.number_input("Pedágios / taxas de rota (R$)", min_value=0.0, max_value=100000.0, value=0.0, step=10.0)
        seguro = st.slider("Seguro (% do subtotal base)", min_value=0.0, max_value=5.0, value=0.5, step=0.1)
        urgencia = st.slider("Adicional de urgência (%)", min_value=0, max_value=100, value=0, step=5)
        desconto = st.slider("Desconto negociado (%)", min_value=0, max_value=50, value=0, step=1)
        adicional = st.number_input("Adicional manual (R$)", min_value=0.0, max_value=100000.0, value=0.0, step=10.0)
        st.divider()
        st.subheader("Dados opcionais")
        cliente = st.text_input("Cliente / projeto", placeholder="Ex.: Cliente A")
        origem = st.text_input("Origem", placeholder="Ex.: Campinas, SP")
        destino = st.text_input("Destino", placeholder="Ex.: Santos, SP")

    try:
        resultado = calcular_frete(
            peso_kg=peso, distancia_km=distancia, modal=modal, tipo_carga=tipo_carga,
            volume_m3=volume, pedagios_brl=pedagios, seguro_pct=seguro,
            urgencia_pct=urgencia, desconto_pct=desconto, adicional_manual_brl=adicional,
            regras=regras
        )
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.subheader("Resultado da simulação")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Frete estimado", brl(resultado["total_estimado_brl"]))
    c2.metric("Peso taxável", f'{resultado["peso_taxavel_kg"]:,.1f} kg'.replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Distância", f'{resultado["distancia_km"]:,.0f} km'.replace(",", "."))
    c4.metric("Modal / carga", f"{modal} / {tipo_carga}")

    st.info("Estimativa calculada por tabela de regras fictícia. Confirme tarifas, impostos, seguros, restrições e condições comerciais antes de usar em operação real.")

    tab1, tab2, tab3, tab4 = st.tabs(["🧾 Composição do preço", "📚 Tabela de regras", "📈 Histórico fictício", "💾 Exportar / salvar"])
    with tab1:
        componentes = [
            ("Taxa fixa", resultado["taxa_fixa_brl"]),
            ("Componente por peso taxável", resultado["componente_peso_brl"]),
            ("Componente por distância", resultado["componente_distancia_brl"]),
            ("Adicional de combustível", resultado["adicional_combustivel_brl"]),
            ("Manuseio especial", resultado["manuseio_especial_brl"]),
            ("Seguro", resultado["seguro_brl"]),
            ("Urgência", resultado["urgencia_brl"]),
            ("Pedágios / taxas de rota", resultado["pedagios_brl"]),
            ("Adicional manual", resultado["adicional_manual_brl"]),
            ("Ajuste para frete mínimo", resultado["ajuste_frete_minimo_brl"]),
            ("Desconto", -resultado["desconto_brl"]),
        ]
        comp = pd.DataFrame(componentes, columns=["Componente","Valor (R$)"])
        comp["Valor (R$)"] = comp["Valor (R$)"].round(2)
        st.dataframe(comp, use_container_width=True, hide_index=True)
        st.bar_chart(comp.set_index("Componente"))
        st.markdown("**Fórmula simplificada**")
        st.latex(r"\text{Subtotal base} = \text{taxa fixa} + (\text{peso taxável}\times\text{taxa/kg}) + (\text{distância}\times\text{taxa/km})")
        st.latex(r"\text{Total} = \max(\text{subtotal com adicionais},\text{frete mínimo}) - \text{desconto}")
        st.caption("O frete mínimo é aplicado antes do desconto. As regras são ilustrativas e editáveis no CSV.")
    with tab2:
        st.dataframe(regras, use_container_width=True, hide_index=True)
        st.download_button("Baixar tabela de regras (CSV)", data=regras.to_csv(index=False).encode("utf-8-sig"), file_name="tabela_regras_frete.csv", mime="text/csv")
    with tab3:
        hist_path = HISTORY_PATH
        if hist_path.exists():
            hist = pd.read_csv(hist_path)
            st.dataframe(hist.tail(50), use_container_width=True, hide_index=True)
            st.caption("Mostrando até as últimas 50 linhas do histórico demonstrativo.")
        else:
            st.dataframe(pd.read_csv(DATA_DIR / "historico_cotacoes_ficticio.csv").head(50), use_container_width=True, hide_index=True)
            st.caption("Amostra de histórico fictício incluída no projeto.")
    with tab4:
        st.write("Baixe esta simulação como CSV ou JSON.")
        st.download_button("⬇️ Baixar resultado (CSV)", data=preparar_csv(resultado), file_name="estimativa_frete.csv", mime="text/csv")
        st.download_button("⬇️ Baixar resultado (JSON)", data=json.dumps(resultado, ensure_ascii=False, indent=2).encode("utf-8"), file_name="estimativa_frete.json", mime="application/json")
        if st.button("💾 Salvar estimativa no histórico local"):
            adicionar_historico(resultado, cliente, origem, destino)
            st.success("Estimativa salva em outputs/historico_estimativas.csv")
        st.caption("O histórico é local ao ambiente onde o app está rodando. Para múltiplos usuários, use um banco de dados.")

    with st.expander("ℹ️ Como a estimativa é calculada"):
        st.markdown("""
        1. O sistema seleciona a regra pela combinação de **modal + tipo de carga**.
        2. Calcula o peso taxável: maior entre peso real e peso cubado.
        3. Soma taxa fixa, parcela por kg e parcela por km.
        4. Aplica adicional de combustível, manuseio, seguro, urgência, pedágios e adicionais manuais.
        5. Garante o frete mínimo e aplica o desconto.
        6. Mostra cada componente para facilitar auditoria.
        """)
    st.caption("Projeto de portfólio • Python + Streamlit + pandas • Dados e preços fictícios")

if __name__ == "__main__":
    main()
