from flask import Flask, jsonify, request, render_template
from pathlib import Path
import markdown
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

app = Flask(__name__)

# Путь к базе знаний
BASE_PATH = Path(r"/home//ObsidianDB/MyObsidian") # ПОМЕНЯТЬ! Поменять адрес на свой

# История открытых файлов (для кнопки "Назад")
history_stack = []

# Инициализация Telegram бота
TOKEN = 'СЮДА_ТОКЕН' # Можно получить у бота @BotFather
bot = telebot.TeleBot(TOKEN)

# ID авторизации
ALLOWED_USER_ID = 1234567890 # ПОМЕНЯТЬ! ID-шник нужно свой указать тут. IDшник берётся у бота @getmyid_bot. Всё это нужно для того, что бы бот общался только с нами и не с кем другим.

# Создаем клавиатуру для Telegram WebApp
def create_webapp_button():
    web_app_url = "https://192.168.31.216:5000"  # Вот тут нужно поставить адрес своего сервера где крутится приложение. У меня это OrangePi со своим локальным адресом, посему и такой ip.
    keyboard = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton("Open Web App", web_app=WebAppInfo(url=web_app_url))
    keyboard.add(web_app_button)
    return keyboard

# Построение навигационного дерева файлов и папок
def build_tree(current_path: Path):
    tree = []
    for item in sorted(current_path.iterdir()):
        if item.name.startswith('.'):
            continue
        node = {
            'name': item.name,
            'path': str(item.relative_to(BASE_PATH)),
        }
        if item.is_dir():
            node['type'] = 'folder'
            node['children'] = build_tree(item)
        elif item.suffix == '.md':
            node['type'] = 'file'
        else:
            continue
        tree.append(node)
    return tree

# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

# API для получения дерева
@app.route("/api/tree")
def get_tree():
    return jsonify(build_tree(BASE_PATH))

# API для получения содержимого файла
@app.route("/api/file")
def get_file():
    rel_path = request.args.get("path", "")
    abs_path = os.path.join(BASE_PATH, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Получаем название статьи из имени файла (без расширения .md)
        title = os.path.basename(abs_path).replace(".md", "")

        # Подключаем подсветку синтаксиса (Нихуя не работает)
        md = markdown.Markdown(extensions=["fenced_code", "codehilite"])
        html_content = md.convert(content)

        # Отправляем HTML и название
        push_to_history(rel_path)
        return jsonify({"html": html_content, "title": title})
    except Exception as e:
        return jsonify({"html": f"<p>Ошибка: {str(e)}</p>", "title": "Ошибка"})

# API для возврата к предыдущей статье
@app.route("/api/back")
def go_back():
    if len(history_stack) > 1:
        history_stack.pop()  # Удаляем текущую
        previous_path = history_stack[-1]  # Берём предыдущую
        return get_file_from_history(previous_path)
    return jsonify({"html": "<p>Нет предыдущих файлов.</p>", "title": "Нет предыдущих файлов"})

# Получение содержимого из истории
def get_file_from_history(path):
    file_path = BASE_PATH / path
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    html_content = markdown.markdown(content, extensions=["fenced_code", "tables"])
    # Извлекаем название статьи из имени файла (без расширения .md). Это нам нужно что бы в web-интерфейсе у статьи было название.
    title = os.path.basename(file_path).replace(".md", "")
    return jsonify({"html": html_content, "title": title})

# Добавление файла в историю
def push_to_history(path):
    if not history_stack or history_stack[-1] != path:
        history_stack.append(path)

# Запуск Telegram бота
@bot.message_handler(commands=['start'])
def start(message):
    # Проверяем ID пользователя. ID-шник свой можно получить у @getmyid_bot
    if message.from_user.id == ALLOWED_USER_ID:
        keyboard = create_webapp_button()
        bot.send_message(
            message.chat.id,
            "ТЕСТОВОЕ WEB-ПРИЛОЖЕНИЕ",
            reply_markup=keyboard
        )
    else:
        bot.send_message(
            message.chat.id,
            "Тебе нельзя пользоваться этим ботом."
        )

# Запуск Flask-сервера
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  
        port=5000,
        ssl_context=(os.path.expanduser("~/Cert/server-cert.pem"), os.path.expanduser("~/Cert/server-key.pem"))
    )
    bot.polling(non_stop=True)
