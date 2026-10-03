import modules3
from modules3 import seatable
from modules3 import loading
from modules3 import imageToPdf
from modules3 import telegram
import os

def seconds_to_h_mm(seconds):
    try:
        if not seconds:
             return ""
        val = int(seconds)
        hours = val // 3600
        minutes = (val % 3600) // 60
        return f"{hours}:{minutes:02}"
    except (ValueError, TypeError):
        return ""

vbcd = r"C:\Users\TAPF\Documents\DistributionFinal\DistributionFinal"


# Skip title array
# Convert each item into string for Pillow Draw Text Function to Work:
# ChatGpt: string_array = [str(item) for item in array]

Date= seatable.dateOfDelivery

i=1
for result in seatable.results[1:]:
	rice = [str(item) for item in result[1:7]]
	dal = [str(item) for item in result[7:14]]
	curry = [str(item) for item in result[14:-1]]
	time= result[-1]
	
	loading.function(str(result[0]),rice, dal, curry, str(i), Date,vbcd, time)
	i=i+1
	


image_folder = os.path.join(vbcd, "image") 
reports_folder = os.path.join(vbcd, "reports")

# Crucial: Make sure the 'reports' folder exists before saving to it!
if not os.path.exists(reports_folder):
    os.makedirs(reports_folder)

# Safely build the final PDF file path
output_pdf = os.path.join(reports_folder, f"{Date}_Loading_Sheet.pdf")

# Run the final functions
imageToPdf.convert_images_to_pdf(image_folder, output_pdf)
telegram.telegramBot(output_pdf)