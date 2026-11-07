from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.blueprints.auth import bp
from app.blueprints.auth.forms import LoginForm, RegistroForm
from app.extensions import db
from app.models.usuario import Usuario


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_by_perfil(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_senha(form.senha.data):
            if usuario.status != "ativo":
                flash(
                    "Sua conta ainda não foi aprovada. Aguarde a aprovação do administrador.",
                    "error",
                )
                return render_template("auth/login.html", form=form)
            login_user(usuario)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return _redirect_by_perfil(usuario)
        flash("Email ou senha incorretos.", "error")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return _redirect_by_perfil(current_user)

    form = RegistroForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash("Este email já está cadastrado.", "error")
            return render_template("auth/registro.html", form=form)

        usuario = Usuario(
            email=form.email.data,
            nome=form.nome.data,
            perfil="gestor",
            status="pendente",
        )
        usuario.set_senha(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        flash("Cadastro realizado. Aguarde aprovação do administrador.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/registro.html", form=form)


@bp.route("/privacidade")
def privacidade():
    return render_template("auth/privacidade.html")


@bp.route("/termos")
def termos():
    return render_template("auth/termos.html")


def _redirect_by_perfil(usuario):
    if usuario.perfil in ("gestor_dono", "gestor"):
        return redirect(url_for("gestor.clientes"))
    return redirect(url_for("cliente.painel"))
