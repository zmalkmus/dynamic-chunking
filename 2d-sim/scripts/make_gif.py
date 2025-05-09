import os
import re
import sys
from PIL import Image

def main(image_dir):
    # Regex pattern for matching mesh_<timestep>.png
    pattern = re.compile(r"mesh_(\d+)\.png")

    # Ensure the directory exists
    if not os.path.isdir(image_dir):
        print(f"Error: Directory '{image_dir}' does not exist.")
        return

    # Collect and sort valid image filenames based on timestep
    image_files = sorted(
        (f for f in os.listdir(image_dir) if pattern.fullmatch(f)),
        key=lambda f: int(pattern.fullmatch(f).group(1))
    )

    if not image_files:
        print(f"No matching images found in '{image_dir}'.")
        return

    # Full paths to the images
    image_paths = [os.path.join(image_dir, f) for f in image_files]


    #Set frame duration based on the number of frames
    frame_duration_ms = 1000 // len(image_paths)  # 1000 ms = 1 second

    # Open images
    frames = [Image.open(path) for path in image_paths]

    output_gif = os.path.join(image_dir, "simulation.gif")

    # Save as animated GIF
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration_ms,
        loop=0
    )

    print(f"GIF saved as {output_gif}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_gif.py <image_directory>")
        sys.exit(1)
    
    image_dir = sys.argv[1]
    main(image_dir)
