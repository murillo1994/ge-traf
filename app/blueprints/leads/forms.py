from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class LeadStatusForm(FlaskForm):
    novo_status = SelectField(
        "Novo Status",
        choices=[
            ("novo", "Novo"),
            ("orcamento", "Orçamento"),
            ("contrato", "Contrato"),
            ("perdido", "Perdido"),
        ],
        validators=[DataRequired()],
    )
    valor_contrato = DecimalField(
        "Valor do Contrato (R$)",
        validators=[Optional(), NumberRange(min=0.01)],
        places=2,
    )
    submit = SubmitField("Atualizar")
