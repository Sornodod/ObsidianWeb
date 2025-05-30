# ObsidianWeb
Web-интерфейс Obsidian Date Base

# Цель создания
Цель создания - развернуть web-интерфейс для Obsidian. 
\
Все файлы расположенные в данном репозитории являются прототипом. В следствие чего могут быть не полностью работоспособны. 

# Вводные данные

Hardware: 
* Одноплатник [`Orange Pi Zero 2W 2Gb`](https://www.ozon.ru/product/mikrokompyuter-orange-pi-zero-2w-2gb-1575206629/) (опционально).


Sofware:
* OS: [`Armbian_community 25.5.0-trunk.367 bookworm aarch64`](https://dl.armbian.com/orangepizero2w/Bookworm_current_minimal)
* syncthing;
* flask;
* markdown;
* pyTelegramBotAPI;
* Pygments;
* openssl.


# Шаги развёртки на Linux Debian
## Шаг №1. Клонирование репозитория.
Сначала клонируем наш чудесный репозиторий:
```shell
git clone https://github.com/Sornodod/ObsidianWeb.git
```

## Шаг №2. Установка сертификатов.
Устанавливаем сертификаты, что бы нашу ссылку http превратить в подобие https. Дабы Telegra API не ругался и запустил нашего монстра Франкенштейна. \
Для них мы создаём папку:
```shell
mkdir Cert
```
И переходим в неё:
```shell
cd Cert
```
В конечном счёте наш проект должен иметь вот такую структуру:
```cpp
ObsidianWeb/
│
├── app.py
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
└── Cert/
```
И создаёи сами серты:
```shell
openssl genpkey -algorithm RSA -out server-key.pem
openssl req -new -key server-key.pem -out server.csr
openssl x509 -req -in server.csr -signkey server-key.pem -out server-cert.pem
```
## Шаг №3. Установка библиотек
Устанавливаем Syncthing:
```shell
sudo apt update
sudo apt install syncthing
```
Syncthing опционален. В рамках этого проекта можно полностью обойтись и без него. Просто с ним, можно бесплатно синхронизировать БД Obsidian между устройствами. 

Устанавливаем теперь библиотеки. Правда для этого нужно будет развернуть виртуальное окружение сначала:
```shell
python3 -m venv venv
source venv/bin/activate
```
И вот теперь мы ставим библиотеки. \
Flask-сервер:
```shell
pip install flask
```
Поддержку разметки markdown:
```shell
pip install markdown
```
Библиотеку для работы с Telegram:
```shell
pip install pyTelegramBotAPI
```
Подсветку синтаксиа кода в статьях Obsidian. Не обязательно, но оно работало у меня в первых версиях... Работало. Сейчас не работает.
```shell
pip install Pygments
```

## Шаг №4. Редактирование кода.
Идём в файл `app.py`. Нас там интересуют следующие вещи: 
1. **Строка 11** - написать свой путь до базы Obsidian. Достаточно просто до папки; 
2. **Строка 17** - написать свой токен Telegram. Получить его можно у @BotFather; 
3. **Строка 21** - напистаь свой Telegram ID. Получить его можно у @getmyid_bot; 
4. **Строка 25** - указать адрес своего сервера. Достаточно и адреса ПК или микро-компьютера где всё это будет хранится\крутится; 
5. **Строка 129** - указать адрес где лежат сертификаты созданные в шаге №2. 


## Шаг №5. Автозапуск.
Создаём файл службы:
```shell
sudo nano /etc/systemd/system/obsidian-webapp.service
```
Пихуем туда вот это:
```ini
[Unit]
Description=Obsidian WebApp
After=network.target

[Service]
[Service]
User=root
WorkingDirectory=/root/SornSoft/ObsidianWeb/WebApp
ExecStart=/root/SornSoft/ObsidianWeb/WebApp/venv/bin/python /root/SornSoft/ObsidianWeb/WebApp/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```
И кидаем в автозапуск:
```shell
sudo systemctl daemon-reload
sudo systemctl enable obsidian-webapp.service
sudo systemctl start obsidian-webapp.service
sudo systemctl status obsidian-webapp.service
```
