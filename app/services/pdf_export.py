from datetime import date

from flask import render_template

from app.models.empresa import Empresa
from app.models.lead import Lead
from app.models.metrica_diaria import MetricaDiaria


def gerar_pdf_painel(empresa_id, periodo_inicio, periodo_fim):
    empresa = Empresa.query.get(empresa_id)

    metricas = MetricaDiaria.query.filter(
        MetricaDiaria.empresa_id == empresa_id,
        MetricaDiaria.data >= periodo_inicio,
        MetricaDiaria.data <= periodo_fim,
    ).all()

    leads = Lead.query.filter(
        Lead.empresa_id == empresa_id,
        Lead.criado_em >= periodo_inicio,
        Lead.criado_em <= periodo_fim,
    ).all()

    total_gasto = sum(float(m.gasto) for m in metricas)
    total_impressoes = sum(m.impressoes for m in metricas)
    total_cliques = sum(m.cliques for m in metricas)
    total_leads = sum(m.leads_gerados for m in metricas)
    total_orcamentos = sum(1 for l in leads if l.status in ("orcamento", "contrato"))
    total_contratos = sum(1 for l in leads if l.status == "contrato")
    valor_contratos = sum(
        float(l.valor_contrato or 0) for l in leads if l.status == "contrato"
    )

    custo_por_lead = total_gasto / total_leads if total_leads > 0 else 0
    custo_por_contrato = total_gasto / total_contratos if total_contratos > 0 else 0

    criativos = {}
    for m in metricas:
        key = m.criativo_titulo or m.anuncio_nome or "Sem nome"
        if key not in criativos:
            criativos[key] = {"gasto": 0, "impressoes": 0, "cliques": 0, "leads": 0}
        criativos[key]["gasto"] += float(m.gasto)
        criativos[key]["impressoes"] += m.impressoes
        criativos[key]["cliques"] += m.cliques
        criativos[key]["leads"] += m.leads_gerados
    ranking_criativos = sorted(
        criativos.items(), key=lambda x: x[1]["gasto"], reverse=True
    )[:10]

    origens = {}
    for l in leads:
        origem = l.origem_campanha or "Origem desconhecida"
        origens[origem] = origens.get(origem, 0) + 1

    teto = float(empresa.teto_verba_mensal) if empresa.teto_verba_mensal else None

    html = render_template(
        "cliente/painel_pdf.html",
        empresa=empresa,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        total_gasto=total_gasto,
        total_impressoes=total_impressoes,
        total_cliques=total_cliques,
        total_leads=total_leads,
        total_orcamentos=total_orcamentos,
        total_contratos=total_contratos,
        valor_contratos=valor_contratos,
        custo_por_lead=custo_por_lead,
        custo_por_contrato=custo_por_contrato,
        ranking_criativos=ranking_criativos,
        origens=origens,
        teto=teto,
        data_geracao=date.today().isoformat(),
    )

    from weasyprint import HTML

    pdf_bytes = HTML(string=html).write_pdf()
    return pdf_bytes
