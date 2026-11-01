from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ClienteForm(FlaskForm):
    nome = StringField("Nome da Empresa", validators=[DataRequired(), Length(max=200)])
    segmento = StringField("Segmento", validators=[Optional(), Length(max=100)])
    teto_verba_mensal = DecimalField(
        "Teto de Verba Mensal (R$)",
        validators=[Optional(), NumberRange(min=0.01)],
        places=2,
    )
    submit = SubmitField("Cadastrar")
