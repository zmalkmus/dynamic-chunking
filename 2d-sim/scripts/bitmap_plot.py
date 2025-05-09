import os
import re
import math
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import sys

def load_bitmap_as_array(filepath):
    with open(filepath, 'r') as f:
        data = f.read().strip()
    side = int(math.isqrt(len(data)))
    if side * side != len(data):
        raise ValueError(f"{filepath} is not a square bitmap.")
    return np.array([int(c) for c in data]).reshape((side, side))

def generate_gif_from_bitmaps(directory):
    pattern = re.compile(r"chunk_status_bitmap_diff_(\d+)\.txt")
    files = [
        (int(m.group(1)), os.path.join(directory, f))
        for f in os.listdir(directory)
        if (m := pattern.fullmatch(f))
    ]
    files.sort()

    if not files:
        raise ValueError(f"No matching files found in directory: {directory}")

    frames = []
    for timestep, filepath in files:
        bitmap_array = load_bitmap_as_array(filepath)

        # Plot using matplotlib and save to memory buffer
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(bitmap_array, cmap='Greys', interpolation='nearest')
        ax.set_title(f"Timestep {timestep}")
        ax.axis('off')

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        frames.append(Image.open(buf).convert("RGB"))
        plt.close(fig)

    frame_duration = 1000 // len(frames) * 2  # Duration in milliseconds

    output_gif = os.path.join(directory, "bitmap.gif")

    # Save to GIF
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0
    )
    print(f"Saved GIF to {output_gif}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bitmap_gif_generator.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    generate_gif_from_bitmaps(directory)
