from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from data_fetcher import fetch_funding_data, calculate_funding_spread

def format_dataframe(df, is_spread=False):
    """Форматування DataFrame для Telegram."""
    lines = []
    if is_spread:
        # Для /spread: Symbol, Max Funding, Min Funding, Spread
        for _, row in df.iterrows():
            max_funding = f"{row['Max Funding (%)']:.6f}"
            min_funding = f"{row['Min Funding (%)']:.6f}"
            spread_value = f"{row['Spread (%)']:.6f}"
            line = (f"{row['Symbol']}:\n"
                    f"Max: {max_funding}% ({row['Max Exchange']})\n"
                    f"Min: {min_funding}% ({row['Min Exchange']})\n"
                    f"Spread: {spread_value}%")
            lines.append(line)
    else:
        # Для /rates: Symbol, Next Funding (%), Exchange
        for _, row in df.iterrows():
            funding_value = f"{row['Next Funding (%)']:.6f}"
            line = f"{row['Symbol']}: {funding_value}% ({row['Exchange']})"
            lines.append(line)
    return "\n\n".join(lines)  # Додаємо додатковий розрив між активами для читабельності

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /start."""
    await update.message.reply_text("Привіт! Я бот для моніторингу фандінг-рейтів.\n"
                                    "Доступні команди:\n"
                                    "/rates - Показати поточні фандінг-рейти\n"
                                    "/spread - Показати спред між біржами",
                                    parse_mode=None)

async def rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /rates."""
    data = fetch_funding_data()
    if data is None or data.empty:
        await update.message.reply_text("Не вдалося отримати дані.", parse_mode=None)
        return
    formatted_text = format_dataframe(data, is_spread=False)
    print("Formatted text for /rates:", formatted_text)  # Для дебагу
    await update.message.reply_text(f"Поточні фандінг-рейти:\n{formatted_text}", parse_mode=None)

async def spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /spread."""
    data = fetch_funding_data()
    if data is None or data.empty:
        await update.message.reply_text("Не вдалося отримати дані.", parse_mode=None)
        return
    spread_data = calculate_funding_spread(data)
    if spread_data is None or spread_data.empty:
        await update.message.reply_text("Недостатньо даних для розрахунку спреду.", parse_mode=None)
        return
    formatted_text = format_dataframe(spread_data, is_spread=True)
    print("Formatted text for /spread:", formatted_text)  # Для дебагу
    await update.message.reply_text(f"Спред фандінг-рейтів:\n{formatted_text}", parse_mode=None)

def run_bot():
    """Запуск Telegram-бота."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rates", rates))
    application.add_handler(CommandHandler("spread", spread))
    application.run_polling()

if __name__ == "__main__":
    run_bot()