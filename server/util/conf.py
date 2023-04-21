from pathlib import Path
from typing import Final

JSON_PATH: Final = 'server/temp_files/path.json'
ENCODING: Final = 'utf-8'  # iso-8859-1, utf-8
CRLF: Final = '\r\n'
PROGRAM_FOLDERS: Final = ('.git', '.idea', 'logs', 'server', 'venv', '__pycache__', )
CLIENT_FOLDERS: Final = ('image', 'view', )
ALLOW_HEADERS: Final = ('Host', 'User-Agent', 'Accept', 'Content-Type', 'Content-Length', )
LOG_PATH: Final = Path('logs', 'server_log.log', )
