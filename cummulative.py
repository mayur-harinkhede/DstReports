# TAPF Image and Top Header Tables:
import os # ✅ Added for safe file paths!
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image,PageBreak, Paragraph, Frame, Spacer
from reportlab.lib.units import inch
from reportlab.lib import styles, colors
from reportlab.lib.styles import ParagraphStyle

import modules2
from modules2 import seatable
from modules2 import iso
from modules2 import cummulative
from modules2 import telegram

vbcd = r"C:\Users\TAPF\Documents\DistributionFinal\DistributionFinal"

# Define Variables:
Date = "Date: " + seatable.dateOfDelivery

# ✅ FIX: Safely build the path to the reports folder
reports_folder = os.path.join(vbcd, "reports")

# ✅ FIX: Make sure the folder exists before trying to save!
if not os.path.exists(reports_folder):
    os.makedirs(reports_folder)

# ✅ FIX: Safely build the final PDF file name
pdf_filename = os.path.join(reports_folder, f"{seatable.dateOfDelivery}_Cummulative Sheet.pdf")

# Create new pdf canvas file using canvas method and define size of pdf:
pdf = canvas.Canvas(pdf_filename, pagesize=landscape(A4))

# 1) Create Data table and top table and recollect updated pdf:
pdf = cummulative.function(pdf, seatable.result, iso, seatable.row, Date, seatable.menu, vbcd, seatable.curryRatio)

pdf.save()
print(f"Hare Krishna!!! Created:  {pdf_filename}")

telegram.telegramBot(pdf_filename)