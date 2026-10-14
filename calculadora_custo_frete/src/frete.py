from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "tabela_regras_frete.csv"

def carregar_regras(caminho=RULES_PATH):
    regras = pd.read_csv(caminho)
    obrigatorias = [
        "modal", "tipo_carga", "taxa_fixa_brl", "taxa_kg_brl", "taxa_km_brl",
        "adicional_combustivel_pct", "frete_minimo_brl", "manuseio_especial_brl"
    ]
    faltantes = set(obrigatorias) - set(regras.columns)
    if faltantes:
        raise ValueError(f"Colunas ausentes: {sorted(faltantes)}")
    if regras.duplicated(["modal", "tipo_carga"]).any():
        raise ValueError("Combinações duplicadas de modal e tipo de carga.")
    return regras

def calcular_frete(peso_kg, distancia_km, modal, tipo_carga, volume_m3=0,
                   pedagios_brl=0, seguro_pct=0.5, urgencia_pct=0,
                   desconto_pct=0, adicional_manual_brl=0, regras=None,
                   fator_cubagem=200):
    if regras is None:
        regras = carregar_regras()
    if peso_kg <= 0 or distancia_km <= 0:
        raise ValueError("Peso e distância devem ser maiores que zero.")
    if volume_m3 < 0 or pedagios_brl < 0 or adicional_manual_brl < 0:
        raise ValueError("Volume, pedágios e adicionais não podem ser negativos.")
    if not 0 <= seguro_pct <= 100:
        raise ValueError("Seguro deve estar entre 0 e 100%.")
    if not 0 <= urgencia_pct <= 300:
        raise ValueError("Urgência deve estar entre 0 e 300%.")
    if not 0 <= desconto_pct <= 80:
        raise ValueError("Desconto deve estar entre 0 e 80%.")
    regra = regras[(regras.modal == modal) & (regras.tipo_carga == tipo_carga)]
    if regra.empty:
        raise ValueError(f"Regra não encontrada: {modal} / {tipo_carga}")
    r = regra.iloc[0]
    peso_cubado = volume_m3 * fator_cubagem
    peso_taxavel = max(float(peso_kg), peso_cubado)
    base = r.taxa_fixa_brl + peso_taxavel*r.taxa_kg_brl + distancia_km*r.taxa_km_brl
    combustivel = base*r.adicional_combustivel_pct
    seguro = base*seguro_pct/100
    urgencia_valor = (base+combustivel)*urgencia_pct/100
    antes_minimo = base+combustivel+r.manuseio_especial_brl+seguro+urgencia_valor+pedagios_brl+adicional_manual_brl
    ajuste_minimo = max(0, r.frete_minimo_brl-antes_minimo)
    antes_desconto = antes_minimo+ajuste_minimo
    desconto = antes_desconto*desconto_pct/100
    return {
        "modal": modal, "tipo_carga": tipo_carga, "peso_real_kg": round(float(peso_kg),2),
        "volume_m3": round(float(volume_m3),3), "peso_cubado_kg": round(peso_cubado,2),
        "peso_taxavel_kg": round(peso_taxavel,2), "distancia_km": round(float(distancia_km),2),
        "taxa_fixa_brl": round(float(r.taxa_fixa_brl),2),
        "componente_peso_brl": round(peso_taxavel*float(r.taxa_kg_brl),2),
        "componente_distancia_brl": round(float(distancia_km)*float(r.taxa_km_brl),2),
        "subtotal_base_brl": round(base,2), "adicional_combustivel_brl": round(combustivel,2),
        "manuseio_especial_brl": round(float(r.manuseio_especial_brl),2),
        "seguro_brl": round(seguro,2), "urgencia_brl": round(urgencia_valor,2),
        "pedagios_brl": round(float(pedagios_brl),2), "adicional_manual_brl": round(float(adicional_manual_brl),2),
        "ajuste_frete_minimo_brl": round(ajuste_minimo,2),
        "subtotal_antes_desconto_brl": round(antes_desconto,2), "desconto_brl": round(desconto,2),
        "total_estimado_brl": round(max(0,antes_desconto-desconto),2)
    }
