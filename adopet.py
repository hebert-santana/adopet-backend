from flask import Flask, render_template, request, redirect, session, flash
import pyodbc
from functools import wraps


app = Flask(__name__)
app.secret_key = 'galo'

def login_required(f):
    @wraps(f)
    def decorated_user_logado(*args, **kwargs):
        rotas_permitidas = ['/', '/login', '/cadastro']
        if 'usuario_logado' not in session or session['usuario_logado'] is None:
            if request.path not in rotas_permitidas:
                flash('Usuário não logado')
                return redirect('/login')
        return f(*args, **kwargs)
    return decorated_user_logado

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404



# conectar ao DB
def connection():
    s = 'hebert'
    d = 'AdoPet' 
    cstr = 'DRIVER={SQL Server};SERVER='+s+';DATABASE='+d
    conn = pyodbc.connect(cstr)
    return conn

# adiciona usuario no DB
@app.route("/adduser", methods = ['POST',])
def adduser():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        senha = request.form['senha']
        senha_confirme = request.form['senha-confirme']
        if senha == senha_confirme:
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO dbo.Usuarios (Nome, Email, Senha) VALUES (?, ?, ?)", nome, email, senha)
            conn.commit()
            conn.close()
            flash('Usuário Gerado!')            
            return redirect('/login')
        else:
            flash('Senhas Diferentes!')
            return redirect('/cadastro')
        
# LOGIN/LOGOUT
@app.route('/logar', methods=['POST',])
def fazerLogin():
    email = request.form['email']
    senha = request.form['senha']    
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Senha FROM dbo.Usuarios WHERE Email=?", email)
    row = cursor.fetchone()
    if row is not None and row[0] == senha:
        session['usuario_logado'] = email
        flash('Logado com sucesso!')
        return redirect('/home')
    else:
        flash('E-mail ou senha incorretos!')
        return redirect('/login')

    
@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Deslogado')
    return redirect('/')
            



# rotas
@app.route('/')
def boasVindas():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/mensagem')
@login_required
def mensagem():
    return render_template('mensagem.html')

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')

    
    
app.run(debug=True)