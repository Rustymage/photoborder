# Photo Border Thing

A small script to add a border to a jpeg or png photo.

Exif data can also be extracted and added to the border if the mood strikes.

A colour palette can be added to the border as well.

## Installation

```bash
git clone https://github.com/stevequinn/photoborder
```

```bash
cd photoborder
```

```bash
pip install -r requirements.txt
```

## Usage

```bash
usage: python main.py [-h] [-e] [-p] [-f] [-fb] [-t{s,m,l,p,i}] filename

Add a border and exif data to a jpg or png photo

positional arguments:
  filename

options:
  -h, --help              Show this help message and exit
  -e, --exif              Print photo exif data on the border
  -p, --palette           Add colour palette to the photo border
  -t, --border_type       Border Type: p for polaroid, s for small, m for medium, l for large, i for instagram (default: s)
  -f, --font              Font Typeface to use (default: Roboto-Regular.ttf)
  -fv, --fontvariant      Font style variant to use (default: 0)
  -fb, --fontbold         Bold Font Typeface to use (default: Roboto-Medium.ttf)
  -fbv, --fontboldvariant Bold Font style variant to use (default: 0)
  --include               File patterns to include (default: *.jpg *.jpeg *.png, *.JPG, *.JPEG, *.PNG)
  --exclude               File patterns to exclude (default: *_border*)

Made for fun and to solve a little problem.
```

---

> Note: This is a hacked together little script. Use at your own peril...

## macOS Quick Actions

Quick Actions allow you to add borders to images directly from Finder's right-click menu.

### Installation

1. Ensure Python dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the installation script:
   ```bash
   ./install_quick_actions.sh
   ```

3. The script will copy all Quick Action workflows to `~/Library/Services/`

### Available Quick Actions

**With EXIF Data:**
- Add Exif Border instagram
- Add Exif Border small
- Add Exif Border medium
- Add Exif Border large
- Add Exif Border polaroid

**Without EXIF Data:**
- Add White Border instagram
- Add White Border small
- Add White Border medium
- Add White Border large
- Add White Border polaroid

### Usage

1. Right-click on any image file (jpg, jpeg, png) in Finder
2. Navigate to **Quick Actions** in the context menu
3. Select your desired border option
4. The processed image will be saved in the same directory with `_border` suffix

### Compatibility

These Quick Actions are compatible with:
- macOS Sequoia (15.x) and newer
- macOS Sonoma (14.x)
- macOS Ventura (13.x)
- macOS Monterey (12.x)
- Works with both Intel and Apple Silicon Macs

The workflows automatically detect your Python installation (pyenv or system python3).

## Fonts

The repo comes with [Roboto](https://fonts.google.com/specimen/Roboto) (Regular, Medium & Bold).

```photoborder/fonts```

Should you wish to use another font you should add it to the ```fonts``` directory and use the appropriate arguments

## Testing

There are some very simple tests available in the `tests/` directory.

You can run these with:

```bash
pytest -s ./tests
```

For specific test modules just do the same for the file like so:

```bash
pytest -s ./tests/test_text.py
```

## Examples

![alt text](doc/images/20241108_20241108DSCF0043_border-p_exif_palette.jpeg)
*`> python main.py -t p -e -p image.jpeg`*

![alt text](doc/images/20241108_20241108DSCF0043_border-s_exif.jpeg)
*`> python main.py -t s -e image.jpeg`*

![alt text](doc/images/20241108_20241108DSCF0043_border-m_exif.jpeg)
*`> python main.py -t m -e image.jpeg`*

![alt text](doc/images/20241108_20241108DSCF0043_border-l_exif.jpeg)
*`> python main.py -t l -e image.jpeg`*

![alt text](doc/images/20241108_20241108DSCF0043_border-i_exif.jpeg)
*`> python main.py -t i -e image.jpeg`*
