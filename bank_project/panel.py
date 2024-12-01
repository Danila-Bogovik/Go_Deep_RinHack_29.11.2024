import os
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

# Инициализация Flask приложения
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ключ для безопасной работы с flash-сообщениями

UPLOAD_FOLDER = 'uploads'  # Папка для загружаемых файлов
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Создаем папку для загрузок, если она не существует
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Главная страница
@app.route('/')
def index():
    # Получение списка файлов в папке загрузок
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('bank-interface.html', files=files)


# Загрузка файлов
@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')  # Получение списка файлов из запроса

    for file in files:
        if file:
            filename = secure_filename(file.filename)  # Обезопасить имя файла
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Сохранить файл

    flash('Файлы успешно загружены!')  # Сообщение пользователю
    return redirect(url_for('index'))


# Скачивание файлов
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# Удаление файлов
@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        os.remove(file_path)  # Удалить файл
        flash(f'Файл {filename} успешно удален!')
    else:
        flash(f'Файл {filename} не найден!')

    return redirect(url_for('index'))


# Показ содержимого файла
@app.route('/view/<filename>')
def view(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()  # Прочитать содержимое файла

        return render_template('view.html', filename=filename, content=content)
    else:
        flash(f'Файл {filename} не найден!')
        return redirect(url_for('index'))


# Главный обработчик
if __name__ == '__main__':
    app.run(debug=True)
