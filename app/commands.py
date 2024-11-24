from aiogram import Bot
from aiogram.types import BotCommand

async def set_commands(bot: Bot):
  commands = [
    BotCommand(command='/start', description='Запуск бота'),
    BotCommand(command='/get-recommendation', description='Получить рекомендацию'),
    BotCommand(command='/get-your-unique-color', description='Получить цвет на основе твоего вкуса'),
  ]
  await bot.set_my_commands(commands)