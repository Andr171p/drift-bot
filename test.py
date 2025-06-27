from src.drift_bot.bot.keyboards import CalendarKeyboard

calendar = CalendarKeyboard()

print(calendar._get_month_days(year=2025, month=6))