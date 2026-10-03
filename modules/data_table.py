# TAPF Image and Top Header Tables:
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, PageBreak, Paragraph, Frame, Spacer
from reportlab.lib.units import inch
from reportlab.lib import styles, colors
from reportlab.lib.styles import ParagraphStyle
import os

def replace_zeros_with_empty(data):
    for i in range(1, len(data)):  # Skip header row at index 0
        for j in range(len(data[i])):
            if data[i][j] == 0:
                data[i][j] = ""
    return data

def colorFunction(x):
    colorArray = []
    for i in range(x - 1):
        if i % 2 != 0:
            colorArray.append(('BACKGROUND', (0, i), (-1, i), colors.lightblue))
    return colorArray

def dataTable(pdf, results, top_table, routes, menu, vbcd):
    # Dynamic column and styles build based on chosen extra items
    from modules import seatable
    selected_items = seatable.selected_items
    
    # 1. Build TitleArray (headers row) dynamically
    TitleArray = [
        'SrNo', 'School', 'PS', 'UPS', 'ZPHS', 'Total', 'PS', 'UPS', 'ZPHS', 'Total',
        '100%', '75%', '50%', '25%', '13%', 'Total',
        '150%', '100%', '75%', '50%', '25%', '13%', 'Total',
        '100%', '75%', '50%', '25%', '13%', 'Total'
    ]
    for name, _, _ in selected_items:
        TitleArray.append(name)
    TitleArray.extend(['Time', 'Signature   '])
    
    # 2. Build array (Super Title row) dynamically
    array = [
        "", 1, "Enrollment", 3, 4, 5, "Indent", 7, 8, 9,
        menu[0], 11, 12, 13, 14, 15,
        menu[1], 17, 18, 19, 20, 21, 22,
        menu[2], 24, 25, 26, 27, 28
    ]
    for _ in range(len(selected_items)):
        array.append("")
    array.extend(["", ""]) # placeholders for Time and Signature
    
    # 3. Build TableStyle styleArray dynamically
    styleArray = [
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightblue),  # Color header row
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),       # Set text color for header row
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),                # Vertically align text to the top
        ('GRID', (0, 1), (-1, -1), 0.7, '#000000'),          # All table Add grid lines
        
        # Original border lines:
        ('GRID', (0, 1), (-1, 0), 1.5, '#000000'),
        ('GRID', (0, -1), (-1, -2), 1.5, '#000000'),
        ('GRID', (2, 0), (28, 0), 1.5, '#000000'),
        
        # Grid block divider lines
        ('GRID', (2, 0), (1, -1), 1.5, '#000000'),   # School divider
        ('GRID', (6, 0), (5, -1), 1.5, '#000000'),   # PS divider
        ('GRID', (10, 0), (9, -1), 1.5, '#000000'),  # EPS divider
        ('GRID', (16, 0), (15, -1), 1.5, '#000000'), # Rice divider
        ('GRID', (23, 0), (22, -1), 1.5, '#000000'), # Dal divider
        ('GRID', (29, 0), (28, -1), 1.5, '#000000'), # Curry divider
    ]
    
    # Draw vertical divider grid lines for Curd, extra items, Time, and Signature dynamically:
    for idx in range(29, len(TitleArray)):
        styleArray.append(('GRID', (idx, 0), (idx - 1, -1), 1.5, '#000000'))
        
    # Spans (super headers):
    styleArray.extend([
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (5, 0)),
        ('SPAN', (6, 0), (9, 0)),
        ('SPAN', (10, 0), (15, 0)),
        ('SPAN', (16, 0), (22, 0)),
        ('SPAN', (23, 0), (28, 0)),
        ('SPAN', (29, 0), (-1, 0)),  # Spans from Curd to the end
        ('SPAN', (0, -1), (1, -1)),
        ('BOX', (0, 1), (-1, -1), 1.5, '#000000'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTRE'),
    ])
    
    # Background colors for Totals row (colored background)
    styleArray.extend([
        ('BACKGROUND', (10, -1), (15, -1), colors.lightblue),
        ('BACKGROUND', (16, -1), (22, -1), colors.yellow),
        ('BACKGROUND', (23, -1), (28, -1), colors.lightblue),
    ])
    
    # Font sizes:
    styleArray.extend([
        ('FONTSIZE', (0, 0), (-1, -1), 4.5),      # Default font size
        ('FONTSIZE', (0, 1), (-1, 1), 5),         # Header font size
        ('FONTSIZE', (10, 2), (-1, -1), 10),      # Vessels, Curd, Snacks, and Totals area
        ('FONTSIZE', (1, 0), (1, -1), 5),         # Schools Column
        ('FONTSIZE', (0, 0), (-1, 0), 7),         # Super title super title
        ('FONTSIZE', (0, 1), (-1, 1), 4),
        ('VALIGN', (0, 0), (-1, 0), 'TOP'),
    ])

    for route in routes:
        pdf.translate(-5, 600)

        # Build page-specific data
        Data = [TitleArray]
        for result in results[1:]:
            if route == result[-1]:
                Data.append(result[:-1])
        
        # Calculate column sums
        data = []     
        for item in Data[1:]:
            data.append(item[2:])

        # Transpose and sum each column, rounding float results to 2 decimal places
        vertical_total = []
        for col in zip(*data):
            col_sum = sum(x for x in col if isinstance(x, (int, float)))
            if isinstance(col_sum, float):
                col_sum = round(col_sum, 2)
            vertical_total.append(col_sum)
        
        # Append totals as the last row
        Data.append(["Total"] + [""] + vertical_total)
        
        # Replace 0 with empty
        Data = replace_zeros_with_empty(Data)
        Data = [array] + Data

        background = colorFunction(len(Data))

        # ReportLab syntax:
        table = Table(Data, rowHeights=15)
        table.setStyle(TableStyle(styleArray + background))
        a, b = table.wrapOn(pdf, 500, 400)  # Wrap table if it exceeds width
        table.drawOn(pdf, 20, -80 - b)      # Specify starting coordinates

        # Draw ISO header top table
        safe_route = route if route is not None else "Unknown"
        top_table.topTable(pdf, safe_route, menu[-1], vbcd)

        # Create next page
        pdf.showPage()
        
    return pdf
