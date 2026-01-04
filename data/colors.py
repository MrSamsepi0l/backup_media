# ============================================================================
# ANSI COLOR CODES
# ============================================================================
class AnsiCodes:
    """Raw ANSI escape codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


# ============================================================================
# SEMANTIC COLORS (Use these in your code)
# ============================================================================
class Colors:
    """Semantic terminal colors - auto-resets after each use"""

    # State colors
    PRIMARY = AnsiCodes.BLUE
    SUCCESS = AnsiCodes.GREEN
    DANGER = AnsiCodes.RED
    WARNING = AnsiCodes.YELLOW
    INFO = AnsiCodes.CYAN
    PROCESS = AnsiCodes.MAGENTA

    # Text colors
    TEXT = AnsiCodes.WHITE
    TEXT_MUTED = AnsiCodes.BRIGHT_BLACK
    TEXT_BOLD = AnsiCodes.BOLD

    # Special
    RESET = AnsiCodes.RESET

    @staticmethod
    def colorize(text, color):
        """Wrap text in color and auto-reset"""
        return f"{color}{text}{AnsiCodes.RESET}"