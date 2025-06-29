
CHAMPIONSHIP_TEMPLATE = """<b><u>Информация о чемпионате 🏆</u></b>

📌 <b>Название:</b> {title}
📝 <b>Описание:</b> {description}
🔢 <b>Количество этапов</b>: {stages_count}

#championship #drift
"""

STAGE_TEMPLATE = """<b><u>Информация о этапе 🏁</u></b>

📌 <b>Название:</b> {title}
📝 <b>Описание:</b> {description}
📍 <b>Место:</b> {location}
🗺️ <b>Как добраться:</b> {map_link}
🗓 <b>Дата проведения:</b> {date}

#stage #drift
"""

JUDGE_TEMPLATE = """<b><u>Информация о судье<u></b>

👤 <b>ФИО</b>: {full_name}
🗳️ <b>Оцениваемый критерий</b>: {criterion}

#judge #drift
"""

PILOT_TEMPLATE = """🏁 <b><u>Информация о пилоте</u></b> 🏁

👤 <b>ФИО:</b>: {full_name}
🎂 <b>Возраст:</b> {age}
📝 <b>Описание:</b> {description}

🏎️ <b>Автомобиль:</b> {car}

📅 <b>Дата регистрации</b> {created_at}

#pilot #drift
"""
