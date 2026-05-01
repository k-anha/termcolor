# Copyright (c) 2008-2011 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

"""ANSI color formatting for output in terminal."""

from __future__ import annotations

import os
import sys
from functools import cache

ALL_COLORS: dict[str, tuple[int, int, int]] = {
    # Custom colors
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "light_pink": (255, 182, 193),
    "dark_pink": (255, 20, 147),
    "cherry_red": (255, 0, 0),
    "raspberry": (226, 30, 100),
    "blue_violet": (138, 43, 226),
    "indigo": (75, 0, 130),
    "violet": (238, 130, 238),
    "turquoise": (64, 224, 208),
    "teal": (0, 128, 128),
    "navy": (0, 0, 128),
    "sky_blue": (135, 206, 235),
    "steel_blue": (70, 130, 180),
    "light_steel_blue": (176, 196, 222),
    "slate_blue": (106, 90, 205),
    "slate_gray": (112, 128, 144),
    "light_slate_gray": (119, 136, 153),
    "light_slate_blue": (132, 112, 255),
    "medium_slate_blue": (123, 104, 238),
    "medium_purple": (147, 112, 219),
    "medium_orchid": (186, 85, 211),
    "medium_violet_red": (199, 21, 133),
    "dark_violet": (148, 0, 211),
    "dark_orchid": (153, 50, 204),
    "dark_magenta": (139, 0, 139),
    "dark_red": (139, 0, 0),
    "dark_green": (0, 100, 0),
    "dark_blue": (0, 0, 139),
    "dark_cyan": (0, 139, 139),
    "dark_yellow": (204, 204, 0),
    "dark_grey": (169, 169, 169),
    "light_grey": (211, 211, 211),
    "light_red": (255, 102, 102),
    "light_green": (102, 255, 102),
    "light_blue": (102, 102, 255),
    "light_cyan": (102, 255, 255),
    "light_yellow": (255, 255, 102),
    "light_magenta": (255, 102, 255),
    "light_orange": (255, 200, 0),
    "black": (0, 0, 0),
    "grey": (128, 128, 128),
    "red": (128, 0, 0),
    "green": (0, 128, 0),
    "yellow": (128, 128, 0),
    "blue": (0, 0, 128),
    "magenta": (128, 0, 128),
    "cyan": (0, 128, 128),
    "light_grey": (192, 192, 192),
    "dark_grey": (64, 64, 64),
    "light_red": (255, 0, 0),
    "light_green": (0, 255, 0),
    "light_yellow": (255, 255, 0),
    "light_blue": (0, 0, 255),
    "light_magenta": (255, 0, 255),
    "light_cyan": (0, 255, 255),
    "white": (255, 255, 255),
}


TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any


ATTRIBUTES: dict[str, int] = {
    "bold": 1,
    "dark": 2,
    "italic": 3,
    "underline": 4,
    "blink": 5,
    "reverse": 7,
    "concealed": 8,
    "strike": 9,
}

# Replacing "on_" prefix for highlights with a separate HIGHLIGHTS dictionary to improve code organization and readability. This way we can easily manage text colors and background colors separately, making the code cleaner and more maintainable.

HIGHLIGHTS: dict[str, int] = {
    "black": 40,
    "grey": 40,  # Actually black but kept for backwards compatibility
    "red": 41,
    "green": 42,
    "yellow": 43,
    "blue": 44,
    "magenta": 45,
    "cyan": 46,
    "light_grey": 47,
    "dark_grey": 100,
    "light_red": 101,
    "light_green": 102,
    "light_yellow": 103,
    "light_blue": 104,
    "light_magenta": 105,
    "light_cyan": 106,
    "white": 107,
}

COLORS: dict[str, int] = {
    "black": 30,
    "grey": 30,  # Actually black but kept for backwards compatibility
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "light_grey": 37,
    "dark_grey": 90,
    "light_red": 91,
    "light_green": 92,
    "light_yellow": 93,
    "light_blue": 94,
    "light_magenta": 95,
    "light_cyan": 96,
    "white": 97,
}


RESET = "\033[0m"


@cache
def can_colorize(
    *, no_color: bool | None = None, force_color: bool | None = None
) -> bool:
    """Check env vars and for tty/dumb terminal"""
    # First check overrides:
    # "User-level configuration files and per-instance command-line arguments should
    # override $NO_COLOR. A user should be able to export $NO_COLOR in their shell
    # configuration file as a default, but configure a specific program in its
    # configuration file to specifically enable color."
    # https://no-color.org
    if no_color is not None and no_color:
        return False
    if force_color is not None and force_color:
        return True

    # Then check env vars:
    if os.environ.get("ANSI_COLORS_DISABLED"):
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True

    # Then check system:
    if os.environ.get("TERM") == "dumb":
        return False
    if not hasattr(sys.stdout, "fileno"):
        return False

    try:
        return os.isatty(sys.stdout.fileno())
    except OSError:
        return sys.stdout.isatty()


def _check_rgb(rgb: tuple[int, int, int]) -> None:
    if len(rgb) != 3 or not all(0 <= c <= 255 for c in rgb):
        msg = f"Expected a tuple of 3 ints in range 0-255, got {rgb!r}"
        raise ValueError(msg)


def colored(
    text: object,
    color: str | tuple[int, int, int] | None = None,
    on_color: str | tuple[int, int, int] | None = None,
    attrs: Iterable[str] | None = None,
    *,
    no_color: bool | None = None,
    force_color: bool | None = None,
) -> str:
    """Colorize text.

    Available text colors:
        black, red, green, yellow, blue, magenta, cyan, white,
        light_grey, dark_grey, light_red, light_green, light_yellow, light_blue,
        light_magenta, light_cyan.

    Available text highlights:
        on_black, on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white,
        on_light_grey, on_dark_grey, on_light_red, on_light_green, on_light_yellow,
        on_light_blue, on_light_magenta, on_light_cyan.

    Alternatively, both text colors (color) and highlights (on_color) may
    be specified via a tuple of 0-255 ints (R, G, B).

    Available attributes:
        bold, dark, italic, underline, blink, reverse, concealed, strike.

    Example:
        colored('Hello, World!', 'red', 'on_black', ['bold', 'blink'])
        colored('Hello, World!', 'green')
        colored('Hello, World!', (255, 0, 255))  # Purple
    """
    result = str(text)
    if not can_colorize(no_color=no_color, force_color=force_color):
        return result

    # Replacing format specifiers with f-strings for better readability and performance.
    # The original code used old-style string formatting with the % operator, which can be less efficient and harder to read compared to f-strings.
    # By using f-strings, we can directly embed expressions inside string literals, making the code cleaner and more concise.

    if color is not None:
        # Using try except to handle the case when color is not found in COLORS or CUSTOM_COLORS. This way we can provide a more informative error message instead of just raising a KeyError.
        try:
            if (
                isinstance(color, str) and color in COLORS
            ):  # Checking if color is in string format and exists in COLORS dictionary.
                result = f"\033[{COLORS[color]}m{result}"
            elif isinstance(
                color, tuple
            ):  # Checking for color to be rgb tuple and validating it using _check_rgb function. If valid, applying the color using ANSI escape code for 24-bit color.
                _check_rgb(color)
                result = f"\033[38;2;{color[0]};{color[1]};{color[2]}m{result}"
            else:  # Finally checking if color is in CUSTOM_COLORS dictionary. If found, validating it as rgb tuple and applying the color using ANSI escape code for 24-bit color.
                _check_rgb(ALL_COLORS[color])
                result = f"\033[38;2;{ALL_COLORS[color][0]};{ALL_COLORS[color][1]};{ALL_COLORS[color][2]}m{result}"
        except (
            KeyError
        ):  # Raising error if color is not found in any of the dictionaries and providing a clear message about the missing color.
            raise ValueError(f"Color not found: {color!r}")

    if on_color is not None:
        try:
            if (
                isinstance(on_color, str) and on_color in HIGHLIGHTS
            ):  # Checking if on_color is in string format and exists in HIGHLIGHTS dictionary.
                result = f"\033[{HIGHLIGHTS[on_color]}m{result}"
            elif isinstance(
                on_color, tuple
            ):  # Checking for on_color to be rgb tuple and validating it using _check_rgb function. If valid, applying the background color using ANSI escape code for 24-bit color.
                _check_rgb(on_color)
                result = f"\033[48;2;{on_color[0]};{on_color[1]};{on_color[2]}m{result}"
            else:
                _check_rgb(ALL_COLORS[on_color])
                result = f"\033[48;2;{ALL_COLORS[on_color][0]};{ALL_COLORS[on_color][1]};{ALL_COLORS[on_color][2]}m{result}"
        except (
            KeyError
        ):  # Raising error if color is not found in any of the dictionaries and providing a clear message about the missing color.
            raise ValueError(f"Color not found: {on_color!r}")

    if attrs is not None:
        for attr in attrs:
            result = f"\033[{ATTRIBUTES[attr]}m{result}"

    result += RESET

    return result


def cprint(
    text: object,
    color: str | tuple[int, int, int] | None = None,
    on_color: str | tuple[int, int, int] | None = None,
    attrs: Iterable[str] | None = None,
    *,
    no_color: bool | None = None,
    force_color: bool | None = None,
    **kwargs: Any,
) -> None:
    """Print colorized text.

    It accepts arguments of print function.
    """

    print(
        (
            colored(
                text,
                color,
                on_color,
                attrs,
                no_color=no_color,
                force_color=force_color,
            )
        ),
        **kwargs,
    )


def generate_gradient(
    start_color: tuple[int, int, int] | str,
    end_color: tuple[int, int, int] | str,
    steps: int,
) -> list[tuple[int, int, int]]:
    """Generates a gradient of colors between two specified colors.

    Args:
        start_color (tuple[int, int, int]|str): The starting color as an RGB tuple or a named color.
        end_color (tuple[int, int, int]|str): The ending color as an RGB tuple or a named color.
        steps (int): The number of colors to generate in the gradient.

    Returns:
        list[tuple[int, int, int]]: A list of RGB tuples representing the gradient colors.
    """
    gradient: list[tuple[int, int, int]] = []

    if isinstance(start_color, str):
        start_color = ALL_COLORS.get(start_color, (0, 0, 0))
    if isinstance(end_color, str):
        end_color = ALL_COLORS.get(end_color, (0, 0, 0))

    for i in range(steps):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * i / (steps - 1))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * i / (steps - 1))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * i / (steps - 1))
        gradient.append((r, g, b))
    return gradient


def gradient_text(
    text: str,
    start_color: tuple[int, int, int] | str,
    end_color: tuple[int, int, int] | str,
    on_color: str | tuple[int, int, int] | None = None,
    attrs: list[str] | None = None,
    *,
    force_color: bool | None = None,
    no_color: bool | None = None,
) -> None:
    """Prints text with a gradient of colors between two specified colors.

    Args:
        text (str): The text to be printed.
        start_color (tuple[int, int, int]|str): The starting color as an RGB tuple or a named color.
        end_color (tuple[int, int, int]|str): The ending color as an RGB tuple or a named color.
    """
    steps = len(text)
    gradient_colors = generate_gradient(start_color, end_color, steps)
    for i in range(len(text)):
        cprint(
            text=text[i],
            color=gradient_colors[i],
            on_color=on_color,
            attrs=attrs,
            force_color=force_color,
            no_color=no_color,
            end="",
        )
    print()


generate_gradient.__doc__ = (
    """Generates a gradient of colors between two specified colors."""
)
generate_gradient.__annotations__ = {
    "start_color": "tuple[int, int, int] | str",
    "end_color": "tuple[int, int, int] | str",
    "steps": "int",
    "return": "list[tuple[int, int, int]]",
}
gradient_text.__doc__ = (
    """Prints text with a gradient of colors between two specified colors."""
)
gradient_text.__annotations__ = {
    "text": "str",
    "start_color": "tuple[int, int, int] | str",
    "end_color": "tuple[int, int, int] | str",
    "on_color": "str | tuple[int, int, int] | None",
    "attrs": "list[str] | None",
    "force_color": "bool | None",
    "no_color": "bool | None",
}
