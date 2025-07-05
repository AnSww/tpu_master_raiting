from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import text
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload



from db import AsyncSessionLocal
from models import User, Directory

import pandas as pd
import os

from scripts.get_position import get_position
from scripts.directions import DIRECTIONS

router = Router()

class IDState(StatesGroup):
    waiting_for_tpu_id = State()

# Кнопки стартовые
@router.message(F.text == "/start")
async def start_cmd(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆔 Задать свой ID")],
            [KeyboardButton(text="📊 Получить рейтинг")],
            [KeyboardButton(text="ℹ️ Инфо")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выбери действие:", reply_markup=kb)


@router.message(F.text == "ℹ️ Инфо")
async def ask_info(message: Message):
    await message.answer("Это телеграм бот для просмотра рейтинговых таблиц на поступление"
                         "в Томский политехнический университет\n\n"
                         'Для просмотра рейтингов задайте свой ID и нажмите кнопку "📊 Получить рейтинг"\n\n'
                         'Данные таблиц обновляются каждые полчаса')


@router.message(F.text == "🆔 Задать свой ID")
async def ask_tpu_id(message: Message, state: FSMContext):
    await message.answer("Введите ваш TPU ID:")
    await state.set_state(IDState.waiting_for_tpu_id)

# Обработка TPU ID + поиск в таблицах
@router.message(IDState.waiting_for_tpu_id)
async def save_tpu_id(message: Message, state: FSMContext):
    tpu_id = message.text.strip()
    tg_id = message.from_user.id

    await state.clear()

    session = AsyncSessionLocal()

    # Удалим старые записи
    await session.execute(
        text("DELETE FROM user WHERE tg_id = :tg_id"),
        {"tg_id": tg_id}
    )

    await session.execute(
        text("DELETE FROM directories WHERE tg_id = :tg_id"),
        {"tg_id": tg_id}
    )

    # Ищем направления из CSV
    directories = []
    folder = "./scripts/tables"
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(folder, file), encoding="utf-8-sig")
            if "ID" in df.columns and tpu_id in df["ID"].astype(str).values:
                directories.append(file.replace(".csv", ""))

    if not directories:
        await message.answer("❗ Направления с таким ID не найдены.")
        await session.close()
        return

    # Сохраняем в БД
    user = User(tg_id=tg_id, tpu_id=tpu_id)
    session.add(user)
    await session.flush()

    for d in directories:
        session.add(Directory(tg_id=tg_id, directory=d))

    await session.commit()
    await session.close()

    await message.answer(f"✅ Сохранено. Направления: {len(directories)}")

@router.message(F.text == "📊 Получить рейтинг")
async def show_rating(message: Message):
    tg_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.directories))
            .where(User.tg_id == tg_id)
        )
        user = result.scalars().first()

        if not user:
            await message.answer("Сначала введите свой TPU ID")
            return

        reply_dicts = []

        for d in user.directories:
            raiting = get_position(d.directory, int(user.tpu_id))
            reply_dicts.append(raiting)

        # Сортируем по приоритету
        reply_dicts.sort(key=lambda x: x.get('Приоритет', 999))

        # Формируем текст ответа
        reply_lines = [
            "\n".join(f"{key}: {value}" for key, value in r.items())
            for r in reply_dicts
        ]

        if reply_lines:
            await message.answer("\n\n".join(reply_lines))
        else:
            await message.answer("⚠️ Вы пока ни в одном рейтинге не участвуете.")
