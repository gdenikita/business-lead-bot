import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
import os

from database import init_db, add_lead, get_stats

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

class LeadForm(StatesGroup):
    service = State()
    name = State()
    phone = State()
    comment = State()

def services_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Разработка сайта", callback_data="svc_website")],
        [InlineKeyboardButton(text="Telegram-бот", callback_data="svc_bot")],
        [InlineKeyboardButton(text="Умный дом / IoT", callback_data="svc_smarthome")],
        [InlineKeyboardButton(text="Мобильное приложение", callback_data="svc_app")],
        [InlineKeyboardButton(text="Другое", callback_data="svc_other")],
    ])

async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден")

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    @dp.message(CommandStart())
    async def start(message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "👋 Привет! Я помогу оставить заявку на разработку.\n\n"
            "Выбери услугу, которая тебя интересует:",
            reply_markup=services_kb()
        )

    @dp.callback_query(F.data.startswith("svc_"))
    async def choose_service(callback: CallbackQuery, state: FSMContext):
        services = {
            "svc_website": "Разработка сайта",
            "svc_bot": "Telegram-бот",
            "svc_smarthome": "Умный дом / IoT",
            "svc_app": "Мобильное приложение",
            "svc_other": "Другое",
        }
        service = services.get(callback.data, "Услуга")
        await state.update_data(service=service)
        await state.set_state(LeadForm.name)
        await callback.message.edit_text(f"Услуга: <b>{service}</b>\n\nКак вас зовут?", parse_mode="HTML")
        await callback.answer()

    @dp.message(LeadForm.name)
    async def get_name(message: Message, state: FSMContext):
        await state.update_data(name=message.text.strip())
        await state.set_state(LeadForm.phone)
        await message.answer("Укажите номер телефона (или Telegram для связи):")

    @dp.message(LeadForm.phone)
    async def get_phone(message: Message, state: FSMContext):
        await state.update_data(phone=message.text.strip())
        await state.set_state(LeadForm.comment)
        await message.answer("Кратко опишите задачу (или напишите «-» если нечего добавить):")

    @dp.message(LeadForm.comment)
    async def get_comment(message: Message, state: FSMContext):
        data = await state.get_data()
        comment = message.text.strip() if message.text.strip() != "-" else ""

        await add_lead(
            user_id=message.from_user.id,
            username=message.from_user.username or "",
            name=data["name"],
            phone=data["phone"],
            service=data["service"],
            comment=comment
        )

        # Уведомление админу
        if ADMIN_ID:
            try:
                text = (
                    f"🆕 <b>Новая заявка!</b>\n\n"
                    f"Услуга: {data['service']}\n"
                    f"Имя: {data['name']}\n"
                    f"Телефон: {data['phone']}\n"
                    f"Username: @{message.from_user.username or 'нет'}\n"
                )
                if comment:
                    text += f"Комментарий: {comment}\n"
                await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
            except Exception as e:
                logging.error(f"Не удалось отправить админу: {e}")

        await message.answer(
            "✅ Спасибо! Заявка принята.\n\n"
            "Мы свяжемся с вами в ближайшее время.",
        )
        await state.clear()

    @dp.message(Command("stats"))
    async def stats(message: Message):
        if message.from_user.id != ADMIN_ID:
            await message.answer("Команда только для администратора.")
            return
        s = await get_stats()
        await message.answer(
            f"📊 <b>Статистика</b>\n\n"
            f"Всего заявок: <b>{s['total']}</b>\n"
            f"Новых: <b>{s['new']}</b>",
            parse_mode="HTML"
        )

    print("Lead-бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
