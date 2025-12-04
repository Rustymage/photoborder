"""
Photo Exif extraction functions
"""
import subprocess
import logging
from dataclasses import dataclass
from fractions import Fraction
from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger(__name__)

def format_shutter_speed(shutter_speed: str) -> str:
    """
    Convert a decimal value to a fraction display.
    Used to display shutter speed values.
    """
    try:
        fraction = Fraction(shutter_speed).limit_denominator()
        if fraction >= 1:
            # return f"{fraction.numerator}/{fraction.denominator}"
            return f"{fraction.numerator}"
        else:
            return f"1/{int(1/float(shutter_speed))}"
    except (ValueError, ZeroDivisionError):
        return shutter_speed

def format_focal_length(focal_length: str) -> str:
    """
    Round Focal Length
    """
    try:
        focal_length_dp = focal_length[::-1].find('.') #https://docs.python.org/dev/library/stdtypes.html#str.find
        if focal_length_dp >= 2: # Checks if the focal length has 2 decimal places or greater eg 24.878mm
            return round(float(focal_length), 2)
        else:
            return round(float(focal_length)) # Rounds focal length to nearest whole number if a single decimal point is present eg 24.0mm is 24mm
    except ValueError:
        return focal_length

@dataclass
class ExifItem:
    tag: str
    data: str

    formatter = {
        'Make': 'Shot on {dataval}',
        'FocalLength': '{dataval}mm',
        'FNumber': 'f/{dataval}',
        'ISOSpeedRatings': 'ISO{dataval}',
        'ExposureTime': '{dataval} sec'
    }

    def __str__(self) -> str:
        if self.data is None or self.data == '':
            return ''
        fmt_data = str(self.data).strip()

        # Deal with any special case data formatting
        if self.tag == 'ExposureTime':
           fmt_data = format_shutter_speed(fmt_data)
        
        # Deal with any special case data formatting
        if self.tag == 'FocalLength':
           fmt_data = format_focal_length(fmt_data)

        # Apply the string template formatting defined in self.formatter
        if self.tag in self.formatter:
            return self.formatter[self.tag].format(dataval=fmt_data)

        return fmt_data


def get_film_simulation(image_path: str) -> str:
    """
    Extract Fuji film simulation mode from image using exiftool.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Film simulation name (e.g., "Reala ACE", "Nostalgic Neg") or empty string
    """
    try:
        result = subprocess.run(
            ['exiftool', '-FilmMode', '-s', '-s', '-s', image_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        film_mode = result.stdout.strip()
        return film_mode if film_mode else ''
    except FileNotFoundError:
        logger.warning('exiftool not found. Film simulation extraction requires exiftool to be installed. '
                      'Install it with: brew install exiftool (macOS) or apt-get install exiftool (Linux)')
        return ''
    except subprocess.TimeoutExpired:
        logger.warning(f'exiftool timed out while processing {image_path}')
        return ''
    except Exception as e:
        logger.debug(f'Error extracting film simulation: {e}')
        return ''


def get_exif(img: Image, image_path: str = None, include_film_sim: bool = False) -> dict:
    """Load the exif data from an image.

    Args:
        img (Image): Pillow image object.
        image_path (str, optional): Path to image file (needed for film simulation extraction)
        include_film_sim (bool): Whether to extract film simulation data (requires exiftool)

    Returns:
        dict: dictionary with exif data
    """
    exif_data = img._getexif()
    exif_dict = {
        'Make': '',
        'Model': '',
        'LensMake': '',
        'LensModel': '',
        'FNumber': '',
        'FocalLength': '',
        'ISOSpeedRatings': '',
        'ExposureTime': '',
        'FilmSimulation': ''
    }

    if exif_data:
        # Iterate through the EXIF data and store it in the dictionary
        for tag_id in exif_data:
            tag = TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)

            if isinstance(data, bytes):
                try:
                    data = data.decode()
                except UnicodeDecodeError as e:
                    # print(f'Error decoding tag {tag}', e)
                    # Expect decoding errors, ust ignore as we don't need the exif these happen on.
                    pass

            exif_dict[tag] = ExifItem(tag, data)

    # Extract film simulation if requested and path provided
    if include_film_sim and image_path:
        film_sim = get_film_simulation(image_path)
        exif_dict['FilmSimulation'] = ExifItem('FilmSimulation', film_sim)

    # Print the EXIF data dictionary
    # print(exif_dict)

    return exif_dict
