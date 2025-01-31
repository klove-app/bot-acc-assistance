import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем значения из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Проверка наличия переменных
if not TELEGRAM_TOKEN or not ANTHROPIC_API_KEY:
    raise ValueError("Отсутствуют необходимые переменные окружения")

# Настройки бота
MAX_HISTORY_LENGTH = 10
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096

# Сообщения бота
MESSAGES = {
    "welcome": """Привет! Я бот, который поможет вам общаться с Claude от Anthropic.

Команды:
/start - Начать новый диалог
/clear - Очистить историю диалога
/help - Показать это сообщение

Просто напишите ваше сообщение, и я передам его Claude.""",
    
    "history_cleared": "История диалога очищена.",
    
    "error": """Произошла ошибка при обработке вашего запроса. 
Пожалуйста, попробуйте позже или обратитесь к администратору.""",
    
    "rate_limit": "Превышен лимит запросов. Пожалуйста, подождите немного и попробуйте снова.",
    
    "timeout": "Превышено время ожидания ответа. Пожалуйста, попробуйте снова.",
    
    "maintenance": "Бот временно находится на техническом обслуживании. Пожалуйста, попробуйте позже."
}

# Настройки логирования
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
