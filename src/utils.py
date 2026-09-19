import sys
import io


def ensure_utf8_console():
    """Force UTF-8 stdout on Windows so emoji print statements don't crash.

    Safe to call repeatedly: once the console is wrapped, its encoding is
    utf-8 so later calls are no-ops.
    """
    if (sys.platform == 'win32' and hasattr(sys.stdout, 'buffer')
            and 'utf-8' not in (getattr(sys.stdout, 'encoding', '') or '').lower()):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')