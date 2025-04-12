from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Projekt zaliczeniowy - Azure</h1><p>Witaj w aplikacji Python!</p>"

@app.route('/azure')
def azure():
    return "<h1>Aplikacja Azure</h1><p>Wdrożono z repo: aplikacja_azure</p>"

if __name__ == '__main__':
    app.run(debug=True)