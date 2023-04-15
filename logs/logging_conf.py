import logging

# Создаем логгер
logger = logging.getLogger('Server Logger')
logger.setLevel(logging.DEBUG)

# Создаем обработчик для записи логов в файл
file_handler = logging.FileHandler('../server_log.log')
file_handler.setLevel(logging.INFO)

# Создаем обработчик для вывода логов на консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создаем форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Устанавливаем форматтер для обработчиков
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавляем обработчики в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)
