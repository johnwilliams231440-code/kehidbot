import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from ollama import Client

# --- Setup ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
AI_MODEL = os.getenv("AI_MODEL", "llama3.2:3b")

# Init bot, dispatcher, and AI client
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ollama_client = Client(host=OLLAMA_HOST)

# Logging
logging.basicConfig(level=logging.INFO)

# --- Helper Functions ---
async def paraphrase_text(text: str) -> str:
    """Sends text to Ollama with a paraphrasing prompt."""
    prompt = f"""You are a helpful assistant that rewrites content.
    TASK: Rewrite the following text to express the same meaning but using different words and sentence structures. Output the rewritten text only, no explanations or extra text.
    TEXT: {text}
    REWRITTEN TEXT:"""
    
    try:
        response = ollama_client.generate(model=AI_MODEL, prompt=prompt)
        return response['response'].strip()
    except Exception as e:
        logging.error(f"Ollama error: {e}")
        return "Sorry, I'm having trouble processing your request right now."

# --- Command Handlers ---
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("👋 Hi! Send me any text and I'll rewrite it in a new way!")

@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = "📝 **How to use me:**\n\n"
    help_text += "Just send me any text message, and I'll send back a rewritten version.\n"
    help_text += "Or use the `/rewrite` command followed by your text.\n"
    help_text += "Example: `/rewrite The meeting is postponed until Friday.`"
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("rewrite"))
async def rewrite_command(message: Message):
    text_to_rewrite = message.text.replace("/rewrite", "", 1).strip()
    if not text_to_rewrite:
        await message.answer("Please provide text to rewrite. Example: `/rewrite Hello world!`")
        return
    
    await message.answer("🔄 Rewriting your text, please wait...")
    result = await paraphrase_text(text_to_rewrite)
    await message.answer(result)

@dp.message()
async def rewrite_text(message: Message):
    """Handles any other text message as a request for paraphrasing."""
    await message.answer("🔄 Let me rewrite that for you...")
    result = await paraphrase_text(message.text)
    await message.answer(result)

# --- Main Execution ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
