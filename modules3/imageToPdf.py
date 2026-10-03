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

    # Open images, resize to a friendly width, and convert to RGB
    image_list = []
    target_width = 1000  # Downscales resolution for PDF compilation (saves 95% space but keeps exact format)
    
    for file in image_files:
        image_path = os.path.join(image_folder, file)
        img = Image.open(image_path)
        
        # Calculate aspect-ratio scale
        w, h = img.size
        if w > target_width:
            new_h = int(h * (target_width / w))
            img = img.resize((target_width, new_h), Image.Resampling.LANCZOS)
            
        img = img.convert('RGB')
        image_list.append(img)

    # Save all images into one PDF file with quality optimization
    first_image = image_list[0]
    rest_images = image_list[1:]
    first_image.save(
        output_pdf_path, 
        "PDF", 
        save_all=True, 
        append_images=rest_images,
        quality=60,          # JPEG quality compression
        optimize=True        # Optimize file size
    )
    print(f"Compressed PDF saved to {output_pdf_path}")
