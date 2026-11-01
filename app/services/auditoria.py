from app.extensions import db
from app.models.log_auditoria import LogAuditoria


def registrar_acao(
    empresa_id,
    usuario_id,
    acao,
    entidade_tipo,
    entidade_id,
    dados_anteriores=None,
    dados_novos=None,
):
    log = LogAuditoria(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        acao=acao,
        entidade_tipo=entidade_tipo,
        entidade_id=entidade_id,
        dados_anteriores=dados_anteriores,
        dados_novos=dados_novos,
    )
    db.session.add(log)
    db.session.commit()
    return log
