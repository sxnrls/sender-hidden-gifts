#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hiddie — Отправитель скрытых подарков Telegram
───────────────────────────────────────────────
Отправляет звёздные подарки, скрытые из UI Telegram,
с поддержкой премиум-эмодзи в подписи через «Избранное».
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path


# ╔══════════════════════════════════════════════╗
# ║          Проверка зависимостей               ║
# ╚══════════════════════════════════════════════╝

def _check_dependencies():
    """Проверяет наличие всех необходимых библиотек перед запуском."""
    missing = []
    for module, package in [
        ("telethon", "telethon"),
        ("rich",     "rich"),
        ("dotenv",   "python-dotenv"),
    ]:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print("\n  ✗  Отсутствуют необходимые библиотеки.\n"
              f"     Выполни:  pip install {' '.join(missing)}\n")
        sys.exit(1)


_check_dependencies()


# ╔══════════════════════════════════════════════╗
# ║                 Импорты                      ║
# ╚══════════════════════════════════════════════╝

from dotenv import load_dotenv, set_key

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from telethon import TelegramClient, errors
from telethon.password import compute_check
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.auth import (
    CheckPasswordRequest,
    SendCodeRequest,
    SignInRequest,
)
from telethon.tl.functions.payments import GetPaymentFormRequest, SendStarsFormRequest
from telethon.tl.types import (
    CodeSettings,
    InputInvoiceStarGift,
    MessageEntityCustomEmoji,
    TextWithEntities,
)


# ╔══════════════════════════════════════════════╗
# ║          Консоль и константы                 ║
# ╚══════════════════════════════════════════════╝

console = Console(
    theme=Theme({
        "accent": "bold magenta",
        "ok":     "bold green",
        "err":    "bold red",
        "warn":   "bold yellow",
        "info":   "cyan",
        "dim":    "dim white",
        "hi":     "bold white",
    }),
    highlight=False,
)

ENV_FILE       = Path(".env")
SESSION        = "gift_sender"
CAPTION_LIMIT  = 128   # Telegram ограничивает подпись к подарку 128 символами


# ╔══════════════════════════════════════════════╗
# ║                  Баннер                      ║
# ╚══════════════════════════════════════════════╝

# ASCII-арт «Hiddie» (шрифт Big Money NW) + миниатюрная иконка подарка
_HIDDIE_LINES = [
    r"$$\   $$\ $$\       $$\       $$\ $$\           ",
    r"$$ |  $$ |\__|      $$ |      $$ |\__|          ",
    r"$$ |  $$ |$$\  $$$$$$$ | $$$$$$$ |$$\  $$$$$$\  ",
    r"$$$$$$$$ |$$ |$$  __$$ |$$  __$$ |$$ |$$  __$$\ ",
    r"$$  __$$ |$$ |$$ /  $$ |$$ /  $$ |$$ |$$$$$$$$ |",
    r"$$ |  $$ |$$ |$$ |  $$ |$$ |  $$ |$$ |$$   ____|",
    r"$$ |  $$ |$$ |\$$$$$$$ |\$$$$$$$ |$$ |\$$$$$$$\ ",
    r"\__|  \__|\__| \_______| \_______|\___|\_______|",
]


def _build_banner_string() -> str:
    """Собирает строку баннера: ASCII Hiddie."""
    return "\n".join(_HIDDIE_LINES)


BANNER_ART = _build_banner_string()


def show_banner():
    """Выводит приветственный баннер в терминал."""
    console.print()
    console.print(Text(BANNER_ART, style="bold magenta"))
    console.print()
    console.print("[dim]       ──  G I F T   S E N D E R  ──   [/dim]")
    console.print()
    console.print(
        Rule(
            "[dim]  github.com/sxnrls/sender-hidden-gifts  [/dim]",
            style="magenta",
        )
    )
    console.print()
    console.print(
        Text(
            "  ✦ Отправка скрытых подарков   ·   Поддержка премиум-эмодзи ✦  ",
            style="magenta",
        )
    )
    console.print()


# ╔══════════════════════════════════════════════╗
# ║          Управление учётными данными         ║
# ╚══════════════════════════════════════════════╝

def load_or_prompt_credentials() -> tuple[int, str]:
    """
    Загружает API-ключи из файла .env.
    Если файл отсутствует — интерактивно запрашивает их у пользователя и сохраняет.
    Возвращает (api_id, api_hash).
    """
    load_dotenv(ENV_FILE)
    api_id   = os.getenv("TG_API_ID",   "").strip()
    api_hash = os.getenv("TG_API_HASH", "").strip()

    if api_id and api_hash:
        console.print(
            f"  [dim]⚙  Учётные данные загружены из [bold]{ENV_FILE}[/bold][/dim]"
        )
        console.print()
        return int(api_id), api_hash

    # ── первый запуск: объяснение и запрос данных ─────────────────────────────
    console.print(
        Panel(
            Text.from_markup(
                "  [info]Первый запуск![/info]\n\n"
                "  Перейди на [bold]https://my.telegram.org[/bold]\n"
                "  → [hi]API development tools[/hi] → [hi]Create App[/hi]\n"
                "  и скопируй [accent]API ID[/accent] и [accent]API Hash[/accent].\n\n"
                "  [dim]Данные будут сохранены в [bold].env[/bold]\n"
                "  и загрузятся автоматически при следующих запусках.[/dim]"
            ),
            title="[accent]⚙  Первичная настройка[/accent]",
            border_style="magenta",
            padding=(1, 3),
        )
    )
    console.print()

    while True:
        raw_id = Prompt.ask("  [accent]API ID[/accent]  [dim](число)[/dim]").strip()
        if raw_id.isdigit():
            api_id = raw_id
            break
        console.print("  [err]✗  API ID должен быть числом.[/err]")

    api_hash = Prompt.ask("  [accent]API Hash[/accent] [dim](hex-строка)[/dim]").strip()
    if not api_hash:
        console.print("  [err]✗  API Hash не может быть пустым.[/err]")
        sys.exit(1)

    ENV_FILE.touch()
    set_key(str(ENV_FILE), "TG_API_ID",   api_id)
    set_key(str(ENV_FILE), "TG_API_HASH", api_hash)

    console.print(f"  [ok]✓  Сохранено в [bold]{ENV_FILE}[/bold][/ok]")
    console.print()
    return int(api_id), api_hash


# ╔══════════════════════════════════════════════╗
# ║                 Авторизация                  ║
# ╚══════════════════════════════════════════════╝

async def do_login(client: TelegramClient):
    """
    Интерактивный вход в аккаунт: номер телефона → код → опциональный 2FA.
    Пропускается, если сессия уже активна.
    """
    if await client.is_user_authorized():
        return

    console.print(Rule("[accent]  Вход в аккаунт  [/accent]", style="magenta"))
    console.print()

    phone = Prompt.ask(
        "  [info]Номер телефона[/info]  [dim](например +79991234567)[/dim]"
    ).strip()

    console.print("  [dim]Отправляю код подтверждения…[/dim]")

    try:
        sent = await client(
            SendCodeRequest(
                phone_number=phone,
                api_id=client.api_id,
                api_hash=client.api_hash,
                settings=CodeSettings(
                    allow_flashcall=False,
                    current_number=False,
                    allow_app_hash=False,
                ),
            )
        )
    except Exception as exc:
        console.print(f"  [err]✗  Не удалось отправить код: {exc}[/err]")
        sys.exit(1)

    delivery = type(sent.type).__name__.replace("SentCodeType", "")
    console.print(f"  [ok]✓  Код отправлен через:[/ok] [accent]{delivery}[/accent]")

    if hasattr(sent, "timeout") and sent.timeout:
        console.print(f"  [dim]Действителен {sent.timeout} сек.[/dim]")
    console.print()

    code = Prompt.ask("  [info]Код подтверждения[/info]").strip()

    try:
        await client(
            SignInRequest(
                phone_number=phone,
                phone_code_hash=sent.phone_code_hash,
                phone_code=code,
            )
        )
    except errors.SessionPasswordNeededError:
        console.print()
        console.print("  [warn]⚠  Включена двухфакторная аутентификация.[/warn]")
        passwd = Prompt.ask("  [warn]Пароль 2FA[/warn]", password=True)
        pwd_obj = await client(GetPasswordRequest())
        try:
            await client(CheckPasswordRequest(password=compute_check(pwd_obj, passwd)))
        except Exception as exc:
            console.print(f"  [err]✗  Неверный пароль: {exc}[/err]")
            sys.exit(1)
    except Exception as exc:
        console.print(f"  [err]✗  Ошибка входа: {exc}[/err]")
        sys.exit(1)

    console.print("  [ok]✓  Вход выполнен![/ok]")
    console.print()


# ╔══════════════════════════════════════════════╗
# ║       Сбор подписи через «Избранное»         ║
# ╚══════════════════════════════════════════════╝

async def collect_caption_from_saved(
    client: TelegramClient, me
) -> tuple[str | None, list | None]:
    """
    Предлагает пользователю написать подпись к подарку прямо в «Избранном» Telegram.

    Это удобно, потому что:
      — там работают любые эмодзи, в том числе анимированные премиум-эмодзи;
      — не нужно копировать текст вручную в терминал;
      — скрипт автоматически подхватит все сущности (CustomEmoji и др.).

    Возвращает (text, entities), готовые для TextWithEntities,
    или (None, None), если пользователь решил пропустить подпись.

    Лимит Telegram: не более 128 символов. Если сообщение длиннее —
    пользователь получает предупреждение и возможность отправить более короткое.
    """
    # ── фиксируем текущий ID, чтобы смотреть только на НОВЫЕ сообщения ───────
    prev_msgs = await client.get_messages(me, limit=1)
    prev_id   = prev_msgs[0].id if prev_msgs else 0

    console.print()
    console.print(
        Panel(
            Text.from_markup(
                "  [info]Открой Telegram и перейди в [bold]Избранное[/bold].[/info]\n\n"
                "  Напиши там [bold]одно сообщение[/bold] с текстом подписи.\n"
                "  Можно добавлять обычные и [accent]премиум-эмодзи[/accent] — \n"
                "  скрипт подхватит их автоматически.\n\n"
                f"  [warn]⚠  Лимит подписи: [bold]{CAPTION_LIMIT} символов[/bold]"
                " (включая пробелы и эмодзи).[/warn]\n\n"
                "  [dim]Когда отправишь — нажми [bold]Enter[/bold] здесь.[/dim]"
            ),
            title="[accent]✍  Подпись к подарку[/accent]",
            border_style="magenta",
            padding=(1, 3),
        )
    )

    while True:
        input()   # ждём Enter от пользователя

        # ── ищем новые сообщения в «Избранном» ───────────────────────────────
        recent = await client.get_messages(me, limit=10)
        target = None

        for m in recent:
            if m.id <= prev_id:
                break
            if m.message:   # любое текстовое сообщение подходит
                target = m
                break

        if target is None:
            console.print(
                "  [warn]⚠  Новых сообщений в «Избранном» не найдено.[/warn]\n"
                "  [dim]Убедись, что отправил сообщение ПОСЛЕ этого шага, "
                "и нажми Enter снова.[/dim]"
            )
            continue

        char_count = len(target.message)

        # ── проверка лимита 128 символов ─────────────────────────────────────
        if char_count > CAPTION_LIMIT:
            console.print(
                f"\n  [err]✗  Слишком длинная подпись![/err]\n"
                f"  [warn]У тебя [bold]{char_count}[/bold] символов, "
                f"максимум — [bold]{CAPTION_LIMIT}[/bold].[/warn]\n\n"
                "  [dim]Отправь в «Избранное» более короткое сообщение "
                "и нажми Enter.[/dim]"
            )
            prev_id = target.id   # сдвигаем водяной знак, чтобы поймать следующее
            continue

        # ── нашли подходящее сообщение ────────────────────────────────────────
        break

    raw_text = target.message
    entities = target.entities or []

    # ── отбираем только премиум-эмодзи для отображения в таблице ─────────────
    premium = [e for e in entities if isinstance(e, MessageEntityCustomEmoji)]

    if premium:
        table = Table(
            title="  Обнаружены премиум-эмодзи",
            box=box.ROUNDED,
            border_style="magenta",
            show_lines=True,
            header_style="bold magenta",
        )
        table.add_column("#",           style="dim",  justify="right", width=4)
        table.add_column("Эмодзи",                   justify="center", width=8)
        table.add_column("Document ID", style="cyan", justify="right", min_width=20)
        table.add_column("Позиция",     style="dim",  justify="right", width=8)
        table.add_column("Длина",       style="dim",  justify="right", width=8)

        for i, ent in enumerate(premium, 1):
            glyph = raw_text[ent.offset: ent.offset + ent.length]
            table.add_row(
                str(i), glyph, str(ent.document_id),
                str(ent.offset), str(ent.length),
            )

        console.print()
        console.print(table)

    # ── превью подписи ────────────────────────────────────────────────────────
    console.print()
    console.print(
        Panel(
            f"  [hi]Предпросмотр подписи[/hi]  "
            f"[dim]({len(raw_text)}/{CAPTION_LIMIT} символов)[/dim]\n\n"
            f"  {raw_text}",
            border_style="cyan",
            padding=(0, 2),
        )
    )
    console.print()

    ok = Confirm.ask("  [accent]Использовать эту подпись?[/accent]", default=True)
    if not ok:
        console.print("  [warn]Пропущено.[/warn]")
        return None, None

    return raw_text, entities if entities else None


# ╔══════════════════════════════════════════════╗
# ║             Построение подписи               ║
# ╚══════════════════════════════════════════════╝

async def build_caption(
    client: TelegramClient, me
) -> tuple[str | None, list | None]:
    """
    Спрашивает, нужна ли подпись к подарку.
    Если да — запускает процесс сбора из «Избранного».
    Возвращает (text, entities) или (None, None).
    """
    console.print()
    console.print(Rule("[accent]  Подпись к подарку  [/accent]", style="magenta"))
    console.print()

    want_caption = Confirm.ask(
        "  [accent]Добавить подпись к подарку?[/accent]", default=False
    )

    if not want_caption:
        return None, None

    return await collect_caption_from_saved(client, me)


# ╔══════════════════════════════════════════════╗
# ║            Поиск получателя                  ║
# ╚══════════════════════════════════════════════╝

async def resolve_recipient(client: TelegramClient):
    """
    Запрашивает @username или числовой ID получателя
    и резолвит его через Telegram API.
    Возвращает объект пользователя или None при ошибке.
    """
    console.print()
    console.print(Rule("[accent]  Получатель  [/accent]", style="magenta"))
    console.print()

    raw = Prompt.ask(
        "  [accent]Получатель[/accent]  [dim](@username или числовой ID)[/dim]"
    ).strip()

    if not raw:
        console.print("  [err]✗  Получатель не может быть пустым.[/err]")
        return None

    try:
        stripped = raw.lstrip("@")
        lookup   = int(stripped) if stripped.isdigit() else raw
        user     = await client.get_entity(lookup)
        name     = getattr(user, "first_name", None) or getattr(user, "title", str(user.id))
        console.print(
            f"  [ok]✓  Получатель:[/ok] [accent]{name}[/accent]  "
            f"[dim](id {user.id})[/dim]"
        )
        return user
    except Exception as exc:
        console.print(f"  [err]✗  Не удалось найти пользователя '{raw}': {exc}[/err]")
        return None


# ╔══════════════════════════════════════════════╗
# ║               Отправка подарка               ║
# ╚══════════════════════════════════════════════╝

async def send_gift(
    client: TelegramClient,
    gift_id: int,
    user,
    caption_text: str | None,
    caption_entities: list | None,
):
    """
    Формирует invoice для звёздного подарка и отправляет форму оплаты.
    Списывает звёзды с аккаунта авторизованного пользователя.
    """
    msg_obj = None
    if caption_text:
        msg_obj = TextWithEntities(
            text=caption_text,
            entities=caption_entities or [],
        )

    input_peer = await client.get_input_entity(user)
    invoice    = InputInvoiceStarGift(
        peer=input_peer,
        gift_id=gift_id,
        message=msg_obj,
    )

    console.print()
    console.print("  [dim]Получаю форму оплаты…[/dim]")
    form = await client(GetPaymentFormRequest(invoice=invoice))

    console.print("  [dim]Отправляю подарок…[/dim]")
    await client(SendStarsFormRequest(form_id=form.form_id, invoice=invoice))


# ╔══════════════════════════════════════════════╗
# ║                  Главная                     ║
# ╚══════════════════════════════════════════════╝

async def main():
    parser = argparse.ArgumentParser(
        prog="sender",
        description="Hiddie — Отправитель скрытых подарков Telegram",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Удалить сохранённые учётные данные (.env) и выйти",
    )
    args = parser.parse_args()

    # ── сброс ─────────────────────────────────────────────────────────────────
    if args.reset:
        if ENV_FILE.exists():
            ENV_FILE.unlink()
            print(f"  ✓  Файл {ENV_FILE} удалён.")
        else:
            print(f"  ⚠  Файл {ENV_FILE} не найден.")
        sys.exit(0)

    # ── запуск ────────────────────────────────────────────────────────────────
    show_banner()
    api_id, api_hash = load_or_prompt_credentials()

    client = TelegramClient(
        SESSION, api_id, api_hash,
        device_model="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        system_version="Win32",
        app_version="5.9.0 K",
        lang_code="ru",
        system_lang_code="ru-RU",
    )

    await client.connect()
    await do_login(client)

    me = await client.get_me()
    console.print()
    console.print(Rule(style="magenta"))
    console.print(
        f"  [ok]✓[/ok]  Авторизован как "
        f"[accent]{me.first_name}[/accent]  "
        f"[dim](id {me.id})[/dim]"
    )
    console.print(Rule(style="magenta"))

    # ── ID подарка ────────────────────────────────────────────────────────────
    console.print()
    console.print(Rule("[accent]  Подарок  [/accent]", style="magenta"))
    console.print()

    while True:
        raw = Prompt.ask(
            "  [accent]ID подарка[/accent]  [dim](число)[/dim]"
        ).strip()
        if raw.isdigit():
            gift_id = int(raw)
            break
        console.print("  [err]✗  ID подарка должен быть числом.[/err]")

    # ── подпись ───────────────────────────────────────────────────────────────
    caption_text, caption_entities = await build_caption(client, me)

    # ── получатель ────────────────────────────────────────────────────────────
    user = await resolve_recipient(client)
    if user is None:
        await client.disconnect()
        return

    # ── итоговая сводка ───────────────────────────────────────────────────────
    console.print()
    console.print(Rule(style="magenta"))

    has_premium = bool(
        caption_entities
        and any(isinstance(e, MessageEntityCustomEmoji) for e in caption_entities)
    )

    s = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    s.add_column("ключ",  style="accent", min_width=16)
    s.add_column("значение", style="hi")

    name = getattr(user, "first_name", None) or getattr(user, "title", str(user.id))

    s.add_row("ID подарка",    str(gift_id))
    s.add_row("Получатель",    f"{name}  (id {user.id})")
    s.add_row("Подпись",       caption_text if caption_text else "[dim]— нет —[/dim]")
    s.add_row("Премиум ✨",    "[ok]да[/ok]" if has_premium else "[dim]нет[/dim]")

    console.print(
        Panel(
            s,
            title="[accent]  📦  Подтверждение отправки  [/accent]",
            border_style="magenta",
            padding=(1, 1),
        )
    )
    console.print()

    if not Confirm.ask("  [accent]Отправить подарок?[/accent]", default=True):
        console.print("\n  [warn]Отменено.[/warn]")
        await client.disconnect()
        return

    # ── отправка ──────────────────────────────────────────────────────────────
    try:
        await send_gift(client, gift_id, user, caption_text, caption_entities)
        console.print()
        console.print(
            Panel(
                f"  [ok]🎁  Подарок успешно отправлен {name}![/ok]",
                border_style="green",
                padding=(1, 3),
            )
        )
    except errors.FloodWaitError as exc:
        console.print(
            f"\n  [warn]⚠  Telegram ограничил запросы. "
            f"Подожди [bold]{exc.seconds}[/bold] сек. и попробуй снова.[/warn]"
        )
    except errors.RPCError as exc:
        console.print(f"\n  [err]✗  Ошибка Telegram RPC: {exc}[/err]")
    except Exception as exc:
        console.print(f"\n  [err]✗  Непредвиденная ошибка: {exc}[/err]")

    await client.disconnect()
    console.print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n  [warn]Прервано пользователем.[/warn]\n")
