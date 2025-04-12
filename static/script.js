async function fetchTree() {
    const res = await fetch("/api/tree");
    const tree = await res.json();
    const treeContainer = document.getElementById("tree");
    treeContainer.innerHTML = "";
    treeContainer.appendChild(renderTree(tree));
}

let openedFolders = new Set(JSON.parse(localStorage.getItem("openedFolders") || "[]"));  // Загружаем состояние из localStorage

function renderTree(nodes) {
    const ul = document.createElement("ul");
    for (let node of nodes) {
        const li = document.createElement("li");

        if (node.type === "file") {
            const fileLink = document.createElement("a");
            fileLink.textContent = node.name;
            fileLink.href = "#";
            fileLink.onclick = (e) => {
                e.stopPropagation();  // Предотвращаем всплытие события
                loadFile(node.path);
            };
            li.appendChild(fileLink);
        } else if (node.type === "folder") {
            const folder = document.createElement("div");
            folder.classList.add("folder");
            folder.textContent = node.name;

            const nested = renderTree(node.children);
            folder.appendChild(nested);

            // Добавляем классы для отображения раскрытия
            if (openedFolders.has(node.path)) {
                folder.classList.add("open");
                nested.style.display = "block";  // Показываем содержимое папки
            } else {
                nested.style.display = "none";  // Скрываем содержимое папки
            }

            // Обработчик нажатия на папку
            folder.onclick = (e) => {
                e.stopPropagation(); // Чтобы не срабатывал клик на родительском элементе
                toggleFolder(node.path, folder, nested); // Включаем/выключаем папку
            };

            li.appendChild(folder);
        }
        ul.appendChild(li);
    }
    return ul;
}

// Функция для загрузки файла
async function loadFile(path) {
    const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
    const data = await res.json();

    // Получаем название статьи из ответа
    const articleTitle = data.title || "Без названия";  // Если название не пришло, поставим дефолтное значение

    // Вставляем заголовок в верхнюю часть контента
    const content = document.getElementById("content");
    const titleElement = document.createElement("h1");
    titleElement.textContent = articleTitle;
    titleElement.classList.add('article-title');  // Добавляем стиль для заголовка
    titleElement.style.textAlign = 'center';  // Выравниваем по центру
    content.innerHTML = '';  // Очищаем текущий контент
    content.appendChild(titleElement);  // Добавляем заголовок

    // Добавляем сам контент статьи
    content.innerHTML += data.html || "<p>Ошибка загрузки.</p>";
}

// Функция для добавления кнопок "Скопировать"
function addCopyButtons() {
    const codeBlocks = document.querySelectorAll("pre code");
    codeBlocks.forEach((block) => {
        // Создаём контейнер для блока кода и кнопки
        const codeContainer = document.createElement("div");
        codeContainer.classList.add("code-container");

        // Добавляем сам блок кода
        const codeElement = block.parentElement;

        // Добавляем кнопку для копирования
        const copyButton = document.createElement("button");
        copyButton.classList.add("copy-btn");
        copyButton.textContent = "Скопировать";

        // Обработчик клика для кнопки копирования
        copyButton.onclick = () => {
            const code = block.textContent;  // Получаем текст кода
            navigator.clipboard.writeText(code)  // Копируем в буфер обмена
                .then(() => alert("Код скопирован!"))
                .catch((err) => alert("Ошибка при копировании: " + err));
        };

        // Вставляем кнопку копирования перед блоком кода
        codeContainer.appendChild(copyButton);
        codeContainer.appendChild(codeElement);  // Добавляем сам блок кода

        // Вставляем контейнер с кодом и кнопкой в статью
        block.parentElement.replaceWith(codeContainer);

        // Получаем язык кода (если есть)
        const language = block.className.split(' ')[1];  // class="language-python"
        if (language) {
            const languageLabel = document.createElement("span");
            languageLabel.classList.add("language-label");
            languageLabel.textContent = language.toUpperCase();  // Показываем язык (например, Python)
            codeContainer.appendChild(languageLabel);
        }
    });
}

// Функция для сворачивания/раскрытия папки
function toggleFolder(path, folder, nested) {
    if (openedFolders.has(path)) {
        openedFolders.delete(path); // Закрываем папку
        folder.classList.remove("open");
        nested.style.display = "none";  // Скрываем содержимое папки
    } else {
        openedFolders.add(path); // Открываем папку
        folder.classList.add("open");
        nested.style.display = "block";  // Показываем содержимое папки
    }
    localStorage.setItem("openedFolders", JSON.stringify(Array.from(openedFolders)));  // Сохраняем состояние в localStorage
}

document.getElementById("back-btn").onclick = async () => {
    const res = await fetch("/api/back");
    const data = await res.json();
    document.getElementById("content").innerHTML = data.html;
};

document.getElementById("search-input").addEventListener("input", function() {
    const query = this.value.toLowerCase();
    filterTree(query);
});

function filterTree(query) {
    const treeContainer = document.getElementById("tree");
    const treeNodes = treeContainer.getElementsByTagName("li");

    Array.from(treeNodes).forEach((node) => {
        const text = node.textContent.toLowerCase();
        if (text.includes(query)) {
            node.style.display = "";
        } else {
            node.style.display = "none";
        }
    });
}

// Обработчик для кнопки "Свернуть" и "Показать древо"
document.getElementById("collapse-btn").onclick = () => {
    const treeContainer = document.getElementById("tree");
    const folders = treeContainer.getElementsByClassName("folder");

    Array.from(folders).forEach((folder) => {
        const nested = folder.querySelector("ul");
        if (nested) {
            nested.style.display = "none";  // Скрыть все папки
            folder.classList.remove("open");  // Убрать стиль для открытых папок
        }
    });

    openedFolders.clear();  // Очистить сохранённое состояние папок
    localStorage.setItem("openedFolders", "[]");  // Сохранить пустое состояние
    document.getElementById("expand-btn").style.display = "inline";  // Показать кнопку "Показать древо"
    document.getElementById("collapse-btn").style.display = "none";  // Скрыть кнопку "Свернуть"
};

document.getElementById("expand-btn").onclick = () => {
    const treeContainer = document.getElementById("tree");
    const folders = treeContainer.getElementsByClassName("folder");

    Array.from(folders).forEach((folder) => {
        const nested = folder.querySelector("ul");
        if (nested) {
            nested.style.display = "block";  // Показать все папки
            folder.classList.add("open");  // Установить стиль для открытых папок
        }
    });

    document.getElementById("expand-btn").style.display = "none";  // Скрыть кнопку "Показать древо"
    document.getElementById("collapse-btn").style.display = "inline";  // Показать кнопку "Свернуть"
};

window.onload = fetchTree;
