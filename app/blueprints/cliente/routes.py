from datetime import date, timedelta

from flask import Response, current_app, render_template, request
from flask_login import current_user, login_required

from app.blueprints.cliente import bp
from app.decorators import role_required
from app.models.metrica_diaria import MetricaDiaria


@bp.route("/painel")
@login_required
@role_required("cliente")
def painel():
    from app.services.metabase_embed import generate_embed_url

    empresa_id = current_user.empresa_id
    periodo_inicio = request.args.get(
        "periodo_inicio", (date.today() - timedelta(days=30)).isoformat()
    )
    periodo_fim = request.args.get("periodo_fim", date.today().isoformat())

    has_data = MetricaDiaria.query.filter_by(empresa_id=empresa_id).first() is not None
    if not has_data:
        return render_template("cliente/painel_vazio.html")

    dashboard_id = current_app.config["METABASE_DASHBOARD_ID"]
    embed_url = generate_embed_url(dashboard_id, str(empresa_id))

    return render_template(
        "cliente/painel.html",
        embed_url=embed_url,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
    )


@bp.route("/painel/pdf")
@login_required
@role_required("cliente")
def painel_pdf():
    from app.services.pdf_export import gerar_pdf_painel

    empresa_id = current_user.empresa_id
    periodo_inicio = request.args.get("periodo_inicio")
    periodo_fim = request.args.get("periodo_fim")

    if not periodo_inicio or not periodo_fim:
        periodo_fim = date.today().isoformat()
        periodo_inicio = (date.today() - timedelta(days=30)).isoformat()

    pdf_bytes = gerar_pdf_painel(empresa_id, periodo_inicio, periodo_fim)
    filename = f"relatorio_{date.today().strftime('%Y%m%d')}.pdf"

    return Response(
        pdf_bytes,
        content_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
