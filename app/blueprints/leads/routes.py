from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.blueprints.leads import bp
from app.blueprints.leads.forms import LeadStatusForm
from app.decorators import empresa_required, role_required
from app.extensions import db
from app.models.lead import Lead
from app.services import auditoria


@bp.route("/<uuid:empresa_id>")
@login_required
@role_required("gestor", "gestor_dono", "cliente")
@empresa_required
def lista(empresa_id, empresa=None):
    status_filter = request.args.get("status")
    page = request.args.get("pagina", 1, type=int)

    query = Lead.query.filter_by(empresa_id=empresa_id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    leads = query.order_by(Lead.criado_em.desc()).paginate(
        page=page,
        per_page=25,
        error_out=False,
    )

    form = LeadStatusForm()
    return render_template(
        "leads/lista.html",
        leads=leads,
        empresa=empresa,
        status_filter=status_filter,
        form=form,
    )


@bp.route("/<uuid:lead_id>/status", methods=["POST"])
@login_required
@role_required("gestor", "gestor_dono", "cliente")
def atualizar_status(lead_id):
    lead = Lead.query.get_or_404(lead_id)

    if current_user.perfil == "cliente":
        if str(current_user.empresa_id) != str(lead.empresa_id):
            from flask import abort

            abort(403)
    elif current_user.perfil == "gestor":
        from app.models.empresa import Empresa

        empresa = Empresa.query.get(lead.empresa_id)
        if str(empresa.gestor_id) != str(current_user.id):
            from flask import abort

            abort(403)

    form = LeadStatusForm()
    if form.validate_on_submit():
        novo_status = form.novo_status.data
        valor = form.valor_contrato.data

        if not lead.pode_transicionar_para(novo_status):
            flash(
                f'Transição de "{lead.status}" para "{novo_status}" não é permitida.',
                "error",
            )
            return redirect(url_for("leads.lista", empresa_id=lead.empresa_id))

        if novo_status == "contrato" and (not valor or valor <= 0):
            flash('Valor do contrato é obrigatório para status "Contrato".', "error")
            return redirect(url_for("leads.lista", empresa_id=lead.empresa_id))

        dados_anteriores = {
            "status": lead.status,
            "valor_contrato": str(lead.valor_contrato) if lead.valor_contrato else None,
        }
        lead.status = novo_status
        if novo_status == "contrato":
            lead.valor_contrato = valor

        dados_novos = {
            "status": lead.status,
            "valor_contrato": str(lead.valor_contrato) if lead.valor_contrato else None,
        }

        db.session.commit()

        auditoria.registrar_acao(
            empresa_id=lead.empresa_id,
            usuario_id=current_user.id,
            acao="lead_status_alterado",
            entidade_tipo="lead",
            entidade_id=lead.id,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
        )

        flash("Status do lead atualizado com sucesso.", "success")
    return redirect(url_for("leads.lista", empresa_id=lead.empresa_id))
