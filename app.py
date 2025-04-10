from flask import Flask, render_template, request, url_for, abort, session, redirect
import os
import markdown
import urllib.parse

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Убедитесь, что у вас есть секретный ключ для сессий

# Путь к вашей базе Obsidian
OBSIDIAN_VAULT = r'E:\ObsidianDataBase\BackupSornMind\SornMind'


def is_safe_path(base_path, target_path):
    """Проверка, что целевой путь находится внутри базового каталога (SornMind)"""
    base_path = os.path.abspath(base_path)
    target_path = os.path.abspath(target_path)
    return os.path.commonpath([base_path]) == os.path.commonpath([base_path, target_path])


def get_folder_structure(path):
    """Получаем структуру каталогов и файлов"""
    folder_structure = []
    for root, dirs, filenames in os.walk(path):
        folder_structure.append({
            'path': root,
            'folders': dirs,
            'files': filenames
        })
        break
    return folder_structure


@app.route('/')
def index():
    folder_structure = get_folder_structure(OBSIDIAN_VAULT)
    return render_template('index.html', folder_structure=folder_structure)


@app.route('/folder/<path:folder_path>')
def folder(folder_path):
    # Декодируем путь, чтобы избежать ошибок с URL
    folder_path = urllib.parse.unquote(folder_path)

    # Получаем полный путь
    full_path = os.path.abspath(os.path.join(OBSIDIAN_VAULT, folder_path))

    # Сохраняем текущий путь в сессии для кнопки "Назад"
    session['previous_folder'] = folder_path

    # Проверка на безопасность пути
    if not is_safe_path(OBSIDIAN_VAULT, full_path):
        abort(403)  # Возвращаем ошибку доступа

    folder_structure = get_folder_structure(full_path)
    files = []

    for root, dirs, filenames in os.walk(full_path):
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                    html_content = markdown.markdown(md_content, extensions=['nl2br'])
                files.append({'title': os.path.splitext(filename)[0], 'content': html_content})
        break

    # Путь к текущей папке относительно OBSIDIAN_VAULT
    relative_path = os.path.relpath(full_path, OBSIDIAN_VAULT)

    # Проверяем существует ли родительская папка
    parent_folder = os.path.dirname(relative_path)
    parent_folder_path = os.path.join(OBSIDIAN_VAULT, parent_folder)

    # Убедимся, что родительская папка существует
    if not os.path.exists(parent_folder_path) or parent_folder == ".":
        show_back_button = False  # Кнопка "Назад" не показывается в корневой папке
    else:
        show_back_button = True

    return render_template(
        'folder.html',
        files=files,
        folder_structure=folder_structure,
        show_back_button=show_back_button,
        current_folder=relative_path.replace("\\", "/"),
        parent_folder=urllib.parse.quote(parent_folder.replace("\\", "/"))  # Кодируем путь
    )


@app.route('/back')
def back():
    previous_folder = session.get('previous_folder', '')  # Получаем путь из сессии
    if previous_folder:
        # Выполняем редирект на предыдущую папку
        return redirect(url_for('folder', folder_path=previous_folder))
    else:
        # Если предыдущий путь не найден, редиректим на главную
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
