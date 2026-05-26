import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
import aiohttp

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
AI_API_URL = os.getenv("AI_API_URL", "https://openrouter.ai/api/v1/chat/completions")
AI_API_KEY = os.getenv("AI_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def paraphrase_via_api(text: str) -> str:
    """Calls external AI API to rewrite the text."""
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a paraphrasing assistant. Rewrite the user's text using different words while keeping the same meaning. Output only the rewritten text, no explanations."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.7
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(AI_API_URL, headers=headers, json=payload) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"].strip()

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("👋 Send me any text and I'll rewrite it for you!")

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer("Just send any text — I'll send back a paraphrased version.")

@dp.message()
async def handle_text(message: Message):
    await message.answer("🔄 Rewriting your text...")
    result = await paraphrase_via_api(message.text)
    await message.answer(result)

async def on_startup():
    """Sets up webhook when the bot starts."""
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown():
    """Cleans up webhook and closes bot session."""
    await bot.delete_webhook()
    await bot.session.close()

def main():
    """Runs the bot with webhook."""
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

if __name__ == "__main__":
    main()
