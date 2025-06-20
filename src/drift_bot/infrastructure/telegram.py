from typing import Optional

import logging

from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.exceptions import TelegramAPIError

from ..core.base import Sender
from ..core.domain import File
from ..core.exceptions import SendingMessageError


class TelegramSender(Sender):
    def __init__(self, bot: Bot) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bot = bot

    async def send(
            self,
            recipient_id: int,
            message: str,
            file: Optional[File],
            **kwargs
    ) -> None:
        try:
            if file:
                await self.bot.send_photo(
                    chat_id=recipient_id,
                    photo=BufferedInputFile(file=file.data, filename=file.file_name),
                    caption=message,
                    **kwargs
                )
                self.logger.info("Message sent successfully")
                return
            await self.bot.send_message(chat_id=recipient_id, text=message)
            self.logger.info("Message sent successfully")
            return
        except TelegramAPIError as e:
            self.logger.error(f"Error while sending message: {e}")
            raise SendingMessageError(f"Error while sending message: {e}") from e
