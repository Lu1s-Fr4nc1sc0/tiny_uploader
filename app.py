from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, send_from_directory
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret_key'  # Substitua por uma chave segura

# Configurações
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg',
                      'jpeg', 'gif', 'mp4', 'zip',
                      'csv','iso','rar','odf','odt',
                      'word','rtf','doc','docx','dotx',
                      'xls','xlsx','ppt','pptx','htm','html',
                      'tar.gz','mkv','sh','zsh','js'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * (1024**3)  # 1 GB

# Arquivo para armazenar descrições
DESCRIPTIONS_FILE = os.path.join(DATA_FOLDER, 'descriptions.json')

# Cria um arquivo JSON vazio, se não existir
if not os.path.exists(DESCRIPTIONS_FILE):
    with open(DESCRIPTIONS_FILE, 'w') as f:
        json.dump({}, f)

# Função para verificar o tipo de arquivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## Carregar ou criar o arquivo de descrições
if not os.path.exists(DESCRIPTIONS_FILE):
    with open(DESCRIPTIONS_FILE, 'w') as f:
        json.dump({}, f)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def load_descriptions():
    """Carrega descrições do arquivo JSON."""
    with open(DESCRIPTIONS_FILE, 'r') as f:
        return json.load(f)


def save_descriptions(data):
    """Salva descrições no arquivo JSON."""
    with open(DESCRIPTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    descriptions = load_descriptions()
    return render_template('index.html',files=files,descriptions=descriptions,extensions=ALLOWED_EXTENSIONS)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return redirect(url_for('index'))


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        # Remove a descrição associada ao arquivo
        descriptions = load_descriptions()
        if filename in descriptions:
            del descriptions[filename]
            save_descriptions(descriptions)
        return redirect(url_for('index'))
    return "Arquivo não encontrado", 404


@app.route('/description/<filename>', methods=['POST'])
def add_description(filename):
    descriptions = load_descriptions()
    description = request.form.get('description', '').strip()
    descriptions[filename] = description
    save_descriptions(descriptions)
    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename,as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
