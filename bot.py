import os
from typing import Dict, Any
import logging
from datetime import datetime
import anthropic
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Импортируем конфигурацию
from config import *

# Настраиваем логирование
logging.basicConfig(
    format=LOG_FORMAT,
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

# Инициализируем клиент Anthropic
client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# Хранилище истории диалогов
conversation_history: Dict[int, list] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text(MESSAGES["welcome"])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    await start(update, context)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /clear"""
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text(MESSAGES["history_cleared"])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик входящих сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text

    # Инициализируем историю диалога если её нет
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Добавляем сообщение пользователя в историю
    conversation_history[user_id].append({"role": "user", "content": user_message})

    # Ограничиваем длину истории
    if len(conversation_history[user_id]) > MAX_HISTORY_LENGTH:
        conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY_LENGTH:]

    try:
        # Отправляем индикатор набора текста
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Получаем ответ от Claude с обновленным системным промптом
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            system="""Ты - эксперт по бухгалтерскому учету в Румынии. 

Твои знания включают актуальное законодательство по состоянию на начало 2025 года:
- Румынское законодательство о бухгалтерском учете
- Налоговый кодекс Румынии с последними изменениями
- Стандарты финансовой отчетности (IFRS, Romanian GAAP)
- Процедуры регистрации и ведения бизнеса в Румынии
- Требования к документации и отчетности
- Сроки подачи деклараций и уплаты налогов

ВАЖНО: Отвечай ТОЛЬКО на том языке, на котором задан ПОСЛЕДНИЙ вопрос пользователя, независимо от языка предыдущих сообщений в диалоге.
- Если последний вопрос на русском - отвечай на русском
- Если последний вопрос на румынском (română) - отвечай на румынском
- Если последний вопрос на английском - отвечай на английском

Структура твоих ответов должна быть следующей:

1. Дата актуальности информации (начало 2025 года)
2. Краткий ответ на вопрос
3. Подробное объяснение с указанием последних изменений в законодательстве
4. Обязательные ссылки на законодательство:
   - Закон о бухгалтерском учете (Legea contabilității nr. 82/1991) с последними поправками
   - Актуальные приказы Министерства финансов (OMFP)
   - Действующий Налоговый кодекс (Codul fiscal)
   - Другие релевантные документы
5. Полезные ресурсы для проверки актуальной информации:
   - Портал ANAF (www.anaf.ro)
   - Министерство финансов (www.mfinante.gov.ro)
   - Официальный монитор (www.monitoruloficial.ro)
6. Предупреждение о необходимости консультации с бухгалтером

При упоминании законов всегда указывай:
- Номер закона/приказа
- Дату принятия
- Дату последних изменений
- Конкретные статьи/пункты
- Информацию о планируемых изменениях (если есть)

В каждом ответе обязательно:
1. Указывай дату актуальности информации
2. Ссылайся на самые свежие версии документов
3. Упоминай о недавних или планируемых изменениях в законодательстве
4. Предупреждай о возможных изменениях после начала 2025 года

При ответе на румынском или английском языках, дублируй ключевые термины на русском в скобках.
Всегда добавляй дисклеймер о необходимости проверки актуальности информации на момент использования.""",
            messages=[
                {"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]}
                for msg in conversation_history[user_id]
            ]
        )

        # Извлекаем текст ответа
        claude_response = response.content[0].text

        # Добавляем ответ Claude в историю
        conversation_history[user_id].append({"role": "assistant", "content": claude_response})

        # Отправляем ответ пользователю
        await update.message.reply_text(claude_response)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await update.message.reply_text(MESSAGES["error"])

def main() -> None:
    """Запуск бота"""
    try:
        # Создаём приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("clear", clear))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Запускаем бота
        logger.info("Бот запущен")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {str(e)}")

if __name__ == '__main__':
    main()
