import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Store data per user
user_files = {}
user_modes = {}


# -------- BUTTONS --------

def main_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 New File", callback_data="new")],
        [InlineKeyboardButton(text="📄 Send Code", callback_data="code")],
        [InlineKeyboardButton(text="📁 Get Last File", callback_data="get")],
        [InlineKeyboardButton(text="🗑 Clear", callback_data="clear")],
        [InlineKeyboardButton(text="ℹ Help", callback_data="help")],
    ])


# -------- START --------

@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(
        "👋 Welcome to Python File Creator Bot!\nUse the buttons below.",
        reply_markup=main_buttons()
    )


# -------- BUTTON HANDLER --------

@dp.callback_query()
async def handle_buttons(cb: types.CallbackQuery):
    uid = cb.from_user.id

    if cb.data == "new":
        user_modes[uid] = "create"
        await cb.message.answer("✍ Send the **filename.py** to create a new file.")
    
    elif cb.data == "code":
        if uid not in user_files:
            return await cb.message.answer("⚠ First create a file.")
        user_modes[uid] = "code"
        await cb.message.answer("💬 Send the code for your file.")
    
    elif cb.data == "get":
        if uid not in user_files:
            return await cb.message.answer("⚠ No file created yet.")
        path = f"generated/{user_files[uid]}"
        await cb.message.answer_document(types.FSInputFile(path))
    
    elif cb.data == "clear":
        user_files.pop(uid, None)
        user_modes.pop(uid, None)
        await cb.message.answer("🗑 File data cleared.")
    
    elif cb.data == "help":
        await cb.message.answer(
            "📘 **Help Menu:**\n"
            "🆕 New File – create a new .py file\n"
            "📄 Send Code – write python code\n"
            "📁 Get Last File – download your file\n"
            "🗑 Clear – clear file session",
            reply_markup=main_buttons()
        )
    
    await cb.answer()


# -------- TEXT HANDLER --------

@dp.message()
async def text_handler(msg: types.Message):
    uid = msg.from_user.id

    if uid not in user_modes:
        return await msg.answer("⚠ Use the buttons to begin.", reply_markup=main_buttons())

    mode = user_modes[uid]

    # --- File Creation ---
    if mode == "create":
        filename = msg.text.strip()

        if not filename.endswith(".py"):
            return await msg.answer("⚠ Filename must end with .py")

        os.makedirs("generated", exist_ok=True)

        path = f"generated/{filename}"
        open(path, "w").close()  # empty file

        user_files[uid] = filename
        user_modes[uid] = None

        return await msg.answer(f"✔ File Created: {filename}\nNow press: 📄 Send Code",
                                reply_markup=main_buttons())

    # --- Code Writing ---
    if mode == "code":
        if uid not in user_files:
            return await msg.answer("⚠ First create a file.")

        filename = user_files[uid]
        path = f"generated/{filename}"

        with open(path, "w", encoding="utf-8") as f:
            f.write(msg.text)

        user_modes[uid] = None

        return await msg.answer(
            f"✔ Code saved in {filename}\nPress 📁 Get Last File to download.",
            reply_markup=main_buttons()
        )


# -------- START BOT --------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())