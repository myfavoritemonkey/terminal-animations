#!/bin/sh
set -eu

cd "$(dirname "$0")"
mkdir -p gifs

# The connected display is 1280x800. Match or exceed it for every GIF.
# Procedural 3D scenes use more terminal cells for additional source detail.
for name in cat_and_mouse cigarette eiffel life satellite; do
    python3 record_gif.py "$name.py" --offline --seconds 30 --fps 15 \
        --width 80 --height 25 --cell-width 16 --cell-height 32 \
        --output "gifs/$name.gif"
done

for name in donut globe monkey star; do
    python3 record_gif.py "$name.py" --offline --seconds 30 --fps 15 \
        --width 100 --height 32 --cell-width 13 --cell-height 25 \
        --output "gifs/$name.gif"
done
