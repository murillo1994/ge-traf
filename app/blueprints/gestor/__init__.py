from flask import Blueprint

bp = Blueprint(
    "gestor", __name__, url_prefix="/gestor", template_folder="../../templates/gestor"
)

from app.blueprints.gestor import routes  # noqa: F401
