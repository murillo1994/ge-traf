import click
from flask import Flask, redirect, render_template, url_for

from app.config import config
from app.extensions import db, init_fernet, login_manager, migrate


def create_app(config_name="default"):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config[config_name])

    from werkzeug.middleware.proxy_fix import ProxyFix

    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)
    init_fernet(flask_app.config.get("FERNET_KEY"))

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.cliente import bp as cliente_bp
    from app.blueprints.gestor import bp as gestor_bp
    from app.blueprints.leads import bp as leads_bp

    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(gestor_bp)
    flask_app.register_blueprint(cliente_bp)
    flask_app.register_blueprint(leads_bp)

    from app.models import (  # noqa: F401
        ContaAnuncio,
        Empresa,
        Lead,
        LogAuditoria,
        MetricaDiaria,
        Usuario,
    )

    @flask_app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @flask_app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @flask_app.route("/")
    def index():
        from flask_login import current_user

        if current_user.is_authenticated:
            from app.blueprints.auth.routes import _redirect_by_perfil

            return _redirect_by_perfil(current_user)
        return redirect(url_for("auth.login"))

    _register_cli(flask_app)
    return flask_app


def _register_cli(flask_app):
    @flask_app.cli.command("create-owner")
    @click.option("--email", prompt=True)
    @click.option("--nome", prompt=True)
    @click.option("--senha", prompt=True, hide_input=True)
    def create_owner(email, nome, senha):
        from app.models.usuario import Usuario

        if Usuario.query.filter_by(email=email).first():
            click.echo(f"Usuário {email} já existe.")
            return
        u = Usuario(email=email, nome=nome, perfil="gestor_dono", status="ativo")
        u.set_senha(senha)
        db.session.add(u)
        db.session.commit()
        click.echo(f"Gestor dono {email} criado com sucesso.")

    @flask_app.cli.command("sync-metricas")
    def sync_metricas_cmd():
        from app.services.sync_metricas import sync_todas

        sync_todas()
        click.echo("Sincronização de métricas concluída.")
