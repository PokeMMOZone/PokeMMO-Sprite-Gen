# PokeMMO-Sprite-Gen

A Python script to generate Pokémon sprites with various modifications for use on forums, websites, or other platforms. The script downloads shiny animated sprites from the PokeAPI, processes them, and generates different versions of the sprites based on user-defined configurations.

## Requirements

- Python 3.6 or higher
- Required Python packages (see `requirements.txt`):
  ```
  Pillow
  requests
  ```

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Usage

### Run the Script

```bash
python pokemmo-sprite-gen.py
```

### Output

The script generates the following variations of sprites in the `output/` directory:

1. **Alpha Versions**:
   - `alpha`: Yellow outline only.
   - `alpha_egg`: Yellow outline + `egg.png`.
   - `alpha_safari`: Yellow outline + `safari.png`.
   - `alpha_secret`: Yellow outline + `secret.png`.
   - `alpha_secret_safari`: Yellow outline + `secret.png` and `safari.png`.

2. **Overlay-Only Versions**:
   - `egg`: Only `egg.png` as overlay.
   - `safari`: Only `safari.png` as overlay.
   - `secret`: Only `secret.png` as overlay.
   - `secret_safari`: Both `secret.png` and `safari.png` as overlays.

3. **Black-Out Versions**:
   - `black`: Animated GIF with all non-transparent pixels turned black.
   - `black_PNG`: Static PNG of the first frame from the blacked-out version.

4. **Greyscale Versions**:
   - `greyscale`: Animated GIF with all frames converted to greyscale.
   - `greyscale_PNG`: Static PNG of the first frame from the greyscale version.

## How It Works

1. Fetches a list of all Pokémon from the PokeAPI.
2. Downloads shiny animated sprites for Gen 5 Pokémon (if available).
3. Processes each sprite to generate:
   - Yellow-outlined versions.
   - Overlayed versions.
   - Blacked-out versions.
   - Greyscale versions.
4. Saves each variation in its corresponding subfolder under `output/`.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature/bug fix.
3. Commit your changes and push the branch.
4. Submit a pull request.

## License

This project is licensed under the terms of the GNU General Public License v2.0 (GPLv2). You are free to use, modify, and distribute this software under the terms of this license. See the `LICENSE.md` file for details.
