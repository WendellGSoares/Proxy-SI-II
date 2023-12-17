from flask import Flask, render_template, request, make_response, session, url_for, redirect
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, quote
import re

app = Flask(__name__)
app.secret_key = "proxy"

urldoProxy = '/meuproxy/'

def filtrar_conteudo(conteudo):
    
    palavras_ofensivas = {'Desemprego menor': 'Vitor desempregado', 'Bosta': 'alternativa2', 'palavra3': 'alternativa3'}

    for ofensiva, correta in palavras_ofensivas.items():
        conteudo = re.sub(r'\b' + re.escape(ofensiva) + r'\b', correta, conteudo, flags=re.IGNORECASE)

    return conteudo

def trocaLink(conteudodoSite, urldoProxy):
    soup = BeautifulSoup(conteudodoSite, 'html.parser')

    for link in soup.find_all('a', href=True):
        linkdoSite = link['href']

        urlFinal = urljoin(urldoProxy, linkdoSite)

        trataCaracterUrl = quote(urlFinal)

        link['href'] = trataCaracterUrl

    return str(soup)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST" and request.form["idade"] != "":
        session["idade"] = request.form["idade"]
        print(session['idade'])
        return redirect(url_for("site"))
    return render_template('index.html')

@app.route('/site')
def site():
    return render_template('site.html')


@app.route('/meuproxy/<path:encoded_url>', methods=['GET'])
def meu_proxy(encoded_url):
    if encoded_url:
        try:
            urldoSite = unquote(encoded_url)

            response = requests.get(urldoSite)
            response.raise_for_status()

            conteudodoSite = response.text
            
            if int(session['idade']) <= 18:
                conteudodoSite = filtrar_conteudo(conteudodoSite)
            linksModificados = trocaLink(conteudodoSite, urldoSite)

            response = make_response(linksModificados)
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição para {urldoSite}: {e}")
            session['erro'] = f"Erro na requisição para {urldoSite}: {e}"
            return redirect(url_for('erro'))

    else:
        session['erro'] = 'URL não fornecida.'
        return redirect(url_for('erro'))

@app.route('/erro')
def erro():
    return render_template('erro.html')

if __name__ == "__main__":
    app.run(debug=True)