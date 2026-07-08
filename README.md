<div align="center">

# 🎁 Hiddie — Отправитель скрытых подарков Telegram

### Отправляй скрытые Telegram-подарки по ID
с поддержкой **премиум-эмодзи**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Telethon](https://img.shields.io/badge/Telethon-Latest-4dabf7?style=flat-square)](https://github.com/LonamiWebs/Telethon)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## Что это такое?

Telegram периодически убирает ивентовые подарки из магазина. Через приложение их больше нельзя отправить — но через API это возможно, если знать **ID подарка.**

Hiddie автоматизирует этот процесс и добавляет удобный интерфейс + поддержку **премиум-эмодзи.**

---

## ✨ Возможности

| | |
|---|---|
| 🎁 **Скрытые подарки** | Отправка любого подарка по ID, даже удалённого из магазина |
| ✍️  **Подпись через «Избранное»** | Пишешь подпись прямо в Telegram — удобно и поддерживает премиум эмодзи в подписи |
| 💾 **Кэш учётных данных** | API-ключи сохраняются в `.env` — вводишь один раз |

---

## ⚠️ Важно перед использованием

Скрипт работает **от твоего аккаунта Telegram**. После первого запуска создаётся файл сессии `gift_sender.session`.

**Никому не передавай:**
- `gift_sender.session` — даёт полный доступ к аккаунту без пароля
- `.env` — содержит твои API-ключи
- `api_id` и `api_hash`

Автор скрипта не несёт ответственности за использование.

---

## 📋 Требования

- Python 3.10+
- Аккаунт Telegram с достаточным балансом звёзд
- API-ключи Telegram (бесплатно, см. ниже)

---

## ⚙️ Получение API-ключей

Это делается **один раз**. При первом запуске скрипт сам спросит их и сохранит.

1. Открой [https://my.telegram.org](https://my.telegram.org)
2. Войди по номеру телефона
3. Нажми **«API development tools»**
4. Заполни форму (App title и Short name — любые слова, например `MyApp`)
5. Нажми **«Create application»**
6. Скопируй **`api_id`** (число) и **`api_hash`** (строка из букв и цифр)

---

## 🔍 Где брать ID подарков

Канал с актуальными ID удалённых и коллекционных подарков: **[@GiftIDs](https://t.me/GiftChangesIDs)**

⚠️ Примечание: коллекционные подарки нельзя дарить

---

## ️🚀 Установка и запуск

### 📱 Android — Termux

1. Установи **Termux** с [F-Droid](https://f-droid.org/packages/com.termux/) *(не из Google Play — там устаревшая версия!)*
2. В Termux выполни:
   ```bash
   pkg update && pkg upgrade -y
   pkg install python -y
   git clone https://github.com/sxnrls/sender-hidden-gifts
   cd sender-hidden-gifts
   pip install -r requirements.txt
   ```
3. Разреши доступ к файлам: `termux-setup-storage`
4. Запусти. Напиши в Termux: `python sender.py`

**Полезно:** Чтобы Termux не убивался системой в фоне — зайди в *Настройки → Приложения → Termux → Батарея → Без ограничений*.

### 📱 Android — Pydroid 3

Альтернатива Termux с графическим интерфейсом и встроенным редактором кода:

1. Установи **Pydroid 3** из Google Play
2. Установи зависимости через встроенный pip: `telethon rich python-dotenv`
3. Скачай этот репозиторий:
- Нажми Code → Download ZIP.
- Распакуй архив в удобную папку.
5. Открой `sender.py` и запусти

### 🍏 iPhone — a-Shell

1. Установи **a-Shell** из App Store *(не a-Shell mini — в mini нет pip!)*. Разработчик: Nicolas Holzschuch
2. Запусти его и убедись, что находишься в папке: «~/Documents», если нет, выполни:
   ```
   cd ~/Documents
   ```
3. Установи репозиторий:
   ```
   lg2 clone https://github.com/sxnrls/sender-hidden-gifts.git sender-hidden-gifts
   ```
4. Перейди в эту папку:
   ```
   cd ~/Documents/sender-hidden-gifts
   ```
5. Установи зависимости:
   ```
   pip install -r requirements.txt
   ```
6. Запуск:
   ```
   python sender.py
   ```
---

💻 Запуск на ПК.

1. Установи **Python**

• Скачай **Python** с [Официального сайта](https://python.org/downloads)
⚠️ ВАЖНО: поставь галочку "Add Python to PATH" внизу окна установки

• После установки открой "cmd" и проверь:
    ```
    python --version
    pip --version
    ```
• Если вместо версии появляется ошибка, Python установлен неправильно или не добавлен в PATH.

2. Скачай скрипт

Есть два варианта:

Вариант 1 — через Git
    ```
    git clone https://github.com/sxnrls/sender-hidden-gifts
    cd sender-hidden-gifts
    ```
Вариант 2 — через ZIP

• 1) Нажми Code → Download ZIP.
• 2) Распакуй архив в удобную папку.
• 3) Открой эту папку.

3. Установи зависимости

Открой командную строку в папке со скриптом и выполни:
    ```
    pip install -r requirements.txt
    ```
Если по какой-то причине "requirements.txt" не ставится, можно поставить библиотеки вручную:
    ```
    pip install telethon rich python-dotenv
    ```

4. Запусти скрипт. В папке со скриптом выполни:
    ```
    python sender.py
    ```
---

## ⚙️ Использование

После установки, следуй понятным инструкциям в терминале:

1. **ID подарка** — вводишь длинный числовой ID (например: `5170233102089322756` 🧸)
2. **Подпись** — если нужна, открываешь «Избранное» в Telegram и пишешь там любое сообщение до 128 символов, отправляешь
3. **Получатель** — `@username` или числовой ID
4. **Подтверждение** — смотришь сводку и жмёшь Enter

## 🛠️ Возможные ошибки

| Ошибка | Решение |
|---|---|
| `No module named telethon` | `pip install telethon rich python-dotenv` |
| `BALANCE_TOO_LOW` | Недостаточно звёзд на аккаунте |
| `FloodWaitError` | Слишком много запросов — подожди указанное количество секунд |
| Ошибки компиляции при установке | Выполни `pkg install build-essential -y` (Termux) |
| `No such file or directory` | Используй `ls` чтобы убедиться, что `sender.py` в текущей папке |
| `pip install` не работает на iPhone | Убедись, что установлена **a-Shell**, а не **a-Shell mini** |

---

## 📁 Структура файлов

```
sender-hidden-gifts/
├── sender.py               # Основной скрипт
├── .env                    # Сохранённые API-ключи (создаётся автоматически)
├── gift_sender.session     # Сессия Telethon (создаётся автоматически)
```

---

<div align="center">

Сделано с ❤️ by sxnrls

</div>
