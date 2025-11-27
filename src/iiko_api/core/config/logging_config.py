from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает logger с именем модуля для контекста в логах.
    
    Библиотека использует стандартный модуль logging и не управляет
    его конфигурацией. Пользователь может настроить логирование
    через стандартные механизмы Python logging.
    
    :param name: Имя модуля/компонента для контекста в логах
    :return: Logger с именем модуля
    """
    return logging.getLogger(name)



