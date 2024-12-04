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
                      'tar.gz','mkv','sh','zsh'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1 GB

# Arquivo para armazenar descrições
DESCRIPTIONS_FILE = os.path.join(DATA_FOLDER, 'descriptions.json')

# Cria um arquivo JSON vazio, se não existir
if not os.path.exists(DESCRIPTIONS_FILE):
    with open(DESCRIPTIONS_FILE, 'w') as f:
        json.dump({}, f)

# Função para verificar o tipo de arquivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para carregar descrições
def load_descriptions():
    # Verifica se o arquivo existe e tenta carregá-lo
    if not os.path.exists(DESCRIPTIONS_FILE):
        # Cria um arquivo vazio, se não existir
        with open(DESCRIPTIONS_FILE, 'w') as f:
            json.dump({}, f)
        return {}

    # Tenta carregar o JSON existente
    try:
        with open(DESCRIPTIONS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Se houver erro no JSON, recria um arquivo vazio
        with open(DESCRIPTIONS_FILE, 'w') as f:
            json.dump({}, f)
        return {}


# Função para salvar descrições
def save_descriptions(data):
    try:
        with open(DESCRIPTIONS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        # Apenas para depuração, não exiba isso ao usuário final em produção
        print(f"Erro ao salvar o JSON: {e}")


@app.route('/')
def index():
    # Lista os arquivos no diretório
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    descriptions = load_descriptions()
    
    # Organiza os arquivos por extensão
    grouped_files = {}
    for file in files:
        ext = file.rsplit('.', 1)[1].lower() if '.' in file else 'unknown'
        grouped_files.setdefault(ext, []).append({
            'name': file,
            'description': descriptions.get(file, '')
        })
    
    return render_template('index.html', grouped_files=grouped_files)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        flash('Arquivo não encontrado.')
        return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado.')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Salva o arquivo diretamente no disco, sem carregar tudo na memória
        with open(filepath, 'wb') as f:
            f.write(file.read())
        
        flash(f'Arquivo {filename} enviado com sucesso!')
        return redirect(url_for('index'))

    flash('Tipo de arquivo não permitido.')
    return redirect(url_for('index'))


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    descriptions = load_descriptions()

    # Remove o arquivo e sua descrição
    if os.path.exists(filepath):
        os.remove(filepath)
        descriptions.pop(filename, None)
        save_descriptions(descriptions)
        flash(f'Arquivo {filename} deletado com sucesso!')
    else:
        flash(f'Arquivo {filename} não encontrado.')
    return redirect(url_for('index'))

@app.route('/add_description', methods=['POST'])
def add_description():
    filename = request.form.get('filename')
    description = request.form.get('description', '').strip()

    if filename:
        descriptions = load_descriptions()
        descriptions[filename] = description
        save_descriptions(descriptions)
        flash(f'Descrição para {filename} atualizada com sucesso!')
    else:
        flash('Arquivo não encontrado.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
