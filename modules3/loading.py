import os
from PIL import Image, ImageDraw, ImageFont

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
    out_path = os.path.join(vbcd, "image", f"{i}edited_loading_sheet.jpg")
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    return out_path

def get_font_size(vbcd, size):
    font_path = os.path.join(vbcd, "modules3", "ARIAL.TTF")
    return ImageFont.truetype(font_path, size)
    
# Main function to generate the edited image
def function(route, rice, dal, curry, i, Date, vbcd, time):
    image_path = os.path.join(vbcd, "modules3", "loadingSheet.jpg")
    
    image = Image.open(image_path).convert("RGB")
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

    # Save the final image
    image.save(get_output_path(vbcd, i), format="JPEG")