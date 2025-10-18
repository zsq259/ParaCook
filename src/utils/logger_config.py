import logging, os, re

RESET = "\x1b[0m"
COLOR_CODES = {
    'BLACK': "\x1b[30m",
    'RED': "\x1b[31m",
    'GREEN': "\x1b[32m",
    'YELLOW': "\x1b[33m",
    'BLUE': "\x1b[34m",
    'PURPLE': "\x1b[35m",
    'CYAN': "\x1b[36m",
    'WHITE': "\x1b[37m",
    'BOLD': "\x1b[1m",
    'UNDERLINE': "\x1b[4m",
    'REVERSE': "\x1b[7m",
    'BG_BLACK': "\x1b[40m",
    'BG_RED': "\x1b[41m",
    'BG_GREEN': "\x1b[42m",
    'BG_YELLOW': "\x1b[43m",
    'BG_BLUE': "\x1b[44m",
    'BG_PURPLE': "\x1b[45m",
    'BG_CYAN': "\x1b[46m",
    'BG_WHITE': "\x1b[47m",
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        return super().format(record)
    
class AnsiStrippingFormatter(logging.Formatter):
    ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
    def format(self, record):
        text = super().format(record)
        return self.ANSI_RE.sub('', text)

class ExcludeModelLogFilter(logging.Filter):
    def filter(self, record):
        return not getattr(record, "model_log", False)

handler = logging.StreamHandler()
formatter = ColoredFormatter('%(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def set_log_dir(log_dir: str, file_name: str = "env.log", keep_colors: bool = False):
    """Set the log directory and file name for the logger."""
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, file_name))
    # file_formatter = logging.Formatter('%(message)s')
    file_formatter = ColoredFormatter('%(message)s') if keep_colors else AnsiStrippingFormatter('%(message)s')
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(ExcludeModelLogFilter())
    logger.addHandler(file_handler)

def log_model_conversation(massage: str):
    """Log the model conversation to the logger."""
    logger.info(massage, extra={"model_log": True})