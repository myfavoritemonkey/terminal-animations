"""Record a Python terminal animation as a GIF (requires ffmpeg)."""

import argparse
import codecs
import errno
import fcntl
from fractions import Fraction
import importlib.util
import os
from pathlib import Path
import pty
import select
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import time
import unicodedata
from xml.sax.saxutils import escape


DEFAULT_FG = (230, 230, 230)
DEFAULT_BG = (0, 0, 0)
ANSI_COLORS = (
    (0, 0, 0), (205, 49, 49), (13, 188, 121), (229, 229, 16),
    (36, 114, 200), (188, 63, 188), (17, 168, 205), (229, 229, 229),
    (102, 102, 102), (241, 76, 76), (35, 209, 139), (245, 245, 67),
    (59, 142, 234), (214, 112, 214), (41, 184, 219), (255, 255, 255),
)


def ansi_256(index):
    if index < 16:
        return ANSI_COLORS[index]
    if index < 232:
        value = index - 16
        levels = (0, 95, 135, 175, 215, 255)
        return (levels[value // 36], levels[(value // 6) % 6], levels[value % 6])
    gray = 8 + (index - 232) * 10
    return (gray, gray, gray)


class Terminal:
    """The ANSI controls commonly used by full-screen Python animations."""

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.fg, self.bg = DEFAULT_FG, DEFAULT_BG
        self.bold = self.reverse = False
        self.row = self.col = 0
        self.grid = [self.blank_row() for _ in range(height)]
        self.state = "normal"
        self.control = ""
        self.completed = None

    def blank_row(self):
        return [(" ", DEFAULT_FG, self.bg) for _ in range(self.width)]

    def snapshot(self):
        return tuple(tuple(row) for row in self.grid)

    def scroll(self):
        while self.row >= self.height:
            self.grid.pop(0)
            self.grid.append(self.blank_row())
            self.row -= 1

    def write_char(self, char):
        if unicodedata.combining(char):
            if self.col:
                old, fg, bg = self.grid[self.row][self.col - 1]
                self.grid[self.row][self.col - 1] = (old + char, fg, bg)
            return
        if self.col >= self.width:
            self.col = 0
            self.row += 1
            self.scroll()
        fg, bg = (self.bg, self.fg) if self.reverse else (self.fg, self.bg)
        self.grid[self.row][self.col] = (char, fg, bg)
        self.col += 1
        if unicodedata.east_asian_width(char) in "WF" and self.col < self.width:
            self.grid[self.row][self.col] = (" ", fg, bg)
            self.col += 1

    def sgr(self, params):
        codes = [int(item) if item else 0 for item in params.split(";")] if params else [0]
        index = 0
        while index < len(codes):
            code = codes[index]
            if code == 0:
                self.fg, self.bg = DEFAULT_FG, DEFAULT_BG
                self.bold = self.reverse = False
            elif code == 1:
                self.bold = True
            elif code == 22:
                self.bold = False
            elif code == 7:
                self.reverse = True
            elif code == 27:
                self.reverse = False
            elif code == 39:
                self.fg = DEFAULT_FG
            elif code == 49:
                self.bg = DEFAULT_BG
            elif 30 <= code <= 37:
                self.fg = ANSI_COLORS[code - 30 + (8 if self.bold else 0)]
            elif 90 <= code <= 97:
                self.fg = ANSI_COLORS[code - 90 + 8]
            elif 40 <= code <= 47:
                self.bg = ANSI_COLORS[code - 40]
            elif 100 <= code <= 107:
                self.bg = ANSI_COLORS[code - 100 + 8]
            elif code in (38, 48) and index + 2 < len(codes):
                if codes[index + 1] == 5:
                    chosen = ansi_256(max(0, min(255, codes[index + 2])))
                    index += 2
                elif codes[index + 1] == 2 and index + 4 < len(codes):
                    chosen = tuple(max(0, min(255, n)) for n in codes[index + 2:index + 5])
                    index += 4
                else:
                    index += 1
                    continue
                if code == 38:
                    self.fg = chosen
                else:
                    self.bg = chosen
            index += 1

    def csi(self, body, command):
        private = body.startswith("?")
        values = body.lstrip("?").split(";")

        def number(position, default=1):
            return int(values[position]) if position < len(values) and values[position] else default

        if command == "m":
            self.sgr(body)
        elif private and command == "h" and "1049" in values:
            self.grid = [self.blank_row() for _ in range(self.height)]
            self.row = self.col = 0
            self.completed = None
        elif command in "Hf":
            self.row = max(0, min(self.height - 1, number(0) - 1))
            self.col = max(0, min(self.width - 1, number(1) - 1))
        elif command == "A":
            self.row = max(0, self.row - number(0))
        elif command == "B":
            self.row = min(self.height - 1, self.row + number(0))
        elif command == "C":
            self.col = min(self.width - 1, self.col + number(0))
        elif command == "D":
            self.col = max(0, self.col - number(0))
        elif command == "G":
            self.col = max(0, min(self.width - 1, number(0) - 1))
        elif command == "d":
            self.row = max(0, min(self.height - 1, number(0) - 1))
        elif command in "JK":
            mode = number(0, 0)
            for row in range(self.height):
                if command == "K" and row != self.row:
                    continue
                for col in range(self.width):
                    before = row < self.row or (row == self.row and col < self.col)
                    after = row > self.row or (row == self.row and col >= self.col)
                    if mode == 2 or (mode == 0 and after) or (mode == 1 and before):
                        self.grid[row][col] = (" ", DEFAULT_FG, self.bg)
            if command == "J" and mode == 0 and self.row >= self.height - 2:
                self.completed = self.snapshot()
            elif command == "J" and mode == 2:
                self.completed = None

    def feed(self, data):
        for char in data:
            if self.state == "normal":
                if char == "\x1b":
                    self.state = "escape"
                elif char == "\r":
                    self.col = 0
                elif char == "\n":
                    self.row += 1
                    self.col = 0
                    self.scroll()
                elif char == "\b":
                    self.col = max(0, self.col - 1)
                elif char == "\t":
                    self.col = min(self.width, (self.col // 8 + 1) * 8)
                elif char >= " ":
                    self.write_char(char)
            elif self.state == "escape":
                if char == "[":
                    self.state, self.control = "csi", ""
                elif char == "]":
                    self.state = "osc"
                else:
                    self.state = "normal"
            elif self.state == "csi":
                if "@" <= char <= "~":
                    self.csi(self.control, char)
                    self.state = "normal"
                elif len(self.control) < 128:
                    self.control += char
                else:
                    self.state = "normal"
            elif self.state == "osc":
                if char == "\x07":
                    self.state = "normal"
                elif char == "\x1b":
                    self.state = "osc_escape"
            elif self.state == "osc_escape":
                self.state = "normal" if char == "\\" else "osc"


def stop_process(process):
    if process.poll() is not None:
        return
    for sig, timeout in ((signal.SIGINT, 1), (signal.SIGTERM, 1), (signal.SIGKILL, 1)):
        try:
            os.killpg(process.pid, sig)
            process.wait(timeout=timeout)
            break
        except ProcessLookupError:
            break
        except subprocess.TimeoutExpired:
            continue


def capture(script, script_args, seconds, fps, width, height):
    emulator = Terminal(width, height)
    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", height, width, 0, 0))
    environment = os.environ.copy()
    environment.update(TERM="xterm-256color", COLORTERM="truecolor",
                       COLUMNS=str(width), LINES=str(height), PYTHONUNBUFFERED="1")
    process = subprocess.Popen([sys.executable, "-u", str(script), *script_args],
                               stdin=slave, stdout=slave, stderr=slave,
                               cwd=script.parent, env=environment,
                               start_new_session=True)
    os.close(slave)
    decoder = codecs.getincrementaldecoder("utf-8")("replace")
    count = max(1, round(seconds * fps))
    frames = []
    start = None
    startup_deadline = time.monotonic() + 10
    last_output = time.monotonic()
    try:
        while len(frames) < count:
            if start is None:
                if emulator.completed is not None:
                    start = time.monotonic()
                    frames.append(emulator.completed)
                    continue
                if time.monotonic() >= startup_deadline:
                    raise RuntimeError("Animation did not draw a frame within 10 seconds")
                ready, _, _ = select.select([master], [], [], 0.05)
                if ready:
                    try:
                        chunk = os.read(master, 65536)
                    except OSError as error:
                        if error.errno == errno.EIO:
                            continue
                        raise
                    if chunk:
                        emulator.feed(decoder.decode(chunk))
                        last_output = time.monotonic()
                elif (time.monotonic() - last_output >= 0.1
                      and any(char != " " or bg != DEFAULT_BG
                              for row in emulator.grid for char, _, bg in row)):
                    start = time.monotonic()
                    frames.append(emulator.snapshot())
                elif process.poll() is not None:
                    raise RuntimeError(f"Animation exited before drawing a frame (exit code {process.returncode})")
                continue
            deadline = start + (len(frames) + 1) * seconds / count
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                frames.append(emulator.completed or emulator.snapshot())
                continue
            if process.poll() is not None:
                # Hold the last frame for the requested GIF duration.
                frames.extend([emulator.completed or emulator.snapshot()] * (count - len(frames)))
                break
            ready, _, _ = select.select([master], [], [], min(remaining, 0.05))
            if ready:
                try:
                    chunk = os.read(master, 65536)
                except OSError as error:
                    if error.errno == errno.EIO:
                        continue
                    raise
                if chunk:
                    emulator.feed(decoder.decode(chunk))
    finally:
        stop_process(process)
        os.close(master)
    return frames


def render_offline(script, seconds, fps, width, height):
    """Render scripts exposing render(t, width, height, color) at exact time steps."""
    spec = importlib.util.spec_from_file_location("recorded_animation", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {script}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(script.parent))
    try:
        spec.loader.exec_module(module)
        render = getattr(module, "render", None)
        if not callable(render):
            raise RuntimeError(f"{script.name} has no render(t, width, height, color) function")
        count = max(1, round(seconds * fps))
        frames = []
        for index in range(count):
            emulator = Terminal(width, height)
            emulator.feed("\x1b[H" + render(index * seconds / count, width, height, True))
            frames.append(emulator.snapshot())
        return frames
    finally:
        sys.path.pop(0)


def hex_color(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def save_svg(frame, path, cell_width, cell_height):
    width = len(frame[0]) * cell_width
    height = len(frame) * cell_height
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
             f'<rect width="{width}" height="{height}" fill="{hex_color(DEFAULT_BG)}"/>']
    for row, cells in enumerate(frame):
        y = row * cell_height
        for col, (char, fg, bg) in enumerate(cells):
            x = col * cell_width
            if char == " ":
                if bg != DEFAULT_BG:
                    parts.append(f'<rect x="{x}" y="{y}" width="{cell_width}" '
                                 f'height="{cell_height}" fill="{hex_color(bg)}"/>')
                continue
            if char in "▀▄█":
                if char == "▀":
                    top, bottom = fg, bg
                elif char == "▄":
                    top, bottom = bg, fg
                else:
                    top = bottom = fg
                half = cell_height // 2
                parts.append(f'<rect x="{x}" y="{y}" width="{cell_width}" '
                             f'height="{half}" fill="{hex_color(top)}"/>')
                parts.append(f'<rect x="{x}" y="{y + half}" width="{cell_width}" '
                             f'height="{cell_height - half}" fill="{hex_color(bottom)}"/>')
                continue
            if bg != DEFAULT_BG:
                parts.append(f'<rect x="{x}" y="{y}" width="{cell_width}" '
                             f'height="{cell_height}" fill="{hex_color(bg)}"/>')
            baseline = y + round(cell_height * 0.79)
            parts.append(f'<text x="{x}" y="{baseline}" fill="{hex_color(fg)}" '
                         f'font-family="FreeMono, monospace" font-size="{round(cell_height * 0.85)}" '
                         f'xml:space="preserve">{escape(char)}</text>')
    parts.append("</svg>")
    path.write_text("".join(parts), encoding="utf-8")


def make_gif(frames, destination, frame_rate, cell_width, cell_height):
    with tempfile.TemporaryDirectory(prefix="terminal-gif-") as directory:
        work = Path(directory)
        for index, frame in enumerate(frames):
            save_svg(frame, work / f"frame_{index:05d}.svg", cell_width, cell_height)
        source = str(work / "frame_%05d.svg")
        palette = str(work / "palette.png")
        common = ["ffmpeg", "-hide_banner", "-loglevel", "error",
                  "-threads", "1", "-y"]
        subprocess.run(common + ["-framerate", frame_rate, "-i", source,
                                 "-vf", "palettegen=stats_mode=full:reserve_transparent=0", palette],
                       check=True)
        subprocess.run(common + ["-framerate", frame_rate, "-i", source,
                                 "-i", palette, "-lavfi", "paletteuse=dither=sierra2_4a:diff_mode=rectangle",
                                 "-loop", "0", str(destination)], check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Record a Python terminal animation to a GIF (ffmpeg required).")
    parser.add_argument("script", type=Path, help="Python animation file")
    parser.add_argument("--seconds", type=float, default=30,
                        help="GIF duration in seconds (default: 30)")
    parser.add_argument("--fps", type=int, default=15,
                        help="GIF frames per second (default: 15)")
    parser.add_argument("--width", type=int, default=80, help="terminal columns (default: 80)")
    parser.add_argument("--height", type=int, default=25, help="terminal rows (default: 25)")
    parser.add_argument("--cell-width", type=int, default=16,
                        help="pixels per terminal column (default: 16)")
    parser.add_argument("--cell-height", type=int, default=32,
                        help="pixels per terminal row (default: 32)")
    parser.add_argument("--offline", action="store_true",
                        help="render exact frames from a script's render(t, width, height, color) function")
    parser.add_argument("--output", type=Path, help="output GIF (default: script name + .gif)")
    args, script_args = parser.parse_known_args()
    if (args.seconds <= 0 or args.fps <= 0 or args.width < 10 or args.height < 5
            or args.cell_width < 4 or args.cell_height < 8):
        parser.error("seconds/fps must be positive; width >= 10, height >= 5, cell size >= 4x8")
    if args.offline and script_args:
        parser.error("animation arguments cannot be used with --offline")
    script = args.script.expanduser().resolve()
    if not script.is_file():
        parser.error(f"Python file not found: {script}")
    if shutil.which("ffmpeg") is None:
        parser.error("ffmpeg is required and was not found in PATH")
    destination = (args.output or Path.cwd() / (script.stem + ".gif")).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Recording {args.seconds:g} seconds from {script.name}...", flush=True)
    frames = (render_offline(script, args.seconds, args.fps, args.width, args.height)
              if args.offline else
              capture(script, script_args, args.seconds, args.fps, args.width, args.height))
    print(f"Rendering {len(frames)} frames...", flush=True)
    rate = Fraction(len(frames), 1) / Fraction(str(args.seconds))
    frame_rate = f"{rate.numerator}/{rate.denominator}"
    make_gif(frames, destination, frame_rate, args.cell_width, args.cell_height)
    print(f"Saved: {destination}")


if __name__ == "__main__":
    main()
