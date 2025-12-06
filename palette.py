"""
Image colour palette functions
"""
import math
import extcolors
from PIL import Image, ImageDraw

def is_near_white(color, threshold=240):
    """
    Check if a color is near-white based on RGB values.
    
    Args:
        color: RGB tuple (r, g, b)
        threshold: RGB threshold value (default 240 - moderate filtering)
        
    Returns:
        bool: True if color is near-white
    """
    r, g, b = color[0], color[1], color[2]
    return r > threshold and g > threshold and b > threshold


def filter_near_white_colors(colors, threshold=240, min_colors=5):
    """
    Filter out near-white colors from the palette.
    
    Args:
        colors: List of (color, count) tuples from extcolors
        threshold: RGB threshold for near-white filtering (default 240)
        min_colors: Minimum number of colors to keep (default 5)
        
    Returns:
        List of filtered colors, ensuring at least min_colors are kept
    """
    # First, try to filter near-white colors
    filtered = [c for c in colors if not is_near_white(c[0], threshold)]
    
    # If we have enough colors after filtering, return them
    if len(filtered) >= min_colors:
        return filtered[:min_colors]
    
    # Otherwise, keep filtered colors and add back some original colors
    # to reach min_colors, preferring darker colors
    remaining_needed = min_colors - len(filtered)
    near_whites = [c for c in colors if is_near_white(c[0], threshold)]
    
    # Sort near-whites by average RGB (darker first)
    near_whites_sorted = sorted(near_whites, key=lambda c: sum(c[0][:3]) / 3)
    
    # Add back the darkest near-white colors to reach minimum
    filtered.extend(near_whites_sorted[:remaining_needed])
    
    return filtered[:min_colors]


def extract_colors(img, tolerance=32, filter_whites=True):
    """
    Extract dominant colors from an image.
    
    Args:
        img: PIL Image object
        tolerance: Color grouping tolerance (default 32)
        filter_whites: Whether to filter near-white colors (default True)
        
    Returns:
        List of (color, count) tuples
    """
    limit = 12  # Extract more initially to account for filtering
    colors, pixel_count = extcolors.extract_from_image(img, tolerance, limit)
    
    if filter_whites:
        colors = filter_near_white_colors(colors, threshold=240, min_colors=5)
    else:
        colors = colors[:5]  # Limit to 5 if not filtering
    
    return colors


def render_color_platte(colors, size):
    # size = 150
    columns = 6
    width = int(min(len(colors), columns) * size)
    height = int((math.floor(len(colors) / columns) + 1) * size)
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas = ImageDraw.Draw(result)
    for idx, color in enumerate(colors):
        x = int((idx % columns) * size)
        y = int(math.floor(idx / columns) * size)
        # canvas.rectangle([(x, y), (x + size - 1, y + size - 1)], fill=color[0])
        canvas.rectangle([(x, y), (x + size, y + size)], fill=color[0])
    return result


def overlay_palette(img: Image, color_palette: Image, offset):
    # nrow = 2
    # ncol = 1
    # f = plt.figure(figsize=(20, 30), facecolor='None',
    #                edgecolor='k', dpi=55, num=None)
    # gs = gridspec.GridSpec(nrow, ncol, wspace=0.0, hspace=0.0)
    # f.add_subplot(2, 1, 1)
    # plt.imshow(img, interpolation='nearest')
    # plt.axis('off')
    # f.add_subplot(1, 2, 2)
    # plt.imshow(color_palette, interpolation='nearest')
    # plt.axis('off')
    # plt.subplots_adjust(wspace=0, hspace=0, bottom=0)
    # plt.show(block=True)

    img.paste(color_palette, offset)

    return img


def load_image_color_palette(img, size, tolerance=32):
    """
    Load color palette from an image.
    
    Args:
        img: PIL Image object
        size: Size of each color square in pixels
        tolerance: Color grouping tolerance (default 32)
        
    Returns:
        PIL Image containing the color palette
    """
    colors = extract_colors(img, tolerance=tolerance, filter_whites=True)
    color_palette = render_color_platte(colors, size)
    return color_palette
