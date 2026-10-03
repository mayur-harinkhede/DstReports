from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, PageBreak, Paragraph, Frame, Spacer
from reportlab.lib.units import inch
from reportlab.lib import styles, colors
from reportlab.lib.styles import ParagraphStyle

# --- The Summary Table style remains static since it doesn't change based on columns ---
style3 = TableStyle([
     ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Color header row
     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),      # Set text color for header row
     ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),              # Align numbers to the centre
     ('VALIGN', (0, 0), (-1, -1), 'TOP'),                # Vertically align text to the top
     ('ALIGN', (1, 0), (1, -1), 'LEFT'),                  # Align Items to the left
     ('GRID', (0, 0), (-1, -1), 1.0, '#000000'),         # Add grid lines
     ('FONTSIZE', (0, 0), (-1, -1), 9),                  # Set font size to 9
])


def function(pdf, result, iso2, row, Date, Menu, vbcd, curryRatio):
    pdf.translate(-10, 600)

    # Fetch the dynamically generated header row from seatable.py
    header_row = result[0]

    # --- 1. Base Styles (Always present on every report) ---
    page1 = [
        # Light blue background for the sub-headers (Row 1)
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        ('ALIGN', (0, 0), (-1, 1), 'CENTRE'),
        ('ALIGN', (1, 2), (-1, -1), 'CENTRE'),
        
        # Default thin grid for all data cells inside the table
        ('GRID', (0, 1), (-1, -1), 0.5, '#000000'),  
        
        # Span and Box for "Schools"
        ('SPAN', (2, 0), (3, 0)),   
        ('BOX', (2, 0), (3, 0), 1, '#000000'), 
        
        # Span and Box for "Attendance"
        ('SPAN', (4, 0), (7, 0)),   
        ('BOX', (4, 0), (7, 0), 1, '#000000'), 
        
        # Thick vertical dividers for the fixed columns
        ('LINEBEFORE', (2, 1), (2, -1), 1, '#000000'),   
        ('LINEBEFORE', (4, 1), (4, -1), 1, '#000000'),   
        ('LINEBEFORE', (8, 1), (8, -1), 1, '#000000'), 
        
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOX', (0, 1), (-1, -1), 1, colors.black), # Outer box for the data block
    ]

    page2 = [
        ('GRID', (0, -1), (-1, -2), 1, '#000000'),
    ]

    # --- 2. Dynamic Styles based on actual columns present ---
    # The dynamic columns (Rice, Dal, Curry) always start at index 8
    current_col = 8

    # Check if Rice is in the headers
    if Menu.get("Rice") in header_row:
        page1.append(('SPAN', (current_col, 0), (current_col + 5, 0))) # Span 6 columns
        page1.append(('BOX', (current_col, 0), (current_col + 5, 0), 1, '#000000')) # Box around Title
        page2.append(('BACKGROUND', (current_col, -1), (current_col + 5, -1), colors.yellow))
        current_col += 6
        # Thick line before the next block
        if current_col < len(header_row):
            page1.append(('LINEBEFORE', (current_col, 1), (current_col, -1), 1, '#000000'))

    # Check if Dal is in the headers
    if Menu.get("Dal") in header_row:
        page1.append(('SPAN', (current_col, 0), (current_col + 6, 0))) # Span 7 columns
        page1.append(('BOX', (current_col, 0), (current_col + 6, 0), 1, '#000000')) # Box around Title
        page2.append(('BACKGROUND', (current_col, -1), (current_col + 6, -1), colors.lightblue))
        current_col += 7
        if current_col < len(header_row):
            page1.append(('LINEBEFORE', (current_col, 1), (current_col, -1), 1, '#000000'))

    # Check if Curry is in the headers
    if Menu.get("Curry") in header_row:
        page1.append(('SPAN', (current_col, 0), (current_col + 5, 0))) # Span 6 columns
        page1.append(('BOX', (current_col, 0), (current_col + 5, 0), 1, '#000000')) # Box around Title matches screenshot!
        page2.append(('BACKGROUND', (current_col, -1), (current_col + 5, -1), colors.yellow))
        current_col += 6
        if current_col < len(header_row):
            page1.append(('LINEBEFORE', (current_col, 1), (current_col, -1), 1, '#000000'))

    # Add vertical thick grid lines between any extra columns (Vessels, Curd, Snack, Pickle)
    while current_col < len(header_row):
        current_col += 1
        if current_col <= len(header_row):
            page1.append(('LINEBEFORE', (current_col - 1, 1), (current_col - 1, -1), 1, '#000000'))

    # Build the final TableStyles
    style = TableStyle(page1)
    style2 = TableStyle(page1 + page2)


    # --- 3. Render Page 1 Data Table ---
    table = Table(result[:36] , rowHeights=15)  
    table.setStyle(style)
    a, b = table.wrapOn(pdf, 500, 400)  
    table.drawOn(pdf, 20, -55-b)        
    iso2.topTable(pdf, Date, vbcd)

    # --- 4. Render Page 2 Data Table ---
    pdf.showPage()
    pdf.translate(-10, 600)
    
    table2 = Table(result[:2] + result[36:] , rowHeights=15)  
    table2.setStyle(style2)
    a, b = table2.wrapOn(pdf, 500, 400)  
    table2.drawOn(pdf, 20, -10-b)  

    # --- 5. Down-Signatures ---
    pdf.setFont("Helvetica", 10)
    pdf.drawString(80, -590, "Prepared By")
    pdf.drawString(250, -590, "Verified By (Production)")
    pdf.drawString(420, -590, "Distribution HOD")

    # --- 6. Fully Dynamic Summary Table Page 2 ---
    DataReport = [["SrNo", "Item", "Kg", "Quantity"]]
    sr_no = 1  
    
    for key, weight in row.items():
        if 'Couldron' not in key and key != 'Date' and isinstance(weight, (int, float)) and weight > 0:
            
            display_name = Menu.get(key, key.capitalize())
            couldron_key = f"{key}Couldron"
            couldron_val = row.get(couldron_key, '-')
            
            if couldron_val != '-':
                couldron_val = round(couldron_val, 2)
                
            DataReport.append([sr_no, display_name, round(weight, 2), couldron_val])
            sr_no += 1

    table3 = Table(DataReport, rowHeights=15)
    table3.setStyle(style3)
    a, b = table3.wrapOn(pdf, 500, 400)  
    table3.drawOn(pdf, 550, -597) 

    return pdf