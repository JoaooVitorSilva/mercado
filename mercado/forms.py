from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from mercado.models import User, Item # Importar Item também

class CadastroForm(FlaskForm):
    def validate_username(self, check_user):
        user = User.query.filter_by(usuario=check_user.data).first()
        if user:
            raise ValidationError("Usuario já existe! Cadastre outro usuário.")
        
    def validate_email(self, check_email):
        email = User.query.filter_by(email=check_email.data).first()
        if email:
            raise ValidationError("E-mail já existe! Cadastre outro e-mail.")
        
        # Nova validação para permitir apenas um usuário administrador
        if check_email.data.endswith('@admin.com'):
            # Verifica se já existe algum usuário com o domínio @admin.com
            admin_user_exists = User.query.filter(User.email.like('%@admin.com')).first()
            if admin_user_exists:
                raise ValidationError("Já existe um usuário administrador cadastrado. Não é permitido cadastrar mais de um.")
        
    # A validação de senha no forms.py não é ideal assim, pois verifica a senha criptografada
    # na base de dados. O Flask-Bcrypt já cuida da criptografia e comparação.
    # Vou remover essa validação para evitar confusão, pois ela não faz sentido aqui.
    # def validate_senha(self, check_senha):
    #     senha = User.query.filter_by(senha=check_senha.data).first()
    #     if senha:
    #         raise ValidationError("Senha já existe! Cadastre outra senha.")

    usuario = StringField(label='Username:', validators=[Length(min=2, max=30), DataRequired()])
    email = StringField(label='E-mail:', validators=[Email(), DataRequired()])
    senha1 = PasswordField(label='Senha:', validators=[Length(min=6), DataRequired()])
    senha2 = PasswordField(label='Confirmação de Senha:', validators=[EqualTo('senha1'), DataRequired()])
    submit = SubmitField(label='Cadastrar')

class LoginForm(FlaskForm):
    usuario = StringField(label="Usuário:", validators=[DataRequired()])
    senha = PasswordField(label="Senha:", validators=[DataRequired()])
    submit = SubmitField(label="Log In")

class CompraProdutoForm(FlaskForm):
    submit = SubmitField(label="Comprar Produto!")

class VendaProdutoForm(FlaskForm):
    submit = SubmitField(label="Vender Produto!")

# Novo formulário para adicionar produtos
class AdicionarProdutoForm(FlaskForm):
    def validate_nome(self, check_nome):
        # Valida se já existe um produto com o mesmo nome
        item = Item.query.filter_by(nome=check_nome.data).first()
        if item:
            raise ValidationError("Já existe um produto com este nome! Por favor, escolha outro.")

    def validate_cod_barra(self, check_cod_barra):
        # Valida se já existe um produto com o mesmo código de barras
        item = Item.query.filter_by(cod_barra=check_cod_barra.data).first()
        if item:
            raise ValidationError("Já existe um produto com este código de barras! Por favor, insira outro.")

    nome = StringField(label='Nome do Produto:', validators=[Length(min=2, max=30), DataRequired()])
    preco = IntegerField(label='Preço:', validators=[DataRequired()])
    cod_barra = StringField(label='Código de Barras:', validators=[Length(min=12, max=12), DataRequired()])
    descricao = TextAreaField(label='Descrição:', validators=[Length(min=10, max=1024), DataRequired()])
    submit = SubmitField(label='Adicionar Produto')
