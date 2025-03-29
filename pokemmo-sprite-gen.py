import os
import requests
from PIL import Image, ImageSequence, ImageDraw, ImageEnhance

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

def add_yellow_outline(frame):
    """Add a yellow outline around the Pokémon in the frame."""
    frame = frame.convert("RGBA")
    width, height = frame.size

    # Create a new image to hold the yellow outline
    outline_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(outline_image)

    # Identify non-transparent pixels
    pixels = frame.load()
    for x in range(width):
        for y in range(height):
            if pixels[x, y][3] > 0:  # Non-transparent pixel
                # Draw a yellow border around the pixel
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and pixels[nx, ny][3] == 0:
                        draw.point((nx, ny), fill=(255, 255, 0, 255))  # Yellow color

    # Combine the yellow outline with the original frame
    return Image.alpha_composite(outline_image, frame)

def apply_overlays_behind(frame, overlay_keys):
    """Place the specified overlays behind the Pokémon sprite."""
    frame = frame.convert("RGBA")
    width, height = frame.size
    background = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    for key in overlay_keys:
        overlay = overlays[key]
        position = {
            "egg": (width - overlay.size[0], 0),
            "secret": (width - overlay.size[0], 0),
            "safari": (width - overlay.size[0], overlays["secret"].size[1] if "secret" in overlay_keys else 0),
        }[key]
        background.paste(overlay, position, overlay)

    # Combine the background with the frame
    combined = Image.alpha_composite(background, frame)
    return combined

def generate_black_versions(pokemon_name, shiny_gif):
    """Generate blacked-out versions (animated GIF and first-frame PNG)."""
    black_folder = os.path.join(root_output_folder, "black")
    black_png_folder = os.path.join(root_output_folder, "black_PNG")
    os.makedirs(black_folder, exist_ok=True)
    os.makedirs(black_png_folder, exist_ok=True)

    # Create blacked-out frames
    frames = []
    for frame in ImageSequence.Iterator(shiny_gif):
        frame = frame.convert("RGBA")
        black_frame = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        pixels = frame.load()
        black_pixels = black_frame.load()

        for x in range(frame.width):
            for y in range(frame.height):
                if pixels[x, y][3] > 0:  # Non-transparent pixel
                    black_pixels[x, y] = (0, 0, 0, pixels[x, y][3])  # Black color, preserve transparency

        frames.append(black_frame)

    # Save animated blacked-out GIF
    gif_output_path = os.path.join(black_folder, f"{pokemon_name}.gif")
    frames[0].save(
        gif_output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=shiny_gif.info.get("duration", 100),
        disposal=2,
    )

    # Save first frame as static PNG
    png_output_path = os.path.join(black_png_folder, f"{pokemon_name}.png")
    frames[0].save(png_output_path)
    print(f"Saved blacked-out GIF and PNG for {pokemon_name} at {black_folder} and {black_png_folder}")

def generate_greyscale_versions(pokemon_name, shiny_gif):
    """Generate greyscale versions (animated GIF and first-frame PNG)."""
    greyscale_folder = os.path.join(root_output_folder, "greyscale")
    greyscale_png_folder = os.path.join(root_output_folder, "greyscale_PNG")
    os.makedirs(greyscale_folder, exist_ok=True)
    os.makedirs(greyscale_png_folder, exist_ok=True)

    # Create greyscale frames
    frames = []
    for frame in ImageSequence.Iterator(shiny_gif):
        frame = frame.convert("RGBA")
        greyscale_frame = ImageEnhance.Color(frame).enhance(0)  # Convert to greyscale
        frames.append(greyscale_frame)

    # Save animated greyscale GIF
    gif_output_path = os.path.join(greyscale_folder, f"{pokemon_name}.gif")
    frames[0].save(
        gif_output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=shiny_gif.info.get("duration", 100),
        disposal=2,
    )

    # Save first frame as static PNG
    png_output_path = os.path.join(greyscale_png_folder, f"{pokemon_name}.png")
    frames[0].save(png_output_path)
    print(f"Saved greyscale GIF and PNG for {pokemon_name} at {greyscale_folder} and {greyscale_png_folder}")

def process_shiny_gif(pokemon_name, shiny_url):
    """Download a shiny gif, generate all variations, and save them in subfolders."""
    response = requests.get(shiny_url, stream=True)
    if response.status_code != 200:
        print(f"Failed to download {shiny_url} for {pokemon_name}")
        return

    # Load the shiny GIF
    shiny_gif = Image.open(response.raw)

    # Generate blacked-out versions
    generate_black_versions(pokemon_name, shiny_gif)

    # Generate greyscale versions
    generate_greyscale_versions(pokemon_name, shiny_gif)

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

        # Apply yellow outline and overlays to all frames
        frames = []
        for frame in ImageSequence.Iterator(shiny_gif):
            frame_with_outline = add_yellow_outline(frame)
            frame_with_overlays = apply_overlays_behind(frame_with_outline, overlay_keys) if overlay_keys else frame_with_outline
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
        print(f"Saved {variation} gif for {pokemon_name} at {output_folder}")

def build_shiny_url_female(base_id):
    """Construct the animated shiny URL for a female sprite using the Pokémon ID."""
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/shiny/female/{base_id}.gif"

def build_form_shiny_url_female(filename_id):
    """Construct the animated shiny URL for a female form."""
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/shiny/female/{filename_id}.gif"

def process_shiny_gif_female(pokemon_name, shiny_url):
    """Same as process_shiny_gif but places results into _female folders."""
    response = requests.get(shiny_url, stream=True)
    if response.status_code != 200:
        print(f"Failed to download {shiny_url} for {pokemon_name} (female)")
        return
    shiny_gif = Image.open(response.raw)
    generate_black_versions(pokemon_name, shiny_gif)
    generate_greyscale_versions(pokemon_name, shiny_gif)
    variations = {
        "alpha_female": [],
        "alpha_egg_female": ["egg"],
        "alpha_safari_female": ["safari"],
        "alpha_secret_female": ["secret"],
        "alpha_secret_safari_female": ["secret", "safari"],
        "egg_female": ["egg"],
        "safari_female": ["safari"],
        "secret_female": ["secret"],
        "secret_safari_female": ["secret", "safari"],
    }
    for variation, overlay_keys in variations.items():
        output_folder = os.path.join(root_output_folder, variation)
        os.makedirs(output_folder, exist_ok=True)
        frames = []
        for frame in ImageSequence.Iterator(shiny_gif):
            frame_with_outline = add_yellow_outline(frame)
            frame_with_overlays = apply_overlays_behind(frame_with_outline, overlay_keys) if overlay_keys else frame_with_outline
            frames.append(frame_with_overlays)
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
        print(f"Saved {variation} gif for {pokemon_name} (female) at {output_folder}")

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

EXCLUDED_VARIATION_PATTERNS = [
    "-mega",
    "-gmax",
    "-alola",
    "-hisui",
    "-galar",
    "-rock-star",
    "-belle",
    "-pop-star",
    "-phd",
    "-libre",
    "-cosplay",
    "-original-cap",
    "-hoenn-cap",
    "-sinnoh-cap",
    "-unova-cap",
    "-kalos-cap",
    "-partner-cap",
    "-starter",
    "-world-cap",
    "-primal",
    "-paldea",
    "-totem",
    "palkia-origin",
    "dialga-origin",
    "basculin-white-striped",
    "unown-a",
    "arceus-normal",
    "arceus-unknown",
    "arceus-fairy",
    "mothim-plant",
    "pichu-spiky-eared",
    "burmy-plant",
    "cherrim-overcast",
    "shellos-west",
    "gastrodon-west",
    "deerling-spring",
    "sawsbuck-spring",
]

def build_form_filename_id(base_id, form_name):
    """Infer a filename ID based on the parent ID and form name."""
    filename_id = str(base_id)
    if "-" in form_name:
        letter_part = form_name.split("-", 1)[1]
        filename_id = f"{filename_id}-{letter_part}"
    return filename_id

def build_form_shiny_url(filename_id):
    """Construct the animated shiny URL for a form using the inferred filename ID."""
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/shiny/{filename_id}.gif"

def get_form_data(form_name):
    """Fetch data for a specific form from PokeAPI."""
    url = f"https://pokeapi.co/api/v2/pokemon-form/{form_name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Failed to fetch form data for {form_name}: {e}")
    return None

def get_pokemon_forms(pokemon_data):
    """Return form data by inferring the shiny URL from the parent ID and form name."""
    forms = []
    base_id = pokemon_data["id"]  # Parent Pokémon ID
    for form in pokemon_data.get("forms", []):
        form_name = form["name"]
        if any(pattern in form_name for pattern in EXCLUDED_VARIATION_PATTERNS):
            continue
        filename_id = build_form_filename_id(base_id, form_name)
        front_shiny = build_form_shiny_url(filename_id)
        forms.append((form_name, front_shiny))
    return forms

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
        female_url = build_shiny_url_female(data["id"])
        process_shiny_gif_female(pokemon_name, female_url)

    # Now also process forms
    forms = get_pokemon_forms(data)
    for form_name, form_shiny_url in forms:
        process_shiny_gif(form_name, form_shiny_url)
        filename_id = build_form_filename_id(data["id"], form_name)
        form_shiny_url_female = build_form_shiny_url_female(filename_id)
        process_shiny_gif_female(form_name, form_shiny_url_female)
