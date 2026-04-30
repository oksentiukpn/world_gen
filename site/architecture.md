# Архітектура веб-додатку World Gen

Цей документ описує архітектурну будову веб-додатку (Single Page Application) для візуалізації процедурної генерації планет у реальному часі.

## 1. Загальна концепція
Додаток побудований за архітектурою клієнт-сервер з використанням двостороннього зв'язку через WebSockets. 
- **Бекенд (Flask)** відповідає за обчислення (генерація 3D-сітки, шуму, біомів) з використанням існуючого Python-рушія.
- **Фронтенд (Three.js + Vanilla JS)** відповідає за відображення UI, відправку параметрів та плавну анімацію 3D-моделі (morphing) на основі даних, що надходять від сервера.

## 2. Структура директорій (Backend)
Проект використовує патерн **Application Factory** (Фабрика додатків) у Flask:

```text
site/
├── run.py                 # Точка входу, запускає Flask та SocketIO сервер
├── config.py              # Конфігураційні класи (Dev, Prod, Test)
├── .env                   # Змінні оточення
├── requirements.txt       # Залежності (Flask, Flask-SocketIO, numpy тощо)
├── Dockerfile             # Інструкції для створення Docker-образу
├── docker-compose.yaml    # Оркестрація контейнерів
└── app/                   # Основний пакет Flask-додатка
    ├── __init__.py        # Створення додатку (create_app) та ініціалізація SocketIO
    ├── main/              # Blueprint для основних маршрутів
    │   ├── __init__.py    # Ініціалізація Blueprint
    │   └── routes.py      # Маршрути (наприклад, рендер index.html)
    ├── sockets/           # (Заплановано) Обробники WebSocket подій генерації
    ├── templates/         # HTML-шаблони
    │   └── index.html     # Єдина сторінка SPA (з підключеним Tailwind CSS)
    └── static/            # Статичні файли (CSS, JS, зображення)
        ├── css/
        │   └── style.css  # Кастомні стилі (доповнення до Tailwind)
        └── js/
            ├── main.js    # Логіка UI, обробка подій, WebSocket-клієнт
            └── scene.js   # Інкапсульована логіка Three.js (Сцена, Камера, Рендерер)
```

## 3. Компоненти системи та їх взаємодія

### 3.1. Клієнтська частина (Frontend)
- **`index.html`**: Містить бокову панель керування (Sidebar) з налаштуваннями (Subdivisions, Radius, Seed) та контейнер для 3D-сцени на весь екран.
- **`main.js`**: 
  - Зчитує значення з UI (повзунки, кнопки).
  - Ініціалізує з'єднання Socket.IO з сервером.
  - Відправляє подію `generate_planet` з конфігурацією.
  - Слухає події від сервера (`step_base`, `step_noise`, `step_biome`) і передає отримані масиви даних (Float32Array) в `scene.js`.
- **`scene.js`**: 
  - Налаштовує Three.js (WebGLRenderer, PerspectiveCamera, OrbitControls, освітлення).
  - Зберігає поточну геометрію планети (`BufferGeometry`).
  - Має метод `updateGeometry(targetPositions, targetColors)`, який у циклі `requestAnimationFrame` плавно інтерполює (lerp) поточні вершини до нових значень, створюючи ефект "виростання" рельєфу.

### 3.2. Серверна частина (Backend)
- **REST API (`routes.py`)**: Віддає `index.html` та може містити ендпоінти для завантаження файлів (експорт у PNG, OBJ).
- **WebSocket Gateway (`app/sockets/` - майбутній модуль)**:
  - Приймає підключення та запити на генерацію.
  - Ініціалізує клас `PlanetGenerator` з ядра проекту.
  - Виконує обчислення поетапно (використовуючи `yield` або розділені методи) і відправляє проміжні результати через `emit()`.

## 4. Життєвий цикл генерації (Потік даних)

1. **User Action**: Користувач тисне "Generate" в UI.
2. **Client Request**: `main.js` збирає параметри і відсилає `socket.emit('generate', config)`.
3. **Server Step 1 (Base Mesh)**: Сервер генерує ідеальну сферу (вершини + індекси). 
   - `socket.emit('mesh_ready', { vertices, indices })`.
   - Фронтенд миттєво відмальовує гладку кулю.
4. **Server Step 2 (Terrain/Noise)**: Сервер розраховує висоти/warp.
   - `socket.emit('heights_ready', { vertices })`.
   - Фронтенд плавно анімує зміщення вершин (гори виростають, западини опускаються).
5. **Server Step 3 (Biomes)**: Сервер розраховує клімат та кольори.
   - `socket.emit('colors_ready', { colors })`.
   - Фронтенд застосовує кольори вершин (`vertexColors`), завершуючи генерацію.

## 5. Розгортання (Deployment)
Додаток запакований у **Docker**. 
- `Dockerfile` створює образ на базі Python (встановлює залежності з `requirements.txt`).
- `docker-compose.yaml` дозволяє легко підняти додаток локально (`docker-compose up`) з прокиданням портів (наприклад, `5000:5000`). Сервером виступає Eventlet або Gevent для підтримки асинхронних WebSocket-з'єднань у Flask-SocketIO.