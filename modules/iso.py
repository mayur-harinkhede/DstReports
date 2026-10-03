# TAPF Image and Top Header Tables:
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image,PageBreak, Paragraph, Frame, Spacer
from reportlab.lib.units import inch
from reportlab.lib import styles, colors
from reportlab.lib.styles import ParagraphStyle


#C is pdf canvas:
def topTable(c, Route, Date, vbcd): 
    # We can findout height and width of pdf file using below method:
    height,width=landscape(A4) 
    #width= 841.8897637795277 and height=595.2755905511812 (border values are not in this)

    #Add data from top to bottom use translate method , default it take down otherwise:
    #c.translate(-10,600)  # New (0,0) coordinate

    # Adding first data on pdf file Date:
    c.setFont("Helvetica", 10)
    c.drawString(105, -70, "Date: "+ Date)

    # Adding route name on pdf file Date:
    c.setFont("Helvetica", 10)
    # To this:
    c.drawString(275, -70, "Route: " + (Route or "Unknown"))

    # Adding customer care name on pdf file Date:
    c.setFont("Helvetica", 10)
    c.drawString(655, -70, "Customer Care: 91332 09900")

    # Adding Route Asst on pdf file Date:
    c.setFont("Helvetica", 10)
    c.drawString(455, -70, "Route Associate:")

    # Adding image file:
    image_data = os.path.join(vbcd, "modules", "tapf.png")

    tapfLogoImage =Image(image_data, width=70, height=35)  # Adjust width and height as needed
    tapfLogoImage.hAlign = 'CENTER'


    # Define table data for top TAPF table:
    DataTop=[ 
             [tapfLogoImage,'The Akshayapatra Foundation-Hyderabad \n\n       Food Delivery Report MDMML'],

            ]


    table = Table(DataTop)
    style = TableStyle([
         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  # Set text color for header row
         ('ALIGN', (1, 1), (-1, -1), 'CENTRE'),  # Align text to center
         ('VALIGN', (0, 0), (-1, 1), 'TOP'),# Vertically align text to the top
         ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Add grid lines everywhere
         ('FONTSIZE', (0, 0), (-1, -1), 8)  # Set font size to 8
         ])
    table.setStyle(style)

    # Draw table on pdf after giving style input at mention coordinate:
    a,b=table.wrapOn(c, 500, 400)  # Wrap table if it exceeds width
    table.drawOn(c, 190, -55)  # Specify starting coordinates.


    #Table for ISO Documents:
    DataTop=[ ["",""],
              ["Doc. No","TAPF/DST/03-A"],
              ["Issue Date","11-06-2018"],
              ["Issue Status","01"],
              ["Revision Date","01-01-2024"],
              ["Revision Status","02"],
              ["Page No","1 of 1"],
            ]
    #ISO---------------------------------------------------
    table2 = Table(DataTop,rowHeights=8)
    style2 = TableStyle([
         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  # Set text color for header row
         ('ALIGN', (1, 1), (-1, -1), 'CENTRE'),  # Align numbers to the right
         ('GRID', (0, 0), (-1, -2), 0.5, '#000000'),  # Add grid lines
         ('FONTSIZE', (0, 0), (-1, -1), 5),  # Set font size to 12
    ])

    table2.setStyle(style2)
    a,b=table2.wrapOn(c, 500, 400)  # Wrap table if it exceeds width
    table2.drawOn(c, 490, -65)  # Specify starting coordinates.



    # Down-Singanutes:
    c.setFont("Helvetica", 10)
    c.drawString(80, -550, "Route Associate")
    c.drawString(250, -550, "Verified By")
    c.drawString(420, -550, "Distribution HOD")
    #return c;