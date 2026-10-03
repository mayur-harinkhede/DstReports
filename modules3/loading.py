import os
from PIL import Image, ImageDraw, ImageFont

_font_cache = {}
_base_template = None

# Draws a single line of text
def add_text_to_image(draw, text, font, position, color=(0, 0, 0)):
    draw.text(position, text, fill=color, font=font)

# Draws a row of texts
def add_rows(draw, font, rows, start_x, y, step_x):
    x = start_x
    for text in rows:
        add_text_to_image(draw, text, font, position=(x, y))
        x += step_x

# Builds the output image path safely
def get_output_path(vbcd, i):
    return os.path.join(vbcd, "image", f"{i}edited_loading_sheet.jpg")

def get_font_size(vbcd, size):
    if size not in _font_cache:
        font_path = os.path.join(vbcd, "modules3", "ARIAL.TTF")
        _font_cache[size] = ImageFont.truetype(font_path, size)
    return _font_cache[size]
    
# Main function to generate the edited image
def function(route, rice, dal, curry, i, Date, vbcd, time):
    global _base_template
    image_path = os.path.join(vbcd, "modules3", "loadingSheet.jpg")
    
    if _base_template is None:
        with Image.open(image_path) as img:
            _base_template = img.convert("RGB")
            
    image = _base_template.copy()
    draw = ImageDraw.Draw(image)

    font2 = get_font_size(vbcd, 40)
    font = get_font_size(vbcd, 60)

    # Add single lines of custom text
    add_text_to_image(draw, route, font2, position=(2040, 785))
    add_text_to_image(draw, Date, font2, position=(340, 785))
    add_text_to_image(draw, (time or "") + "am", font, position=(980, 1825))

    # Add the rows of text
    add_rows(draw, font, rice, start_x=290, y=1010, step_x=280)
    add_rows(draw, font, dal, start_x=290, y=1270, step_x=240)
    add_rows(draw, font, curry, start_x=290, y=1570, step_x=280)

    # Downscale resolution right before saving to keep memory footprint minimal and save 80% disk/I/O
    target_width = 1000
    w, h = image.size
    if w > target_width:
        new_h = int(h * (target_width / w))
        image = image.resize((target_width, new_h), Image.Resampling.BILINEAR)

    # Save the final image
    image.save(get_output_path(vbcd, i), format="JPEG", quality=75)