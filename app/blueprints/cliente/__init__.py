from flask import Blueprint

bp = Blueprint(
    "cliente",
    __name__,
    url_prefix="/cliente",
    template_folder="../../templates/cliente",
)

from app.blueprints.cliente import routes  # noqa: F401
