import logging
import asyncio

from aiogram import Bot

from src.drift_bot.ioc import container
from src.drift_bot.bot import create_dispatcher


async def main() -> None:
    bot = await container.get(Bot)
    dp = create_dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
