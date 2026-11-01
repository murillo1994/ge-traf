from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


class RegistroForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=8)])
    confirmar_senha = PasswordField(
        "Confirmar Senha",
        validators=[
            DataRequired(),
            EqualTo("senha", message="As senhas devem ser iguais."),
        ],
    )
    submit = SubmitField("Cadastrar")
