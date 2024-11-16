"""
Text on image functions
"""
import os
from PIL import Image, ImageDraw, ImageFont

FONTINDEX = 0

def create_font(size: int, fontname: str) -> ImageFont.FreeTypeFont:
    """Create the font object

    Args:
        size (int): Pixel size
        fontname (str): Path to the font file

    Returns:
        ImageFont.FreeTypeFont: The created font
    """
    font = ImageFont.truetype(fontname, size)
    return font

def create_bold_font(size: int, fontname: str) -> ImageFont.FreeTypeFont:
    """Create the bold font object

    Args:
        size (int): Pixel size
        fontname (str): Path to the bold font file

    Returns:
        ImageFont.FreeTypeFont: The created bold font
    """
    font = ImageFont.truetype(fontname, size, index=FONTINDEX)
    return font

def draw_text_on_image(img: Image, text: str, xy: tuple, centered: bool,
                       font: ImageFont.FreeTypeFont, fill: tuple = (100, 100, 100)) -> Image:
    """Draw text on an image

    Args:
        img (Image): The image to draw on
        text (str): The text to draw
        xy (tuple): The xy position of the starting point
        centered (bool): Center the text relative to the entire image
        font (ImageFont.FreeTypeFont): The font to use. See create_font and create_bold_font.
        fill (tuple, optional): The font color. Defaults to black (100, 100, 100).

    Returns:
        Image: The image with the text drawn on it.
        xy (tuple): The xy position of the next drawing pos
    """
    draw = ImageDraw.Draw(img)
    draw.fontmode = 'L'

    x, y = xy
    w = draw.textlength(text, font=font)

    if centered:
        x = (img.width - w) / 2

    draw.text((x, y), text, font=font, fill=fill, anchor="ls")

    next_y = y + font.size + (font.size / 2) if centered else y
    next_x = x if centered else x + w + (font.size / 2)

    return img, (next_x, next_y)

def get_optimal_font_size(text, target_height, fontname, max_font_size=100, min_font_size=1):
    """
    Calculate the optimal font size based on a target height

    Args:
        text (str): Sample text to draw
        target_height (int): The target height
        fontname (str): Path to the font file
        max_font_size (int, optional): Max font size to return. Defaults to 100.
        min_font_size (int, optional): Min font size to return. Defaults to 1.
    """
    def check_size(font_size):
        font = ImageFont.truetype(fontname, font_size)
        _, _, _, text_height = font.getbbox(text)
        return text_height <= target_height

    low, high = min_font_size, max_font_size
    while low <= high:
        mid = (low + high) // 2
        if check_size(mid):
            low = mid + 1
        else:
            high = mid - 1

    return high