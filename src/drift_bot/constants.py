from typing import Literal


# Разрешённое количество попыток
ATTEMPT = Literal[1, 2]

CRITERION = Literal[
    "STYLE",  # Судья стиля
    "ANGLE",  # Судья угла
    "LINE"  # Судья траектории
]
