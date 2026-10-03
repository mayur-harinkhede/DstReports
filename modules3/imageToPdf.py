from PIL import Image
import os

def convert_images_to_pdf(image_folder, output_pdf_path):
    # Get all image files in the folder
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    # Sort files numerically based on prefix (e.g. '1edited_loading_sheet.jpg' -> 1)
    def get_sort_key(filename):
        try:
            prefix = filename.split('edited')[0]
            return int(prefix)
        except Exception:
            return filename
            
    image_files.sort(key=get_sort_key)

    if not image_files:
        print("No images found in the folder.")
        return

    # Open images and convert to RGB (already pre-scaled to 1000px in loading.py)
    image_list = []
    for file in image_files:
        image_path = os.path.join(image_folder, file)
        img = Image.open(image_path).convert('RGB')
        image_list.append(img)

    # Save all images into one PDF file with quality optimization
    first_image = image_list[0]
    rest_images = image_list[1:]
    first_image.save(
        output_pdf_path, 
        "PDF", 
        save_all=True, 
        append_images=rest_images,
        quality=65,
        optimize=True
    )
    
    # Explicitly close images to free memory immediately
    for img in image_list:
        try:
            img.close()
        except Exception:
            pass
            
    print(f"Compressed PDF saved to {output_pdf_path}")
