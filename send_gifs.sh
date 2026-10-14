#!/bin/sh
# Send the generated GIFs one at a time, in the same order as the animations.
set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
cd "$script_dir/gifs"

if ! command -v send >/dev/null 2>&1; then
    printf '%s\n' 'Ошибка: команда send не найдена.' >&2
    exit 1
fi

files='globe.gif donut.gif star.gif eiffel.gif satellite.gif life.gif cat_and_mouse.gif cigarette.gif monkey.gif'

# Check everything first so a missing file cannot interrupt a partial batch.
for gif in $files; do
    if [ ! -f "$gif" ]; then
        printf 'Ошибка: файл не найден: %s\n' "$gif" >&2
        exit 1
    fi
done

for gif in $files; do
    printf 'Отправка: %s\n' "$gif"
    if ! send "$gif"; then
        printf 'Ошибка отправки: %s. Скрипт остановлен.\n' "$gif" >&2
        exit 1
    fi
done

printf '%s\n' 'Все GIF отправлены.'
