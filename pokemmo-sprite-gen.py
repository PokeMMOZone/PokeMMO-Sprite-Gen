import os
import requests
from PIL import Image, ImageSequence, ImageDraw

# Create the root output folder if it doesn't exist
root_output_folder = "output"
os.makedirs(root_output_folder, exist_ok=True)

# Define overlay paths
overlay_paths = {
    "egg": "egg.png",
    "safari": "safari.png",
    "secret": "secret.png",
}

# Load overlays if they exist
overlays = {}
for key, path in overlay_paths.items():
    if os.path.exists(path):
        overlays[key] = Image.open(path).convert("RGBA").resize((20, 20), Image.LANCZOS)
    else:
        print(f"Warning: Overlay '{path}' not found. Skipping '{key}' variations.")

def add_red_outline(frame):
    """Add a red outline around the Pokémon in the frame."""
    frame = frame.convert("RGBA")
    width, height = frame.size

    # Create a new image to hold the red outline
    outline_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(outline_image)

    # Identify non-transparent pixels
    pixels = frame.load()
    for x in range(width):
        for y in range(height):
            if pixels[x, y][3] > 0:  # Non-transparent pixel
                # Draw a red border around the pixel
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and pixels[nx, ny][3] == 0:
                        draw.point((nx, ny), fill=(255, 0, 0, 255))  # Red color

    # Combine the red outline with the original frame
    return Image.alpha_composite(outline_image, frame)

def apply_overlays(frame, overlay_keys):
    """Apply the specified overlays to the frame."""
    frame_width, frame_height = frame.size
    positions = {
        "egg": (frame_width - overlays["egg"].size[0], 0),
        "secret": (frame_width - overlays["secret"].size[0], 0),
        "safari": (frame_width - overlays["safari"].size[0], overlays["secret"].size[1] if "secret" in overlay_keys else 0),
    }

    for key in overlay_keys:
        frame.paste(overlays[key], positions[key], overlays[key])
    return frame

def process_shiny_gif(pokemon_name, shiny_url):
    """Download a shiny gif, generate all variations, and save them in subfolders."""
    response = requests.get(shiny_url, stream=True)
    if response.status_code != 200:
        print(f"Failed to download {shiny_url} for {pokemon_name}")
        return

    # Load the shiny GIF
    shiny_gif = Image.open(response.raw)

    # Define variations and corresponding overlay keys
    variations = {
        "alpha": [],
        "alpha_egg": ["egg"],
        "alpha_safari": ["safari"],
        "alpha_secret": ["secret"],
        "alpha_secret_safari": ["secret", "safari"],
        "egg": ["egg"],
        "safari": ["safari"],
        "secret": ["secret"],
        "secret_safari": ["secret", "safari"],
    }

    # Process each variation
    for variation, overlay_keys in variations.items():
        output_folder = os.path.join(root_output_folder, variation)
        os.makedirs(output_folder, exist_ok=True)

        # Apply red outline and overlays to all frames
        frames = []
        for frame in ImageSequence.Iterator(shiny_gif):
            frame_with_outline = add_red_outline(frame)
            frame_with_overlays = apply_overlays(frame_with_outline, overlay_keys) if overlay_keys else frame_with_outline
            frames.append(frame_with_overlays)

        # Save the modified GIF
        output_path = os.path.join(output_folder, f"{pokemon_name}.gif")
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=shiny_gif.info.get("duration", 100),
            disposal=2,
            transparency=0,
        )
        print(f"Saved {variation} gif for {pokemon_name} at {output_path}")

def fetch_all_pokemon():
    """Fetch all Pokémon names from PokeAPI."""
    url = "https://pokeapi.co/api/v2/pokemon?limit=10000"  # Fetch all Pokémon
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch Pokémon list from PokeAPI.")
    data = response.json()
    return [pokemon["name"] for pokemon in data["results"]]

def get_pokemon_data(pokemon_name):
    """Fetch data for a specific Pokémon from PokeAPI."""
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data for {pokemon_name}")
        return None
    return response.json()

# Fetch all Pokémon names
pokemon_names = fetch_all_pokemon()

# Iterate over Pokémon names
for pokemon_name in pokemon_names:
    data = get_pokemon_data(pokemon_name)
    if not data:
        continue

    # Get the shiny GIF URL for Gen 5 (black-white animated front shiny)
    shiny_url = data.get("sprites", {}).get("versions", {}).get("generation-v", {}).get("black-white", {}).get("animated", {}).get("front_shiny")
    if shiny_url:
        process_shiny_gif(pokemon_name, shiny_url)
