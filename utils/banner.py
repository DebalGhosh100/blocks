"""
Banner - Compute the width used for #/= banner rules in cocoon's logs.

Centralised so block_executor and any other module that prints
boundaries renders them at the same width.
"""

import os
import shutil


def banner_width() -> int:
    """Width (columns) for #/= banner rules.

    Tries, in order:
      1. shutil.get_terminal_size() (works in real TTYs)
      2. $COLUMNS environment variable
      3. $COCOON_BANNER_WIDTH (override for non-TTY envs like Jenkins)
      4. fallback of 80

    Result is clamped to a minimum of 40 so banners always render.
    """
    cols = 0
    try:
        cols = shutil.get_terminal_size(fallback=(0, 0)).columns
    except Exception:
        cols = 0
    if not cols:
        try:
            cols = int(os.environ.get('COLUMNS', '') or 0)
        except ValueError:
            cols = 0
    if not cols:
        try:
            cols = int(os.environ.get('COCOON_BANNER_WIDTH', '') or 0)
        except ValueError:
            cols = 0
    if not cols:
        cols = 80
    return max(cols, 40)
