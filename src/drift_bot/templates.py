

ADMIN_COMMANDS_TEXT = """<b><u>Доступные команды</u></b>

 * /create_championship - создаёт чемпионат
 * /championships - получает все чемпионаты
"""

JUDGE_COMMANDS_TEXT = """<b><u>Доступные команды</u></b>

 * /active_championships
"""

CHAMPIONSHIP_TEMPLATE = """<b><u>Информация о чемпионате 🏆</u></b>

📌 <b>Название:</b> {title}
📝 <b>Описание:</b> {description}
🔢 <b>Количество этапов</b>: {stages_count}

#championship #drift
"""

STAGE_TEMPLATE = """📌 <b>Название:</b> {title}
📝 <b>Описание:</b> {description}
📍 <b>Место:</b> {location}
🗺️ <b>Как добраться:</b> {map_link}
🗓 <b>Дата:</b> {date}

#stage #drift
"""

SUBMIT_JUDGE_REGISTRATION_TEMPLATE = """<b><u>Информация о судье<u></b>

👤 <b>ФИО</b>: {full_name}
🗳️ <b>Оцениваемый критерий</b>: {criterion}
"""

REGISTERED_PILOT_TEMPLATE = """🏁 <b><u>Информация о пилоте</u></b> 🏁

👤 <b>ФИО:</b>: {full_name}
🎂 <b>Возраст:</b> {age}
📝 <b>Описание:</b> {description}

🏎️ <b>Автомобиль:</b> {car}

📅 <b>Дата регистрации</b> {created_at}

#pilot #drift
"""

START_ADMIN_MESSAGE = """<b><u>Доступные команды</u></b>

<b>Мероприятия (Дрифт этапы, гонки, ивенты ...)
 * /create_event - Создаёт мероприятие
 * /events - Получить все созданные мероприятия
"""

START_PILOT_MESSAGE = """...
"""

JUDGE_COMMANDS_MESSAGE = """<b><u>Доступные команды</u></b>

 * /event - Ваше текущее мероприятие на которое вы зарегистрированы.
 * /give_points - Выставить баллы за квалификацию.
 * /vote - Проголосовать за пилота.
 * /my_profile
"""

REGISTERED_JUDGE_TEMPLATE = """<b><u>Информация о судье<u></b>

👤 <b>ФИО</b>: {full_name}
🗳️ <b>Оцениваемый критерий</b>: {criterion}

📅 <b>Дата регистрации</b>: {created_at}
"""
