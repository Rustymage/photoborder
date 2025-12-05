"""
 Add a border to the image named in the first parameter.
 A new image with {filename}_bordered will be generated.
 TODO: Read up on sorting images by appearance https://github.com/Visual-Computing/LAS_FLAS/blob/main/README.md
 """

import os
import argparse
import logging
from PIL import Image, ImageOps
from exif import get_exif
from filemanager import should_include_file, get_directory_files
from palette import load_image_color_palette, overlay_palette
from border import BorderType, create_border, draw_border, draw_exif, get_film_simulation_image
from text import validate_font

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='python border.py',
        description='Add a border and exif data to jpg or png photos',
        epilog='Made for fun and to solve a little problem.'
    )
    parser.add_argument('path',
                        help='File or directory path')
    parser.add_argument('-e', '--exif', action='store_true', default=False,
                        help='Print photo exif data on the border')
    parser.add_argument('-p', '--palette', action='store_true', default=False,
                        help='Add colour palette to the photo border')
    parser.add_argument('-t', '--border_type', type=BorderType, choices=list(BorderType), default=BorderType.SMALL,
                        help='Border Type: p for polaroid, s for small, m for medium, l for large, i for instagram')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Process directories recursively')
    parser.add_argument('--include', nargs='+', default=['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'],
                        help='File patterns to include (default: *.jpg *.jpeg *.png, *.JPG, *.JPEG, *.PNG')
    parser.add_argument('--exclude', nargs='+', default=["*_border*"],
                        help='File patterns to exclude (default: *_border*)')
    parser.add_argument('-f', '--font', default='Roboto-Regular.ttf',
                        help='Font file in fonts directory')
    parser.add_argument('-fv', '--fontvariant', default=0, type=int,
                        help='Font style variant index')
    parser.add_argument('-fb', '--fontbold', default='Roboto-Medium.ttf',
                        help='Bold font file in fonts directory')
    parser.add_argument('-fbv', '--fontboldvariant', default=0, type=int,
                        help='Bold font style variant index')
    parser.add_argument('--oneline', action='store_true', default=False,
                        help='Use single-line text layout for large, polaroid, and instagram borders')
    parser.add_argument('--twoline', action='store_true', default=False,
                        help='Use two-line left-aligned layout for large, polaroid, and instagram borders')
    parser.add_argument('-s', action='store_true', default=False,
                        help='Include Fuji film simulation in EXIF data (requires exiftool)')
    parser.add_argument('--filmsim-scale', type=float, default=0.5,
                        help='Scale factor for film-sim image relative to bottom border height (default: 0.9)')
    return parser.parse_args()


def process_image(path: str, add_exif: bool, add_palette: bool, border_type: BorderType,
                  font: tuple[str, int], boldfont: tuple[str, int], oneline: bool = False, 
                  twoline: bool = False, include_film_sim: bool = False, film_sim_scale: float = 0.5) -> str:
    """ Add a border to an image
    Supported image types ['jpg', 'jpeg', 'png'].

    Args:
        path (str): The image file path
        add_exif (bool): Add photo exif information to the border
        add_palette (bool): Add colour palette information to the border.
                            Currently only supported on Polaroid border types.
        border_type (BorderType): The type of border to add to the photo.
        font: tuple[str, int]: (fontName, fontVariantIndex)
        boldfont: tuple[str, int]: (fontName, fontVariantIndex)
        oneline: bool: Use single-line text layout for large/polaroid/instagram borders
        twoline: bool: Use two-line left-aligned layout for large/polaroid/instagram borders
        include_film_sim: bool: Include Fuji film simulation data (requires exiftool)
        film_sim_scale: float: Scale factor for the film-sim image relative to the bottom border height.
    """
    filetypes = ['jpg', 'jpeg', 'png']
    path_dot_parts = path.split('.')
    ext = path_dot_parts[-1:][0]
    filename = ".".join(path_dot_parts[:-1])

    if not ext or ext.lower() not in filetypes:
        logger.error(f'Image must be one of {filetypes}')
        return

    exif = None
    img = Image.open(path)
    
    # Extract EXIF data before transposing (transpose creates a new image without _getexif method)
    if add_exif:
        exif = get_exif(img, image_path=path, include_film_sim=include_film_sim)
    
    # Apply EXIF orientation to ensure portrait images are correctly oriented
    img = ImageOps.exif_transpose(img)
    border = create_border(img.width, img.height, border_type)
    img_with_border = draw_border(img, border)
    save_as = f'{filename}_border-{border.border_type}'

    # Precompute film-sim image sizing and position so palette placement can avoid overlap.
    film_img = None
    film_w = film_h = film_x = None
    if include_film_sim and exif:
        film_sim = str(exif.get('FilmSimulation', ''))
        if film_sim:
            film_img = get_film_simulation_image(film_sim)
            if film_img:
                # compute target dimensions (do not resize yet)
                film_target_h = max(1, round(border.bottom * film_sim_scale))
                orig_w, orig_h = film_img.size
                film_w = max(1, int(orig_w * (film_target_h / orig_h)))
                film_h = film_target_h
                # right-edge alignment coordinate for the film image (relative to canvas)
                photo_right = border.left + img.width
                film_x = photo_right - film_w

    if add_exif:
        if exif:
            moduledir = os.path.dirname(os.path.abspath(__file__))
            fontdir = os.path.join(moduledir, "fonts")
            font_path = os.path.join(fontdir, font[0])
            bold_font_path = os.path.join(fontdir, boldfont[0])

            # Exit early if a problem exists with the fonts
            error_messages = [err for f in [(font_path, font[1]), (bold_font_path, boldfont[1])]
                              if (err := validate_font(fontpath=f[0], index=f[1]))]
            if len(error_messages) > 0:
                raise ValueError(error_messages)

            # We'll compute film image usage below and pass that into draw_exif
            # (film image sizing/position will be precomputed just after this block)
            use_film_image = True if (film_img and include_film_sim) else False
            img_with_border = draw_exif(img_with_border, exif, border, (font_path, font[1]), (bold_font_path, boldfont[1]), oneline, twoline, add_palette, use_film_image)
            save_as = f'{save_as}_exif'

    if add_palette:
        palette_size = round(border.bottom / 3)
        color_palette = load_image_color_palette(img, palette_size)
        # Position palette on right side of bottom border
        palette_x = img_with_border.width - border.right - color_palette.width
        # For twoline layout, align top edge with breathing room from photo edge
        if twoline:
            breathing_room = max(16, int(border.bottom * 0.20))
            palette_y = img_with_border.height - border.bottom + breathing_room
        else:
            # Default: center in bottom border
            palette_y = img_with_border.height - round(border.bottom / 2) - round(color_palette.height / 2)
        # Shift palette to the left of the film-sim image (if present) or align to photo right edge
        padding = max(4, round(border.bottom * 0.12))
        photo_right = border.left + img.width
        if film_img and film_x is not None:
            # place palette so its right edge is film_x - padding
            desired_palette_x = film_x - padding - color_palette.width
        else:
            # align palette right edge with photo right edge
            desired_palette_x = photo_right - color_palette.width
        # Cap desired position so palette stays inside the image canvas and not negative
        max_palette_x = img_with_border.width - color_palette.width
        palette_x = min(max(desired_palette_x, 0), max_palette_x)
        img_with_border = overlay_palette(img=img_with_border,
                                          color_palette=color_palette,
                                          offset=(palette_x, palette_y))
        save_as = f'{save_as}_palette'

    # Paste film-sim image inline with the palette area (or at the right if no palette)
    if include_film_sim and exif and film_img:
        # use precomputed film_w, film_h, film_x
        resized = film_img.resize((film_w, film_h), resample=Image.LANCZOS)

        # Vertical placement
        if twoline:
            # For twoline layout, align film sim top edge with visual top of first text line
            # Text is drawn with anchor "ls" (left-baseline), so baseline is at y_start
            # The visual top of text is approximately baseline - 0.75 * font_size
            breathing_room = max(16, int(border.bottom * 0.20))
            text_baseline_y = img_with_border.height - border.bottom + breathing_room
            # Estimate font size as a fraction of border (using same logic as in border.py)
            multiplier = 0.20
            estimated_heading_font_size = int(border.bottom * (multiplier + 0.04))
            max_font_from_border = int(border.bottom * 0.18)
            estimated_heading_font_size = min(estimated_heading_font_size, max_font_from_border)
            # Visual top of text is approximately baseline - 0.75 * font_size
            visual_text_top = text_baseline_y - int(estimated_heading_font_size * 0.75)
            film_y = visual_text_top
        elif add_palette and 'color_palette' in locals():
            # Align with palette vertically if present
            film_y = palette_y + (color_palette.height - film_h) // 2
        else:
            # Default: center in bottom border
            film_y = img_with_border.height - round(border.bottom / 2) - round(film_h / 2)

        try:
            img_with_border.paste(resized, (int(film_x), int(film_y)), resized)
        except Exception:
            img_with_border.paste(resized, (int(film_x), int(film_y)))

    # There are two parts to JPEG quality. The first is the quality setting.
    #
    # JPEG also uses chroma subsampling, assuming that color hue changes are
    # less important than lightness changes and some information can be safely
    # thrown away. Unfortunately in demanding applications this isn't always true,
    # and you can most easily notice this on red edges. PIL didn't originally expose
    # a documented setting to control this aspect.
    #
    # Pascal Beyeler discovered the option which disables chroma subsampling. You can set
    # subsampling=0 when saving an image and the image looks way sharper!
    #
    # Note also that the documentation claims quality=95 is the best quality setting and
    # that anything over 95 should be avoided. This may be a change from earlier versions of PIL.
    #
    # ref: https://stackoverflow.com/a/19303889
    save_path = f'{save_as}.{ext}'
    exifdata = img.getexif()  # extracts original EXIF data from Image.open(path)
    img_with_border.save(save_path, exif=exifdata, subsampling=0, quality=95)

    # Clean up
    img_with_border.close()
    img.close()

    return save_path


def main():
    args = parse_arguments()
    paths = []

    # Figure out paths to save based on include/exclude opts and allowable file types
    if os.path.isdir(args.path):
        paths = get_directory_files(args.path, args.recursive, args.include, args.exclude)
    elif os.path.isfile(args.path):
        if should_include_file(args.path, args.include, args.exclude):
            paths.append(args.path)
        else:
            logger.info(f'Skipping {args.path} as it does not match the include/exclude patterns')
    else:
        logger.error(f'{args.path} is not a valid file or directory')

    for path in paths:
        logger.info(f'Adding border to {path}')
        save_path = process_image(path=path, add_exif=args.exif, add_palette=args.palette, border_type=args.border_type,
                      font=(args.font, args.fontvariant) , boldfont=(args.fontbold, args.fontboldvariant), 
                      oneline=args.oneline, twoline=args.twoline, include_film_sim=args.s, film_sim_scale=args.filmsim_scale)
        logger.info(f'Saved as {save_path}')

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        logger.error(e)
