"""
Image border functions and classes
"""
import math
from enum import Enum
from dataclasses import dataclass
from PIL import Image
import text as tm

class BorderType(Enum):
    POLAROID = 'p'
    SMALL = 's'
    MEDIUM = 'm'
    LARGE = 'l'
    INSTAGRAM = 'i'

    def __str__(self):
        return self.value

@dataclass
class Border:
    top: int
    right: int
    bottom: int
    left: int
    border_type: BorderType

def get_border_size(img_width: int, img_height: int, reduceby: int=4) -> int:
    """Calculate an image border size based on the golden ratio.

    Args:
        img_width (number): Source image width
        img_height (number): Source image height
        reduceby (int): Reduce the border by a factor of this

    Returns:
        int: The border size
    """
    # Use golden ratio to determine border size from image size.
    golden_ratio = (1 + 5 ** 0.5) / 2
    img_area = img_width * img_height
    canvas_area = img_area * golden_ratio
    border_size = math.ceil(math.sqrt(canvas_area - img_area) / reduceby)

    return border_size

def calculate_ratio_border(width, height, min_border=0, target_ratio=4/5) -> tuple[int, int]:
    """
    Given an image width and height, and a target_ratio, calculate the horizontal and vertical border pixel
    sizes needed to meet the target ratio.

    This is useful for matching 4/5 image ratios for instagram and the like.

    Args:
        width (int): The image width
        height (int): The image height
        min_border (int, optional): The minimum border to add to all sides. Defaults to 0.
        target_ratio (float, optional): The image ratio to match. Defaults to 4/5.

    Returns:
        tuple[int, int]: horizontal border pixels, vertical border pixels
    """
    current_ratio = width / height

    if current_ratio > target_ratio:
        # Image is too wide, add vertical borders
        new_height = max(height, math.ceil(width / target_ratio))
        vertical_border = max((new_height - height) // 2, min_border)
        horizontal_border = min_border
    else:
        # Image is too tall, add horizontal borders
        new_width = max(width, math.ceil(height * target_ratio))
        horizontal_border = max((new_width - width) // 2, min_border)
        vertical_border = min_border

    # Adjust to ensure the final image meets the target ratio
    final_width = width + 2 * horizontal_border
    final_height = height + 2 * vertical_border
    final_ratio = final_width / final_height

    if final_ratio > target_ratio:
        additional_vertical = math.ceil(final_width / target_ratio) - final_height
        vertical_border += additional_vertical // 2
    elif final_ratio < target_ratio:
        additional_horizontal = math.ceil(final_height * target_ratio) - final_width
        horizontal_border += additional_horizontal // 2

    return horizontal_border, vertical_border

def create_border(imgw: int, imgh: int, border_type: Border) -> Border:
    # top, right, bottom, left
    reduceby_map = {
        BorderType.POLAROID: (32, 32, 6, 32),
        BorderType.SMALL: (32, 32, 32, 32),
        BorderType.MEDIUM: (16, 16, 16, 16),
        BorderType.LARGE: (6, 6, 6, 6),
        BorderType.INSTAGRAM: (32, 32, 32, 32)
    }
    rtop, rright, rbottom, rleft = reduceby_map[border_type]
    btop = get_border_size(imgw, imgh, rtop)
    bright = get_border_size(imgw, imgh, rright)
    bbottom = get_border_size(imgw, imgh, rbottom)
    bleft = get_border_size(imgw, imgh, rleft)

    if border_type == BorderType.INSTAGRAM:
        # In the case of instagram, we want to enforce an image ratio of 4/5 with a minimum border so the
        # non-padded sides also have a border.
        ratio_border_horizonal, ratio_border_vertical = calculate_ratio_border(imgw, imgh, min_border=btop)
        btop = ratio_border_vertical
        bright = ratio_border_horizonal
        bbottom = ratio_border_vertical
        bleft = ratio_border_horizonal

    border = Border(btop, bright, bbottom, bleft, border_type)

    return border

def draw_border(img: Image, border: Border) -> Image:
    w = img.width + border.left + border.right
    h = img.height + border.top + border.bottom
    canvas = Image.new("RGB", (w, h), (255, 255, 255, 0))
    canvas.paste(img, (border.left, border.top))

    return canvas

def draw_exif(img: Image, exif: dict, border: Border, font: tuple[str, int], boldfont: tuple[str, int], oneline: bool = False, has_palette: bool = False) -> Image:
    centered = border.border_type in (BorderType.POLAROID, BorderType.LARGE, BorderType.INSTAGRAM)
    
    # If oneline flag is set, force single-line layout for centered border types
    if oneline and centered:
        centered = False
    
    if centered:
        # For polaroid, large, and instagram: 3 lines of text, centered, stacked vertically
        # Increased multiplier from 0.2 to 0.28 for larger, more readable text
        multiplier = 0.28
        font_size = tm.get_optimal_font_size("Test", border.bottom * multiplier, font[0], index=font[1])
        heading_font_size = tm.get_optimal_font_size("Test", border.bottom * (multiplier + 0.04), boldfont[0], index=boldfont[1])
        font_obj = tm.create_font(font_size, fontpath=font[0], index=font[1])
        heading_font = tm.create_font(heading_font_size, fontpath=boldfont[0], index=boldfont[1])

        # 3 Lines of text. 1 heading, two normal. Minus heading margins. A bit sketchy but it aligns fine.
        total_font_height = heading_font.size + (2 * font_obj.size) - (heading_font.size / 2)
        y = img.height - border.bottom + \
            (border.bottom / 2) - (total_font_height / 2)
        x = border.left

        text = f"{exif['Make']} {exif['Model']}"
        text_img, (x, y) = tm.draw_text_on_image(img, text, (x,y), centered, heading_font, fill=(100, 100, 100))

        text = f"{exif['LensMake']} {exif['LensModel']}"
        text_img, (x, y) = tm.draw_text_on_image(text_img, text, (x,y), centered, font_obj, fill=(128, 128, 128))

        # Build settings line with optional film simulation
        settings_parts = [
            str(exif['FocalLength']),
            str(exif['FNumber']),
            str(exif['ISOSpeedRatings']),
            str(exif['ExposureTime'])
        ]
        
        # Join settings with dots
        text = " · ".join(settings_parts)
        
        # Add film simulation if available (with pipe separator)
        film_sim = str(exif.get('FilmSimulation', ''))
        if film_sim:
            text = f"{text}  | {film_sim}"
        text_img, (x, y) = tm.draw_text_on_image(text_img, text, (x,y), centered, font_obj, fill=(128, 128, 128))
    else:
        # For small and medium: Single line of text at bottom, centered horizontally
        # Increased multiplier from 0.2 to 0.32 for larger, more readable single-line text
        # (0.4 was too large and caused text cutoff on small borders)
        multiplier = 0.32
        font_size = tm.get_optimal_font_size("Test", border.bottom * multiplier, font[0], index=font[1])
        heading_font_size = tm.get_optimal_font_size("Test", border.bottom * (multiplier + 0.04), boldfont[0], index=boldfont[1])
        font_obj = tm.create_font(font_size, fontpath=font[0], index=font[1])
        heading_font = tm.create_font(heading_font_size, fontpath=boldfont[0], index=boldfont[1])
        
        # Build the single line with mixed fonts: we'll draw bold camera, then regular rest
        camera_text = f"{exif['Make']} {exif['Model']}"
        lens_text = f"{exif['LensMake']} {exif['LensModel']}"
        
        # Build settings text with optional film simulation
        settings_parts = [
            str(exif['FocalLength']),
            str(exif['FNumber']),
            str(exif['ISOSpeedRatings']),
            str(exif['ExposureTime'])
        ]
        
        # Join settings with dots
        settings_text = " · ".join(settings_parts)
        
        # Add film simulation if available (with pipe separator)
        film_sim = str(exif.get('FilmSimulation', ''))
        if film_sim:
            settings_text = f"{settings_text}  | {film_sim}"
        
        # Calculate total width for centering (using heading font for camera, regular for rest)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        camera_width = draw.textlength(camera_text, font=heading_font)
        separator_width = draw.textlength(" · ", font=font_obj)
        lens_width = draw.textlength(lens_text, font=font_obj)
        settings_width = draw.textlength(settings_text, font=font_obj)
        total_width = camera_width + separator_width + lens_width + separator_width + settings_width
        
        # If palette is present, adjust text position to leave room on the right
        # Palette width is approximately border.bottom / 3 * number_of_colors (up to 5 colors)
        # We'll reserve space for the palette on the right side
        if has_palette:
            palette_reserved_width = border.bottom  # Approximate palette width plus padding
            available_width = img.width - palette_reserved_width - border.left
            x = border.left + (available_width - total_width) / 2
        else:
            # Center the text block horizontally
            x = (img.width - total_width) / 2
        
        # Center vertically in bottom border using actual text bounding box for precise centering
        # Get the bounding box of the heading font (tallest text in the line)
        bbox = heading_font.getbbox(camera_text)
        text_height = bbox[3] - bbox[1]  # bottom - top gives actual rendered height
        # Position Y so the text is perfectly centered in the bottom border
        # Note: anchor is "ls" (left-baseline), so we need to account for the baseline position
        y = img.height - border.bottom + (border.bottom / 2) - (text_height / 2) + bbox[3]
        
        # Draw camera (bold)
        text_img, (x, _) = tm.draw_text_on_image(img, camera_text, (x, y), centered=False, font=heading_font, fill=(100, 100, 100))
        
        # Draw first separator
        text_img, (x, _) = tm.draw_text_on_image(text_img, " · ", (x, y), centered=False, font=font_obj, fill=(128, 128, 128))
        
        # Draw lens
        text_img, (x, _) = tm.draw_text_on_image(text_img, lens_text, (x, y), centered=False, font=font_obj, fill=(128, 128, 128))
        
        # Draw second separator
        text_img, (x, _) = tm.draw_text_on_image(text_img, " · ", (x, y), centered=False, font=font_obj, fill=(128, 128, 128))
        
        # Draw settings
        text_img, (x, _) = tm.draw_text_on_image(text_img, settings_text, (x, y), centered=False, font=font_obj, fill=(128, 128, 128))

    return text_img
