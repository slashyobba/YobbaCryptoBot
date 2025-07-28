import os
import time
import asyncio
import logging
from aiogram import Bot, Dispatcher
from core.bitget_client import get_portfolio_value
from core.market_analysis import get_market_summary

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def send_report():
    try:
        portfolio_text, portfolio_symbols = await get_portfolio_value()
        market = await get_market_summary(portfolio_symbols)
        message = f"📊 Отчёт по портфелю\n\n{portfolio_text}\n\n📈 Рынок:\n{market}"
        await bot.send_message(CHANNEL_ID, message, parse_mode='Markdown')
    except Exception as e:
        logging.exception("Ошибка при отправке отчета: %s", e)

async def scheduler():
    while True:
        await send_report()
        await asyncio.sleep(3 * 60 * 60)  # каждые 3 часа

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await scheduler()

if name == "__main__":
    asyncio.run(main())
