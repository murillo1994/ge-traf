from flask import Blueprint

bp = Blueprint(
    "leads", __name__, url_prefix="/leads", template_folder="../../templates/leads"
)

from app.blueprints.leads import routes  # noqa: F401
