from mercado import app
from flask import render_template, redirect, url_for, flash, request
from mercado.models import Item, User
from mercado.forms import CadastroForm, LoginForm, CompraProdutoForm, VendaProdutoForm, AdicionarProdutoForm
from mercado import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
def page_home():
    return render_template("home.html")

@app.route('/Produtos', methods=["GET", "POST"])
@login_required
def page_produto():
    compra_form = CompraProdutoForm()
    venda_form = VendaProdutoForm()
    if request.method == "POST":
        # Compra Produto
        compra_produto = request.form.get('compra_produto')
        produto_obj = Item.query.filter_by(nome=compra_produto).first()
        if produto_obj:
            if current_user.compra_disponivel(produto_obj):
                produto_obj.compra(current_user)
                flash(f"Parabéns! Você comprou o produto {produto_obj.nome}", category="success")
            else:
                flash(f"Você não possui saldo suficiente para comprar o produto{produto_obj.nome}", category="danger")
        # Venda Produto
        venda_produto = request.form.get('venda_produto')
        produto_obj_venda = Item.query.filter_by(nome=venda_produto).first()
        if produto_obj_venda:
            if current_user.venda_disponivel(produto_obj_venda):
                produto_obj_venda.venda(current_user)
                flash(f"Parabéns! Você vendeu o produto {produto_obj_venda.nome}", category="success")
            else:
                flash(f"Algo deu errado com a venda do produto {produto_obj_venda.nome}", category="danger")
        return redirect(url_for('page_produto'))
    if request.method == "GET":
        itens = Item.query.filter_by(dono=None)
        dono_itens = Item.query.filter_by(dono=current_user.id)
        return render_template("produtos.html", itens=itens, compra_form=compra_form, dono_itens=dono_itens, venda_form=venda_form)

@app.route('/cadastro', methods=['GET', 'POST'])
def page_cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        usuario = User(
            usuario = form.usuario.data,
            email = form.email.data,
            senhacrip = form.senha1.data
        )

        db.session.add(usuario)
        db.session.commit()
        flash(f"Conta criada com sucesso para o usuário: {usuario.usuario}", category="success")
        login_user(usuario)
        return redirect(url_for('page_produto'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f"Erro ao cadastrar usuário: {err}", category="danger")
    return render_template("cadastro.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def page_login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario_logado = User.query.filter_by(usuario=form.usuario.data).first()
        if usuario_logado and usuario_logado.converte_senha(senha_texto_claro=form.senha.data):
            login_user(usuario_logado)
            flash(f'Sucesso! Seu login: {usuario_logado.usuario}', category='success')
            return redirect(url_for('page_produto'))
        else:
            flash(f'Usuário ou senha estão incorretos! Tente novamente.', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def page_logout():
    logout_user()
    flash("Você fez o logout", category="info")
    return redirect(url_for("page_home"))

# Rota para a página de administração de produtos
@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required # Apenas usuários logados podem acessar
def page_add_product():
    # Verifica se o usuário logado é um administrador
    if not current_user.is_admin:
        flash("Você não tem permissão para acessar esta página.", category="danger")
        return redirect(url_for('page_home')) # Redireciona para a home ou outra página

    form = AdicionarProdutoForm()
    if form.validate_on_submit():
        try:
            novo_produto = Item(
                nome=form.nome.data,
                preco=form.preco.data,
                cod_barra=form.cod_barra.data,
                descricao=form.descricao.data,
                dono=None # Produtos adicionados pelo admin não têm dono inicialmente
            )
            db.session.add(novo_produto)
            db.session.commit()
            flash(f"Produto '{novo_produto.nome}' adicionado com sucesso!", category="success")
            return redirect(url_for('page_add_product'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao adicionar produto: {e}", category="danger")
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"Erro ao adicionar produto: {err_msg}", category="danger")
    
    return render_template('add_product.html', form=form)
