from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import time

# --- Configuração da Aplicação ---
app = Flask(__name__)
# Cria um banco de dados simples arquivo local 'sites.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sites.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 1. MODELO (Banco de Dados) ---
# Aqui definimos a "tabela" onde os sites serão salvos
class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)

# --- 2. FUNÇÃO AUXILIAR (A Lógica de Redes) ---
def checar_status(url):
    """
    Tenta acessar o site e retorna um dicionário com os dados.
    Simula um 'ping' HTTP.
    """
    try:
        inicio = time.time()
        # timeout=5 impede que o app trave se o site demorar muito
        response = requests.get(url, timeout=5)
        fim = time.time()
        
        tempo = round((fim - inicio) * 1000) # Converte para milissegundos
        
        # Define a cor baseada no status code
        if response.status_code == 200:
            status_text = "Online"
            css_class = "success" # Verde
        else:
            status_text = f"Erro {response.status_code}"
            css_class = "warning" # Amarelo
            
        return {
            "status_code": response.status_code,
            "latency": tempo,
            "status_text": status_text,
            "css_class": css_class
        }

    except requests.exceptions.ConnectionError:
        return {"status_code": "Falha", "latency": 0, "status_text": "Offline/DNS", "css_class": "danger"}
    except requests.exceptions.Timeout:
        return {"status_code": "Timeout", "latency": ">5000", "status_text": "Lento", "css_class": "danger"}
    except Exception as e:
        return {"status_code": "Erro", "latency": 0, "status_text": "Erro Desconhecido", "css_class": "danger"}

# --- 3. ROTAS (Controller) ---

@app.route('/')
def index():
    # Pega todos os sites salvos no banco
    sites_db = Site.query.all()
    
    # Lista para enviar ao HTML
    sites_monitorados = []
    
    # Para cada site no banco, fazemos a verificação em tempo real
    for site in sites_db:
        dados_rede = checar_status(site.url)
        sites_monitorados.append({
            "id": site.id,
            "nome": site.nome,
            "url": site.url,
            **dados_rede # Desempacota o dicionário de rede aqui
        })
        
    return render_template('index.html', sites=sites_monitorados)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form.get('nome')
    url = request.form.get('url')
    
    if nome and url:
        # Garante que a URL tenha http/https
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        novo_site = Site(nome=nome, url=url)
        db.session.add(novo_site)
        db.session.commit()
        
    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    site = Site.query.get_or_404(id)
    db.session.delete(site)
    db.session.commit()
    return redirect(url_for('index'))

# --- Inicialização ---
if __name__ == '__main__':
    # Cria as tabelas no banco se não existirem
    with app.app_context():
        db.create_all()
    app.run(debug=True)