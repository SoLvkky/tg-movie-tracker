from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from bot.i18n import current_locale
from bot.logger import logger
from database.crud import get_locale

class I18nMiddleware(BaseMiddleware):   
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        session: AsyncSession = data.get('session')
        if not session:
            logger.warning("No session in data, skipping i18n")
            return await handler(event, data)
        
        user_id = self._extract_user_id(event)
        
        if not user_id:
            logger.debug("No user_id, fallback to en-US")
            token = current_locale.set('en-US')
            try:
                return await handler(event, data)
            finally:
                current_locale.reset(token)
        
        try:
            locale = await get_locale(session, user_id)
            logger.debug(f"User {user_id} → locale={locale}")
            
            token = current_locale.set(locale)
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Failed to get locale for {user_id}: {e}")
            token = current_locale.set('en-US')
            try:
                return await handler(event, data)
            finally:
                current_locale.reset(token)

    def _extract_user_id(self, event: Update) -> int | None:
        if event.message:
            return event.message.chat.id
        if event.callback_query:
            return event.callback_query.message.chat.id
        return None