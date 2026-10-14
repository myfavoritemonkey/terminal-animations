"""Small, dependency-free terminal animation runner."""

import argparse
import shutil
import sys
import time


def animate(title, render, default_fps=20, continuous=False):
    parser = argparse.ArgumentParser(description=title)
    parser.add_argument("--fps", type=float, default=default_fps,
                        help=f"frames per second (default: {default_fps:g})")
    parser.add_argument("--frames", type=int, help="stop after this many frames")
    parser.add_argument("--width", type=int, help="canvas width (default: terminal width)")
    parser.add_argument("--height", type=int, help="canvas height (default: terminal height minus one)")
    parser.add_argument("--no-color", action="store_true", help="use plain characters")
    args = parser.parse_args()
    if args.fps <= 0 or (args.frames is not None and args.frames < 1):
        parser.error("--fps must be positive and --frames must be at least 1")
    if args.width is not None and args.width < 10:
        parser.error("--width must be at least 10")
    if args.height is not None and args.height < 5:
        parser.error("--height must be at least 5")

    interactive = sys.stdout.isatty()
    color = interactive and not args.no_color
    limit = (args.frames if args.frames is not None else
             None if interactive or continuous else 1)
    if interactive:
        sys.stdout.write("\x1b[?1049h\x1b[?25l")
        sys.stdout.flush()
    try:
        frame = 0
        deadline = time.monotonic()
        while limit is None or frame < limit:
            columns, lines = shutil.get_terminal_size((80, 24))
            width = args.width or columns
            height = args.height or max(5, lines - 1)
            picture = render(frame / args.fps, width, height, color)
            if interactive:
                sys.stdout.write("\x1b[H" + picture + "\x1b[0m\x1b[J")
            else:
                sys.stdout.write(picture + "\n")
            sys.stdout.flush()
            frame += 1
            deadline += 1 / args.fps
            delay = deadline - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                deadline = time.monotonic()
    except (KeyboardInterrupt, BrokenPipeError):
        pass
    finally:
        if interactive:
            sys.stdout.write("\x1b[0m\x1b[?25h\x1b[?1049l")
            sys.stdout.flush()


def color_row(cells, enabled):
    """Turn (character, ANSI color) pairs into one terminal row."""
    if not enabled:
        return "".join(character for character, _ in cells)
    result = []
    current = None
    for character, code in cells:
        if code != current:
            result.append(f"\x1b[{code}m" if code else "\x1b[0m")
            current = code
        result.append(character)
    result.append("\x1b[0m")
    return "".join(result)
