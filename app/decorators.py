from functools import wraps

from flask import abort
from flask_login import current_user

from app.models.empresa import Empresa


def role_required(*perfis):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.perfil not in perfis:
                abort(403)
            if current_user.status != "ativo":
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator


def empresa_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        empresa_id = kwargs.get("empresa_id") or kwargs.get("id")
        if not empresa_id:
            abort(400)

        empresa = Empresa.query.get_or_404(empresa_id)

        if current_user.perfil == "gestor_dono":
            pass
        elif current_user.perfil == "gestor":
            if str(empresa.gestor_id) != str(current_user.id):
                abort(403)
        elif current_user.perfil == "cliente":
            if str(current_user.empresa_id) != str(empresa.id):
                abort(403)
        else:
            abort(403)

        kwargs["empresa"] = empresa
        return f(*args, **kwargs)

    return wrapped
