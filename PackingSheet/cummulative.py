from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image,PageBreak, Paragraph, Frame, Spacer
from reportlab.lib.units import inch
from reportlab.lib import styles, colors
from reportlab.lib.styles import ParagraphStyle


page1=[
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightblue),  # Color header row
        ('BACKGROUND', (0, 3), (-1, 3), colors.lightblue),  # Color header row
        ('BACKGROUND', (0, 5), (-1, 5), colors.lightblue),  # Color header row
        ('BACKGROUND', (0, 7), (-1, 7), colors.lightblue),  # Color header row


        #('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),  # Color header row

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Set text color for header row
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),# Vertically align text to the top

        ('SPAN', (1, 0), (6, 0)),  # Span Schools Title
        #('SPAN', (3, 0), (6, 0)),  # Span PS UPS..
        ('SPAN', (7, 0), (13, 0)), # Span Schools Title
        ('SPAN', (14, 0), (19, 0)),  # Span Schools Title
        #('SPAN', (20, 0), (25, 0)),  # Span Schools Title

        ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),  # Align Both Titles        
        #('ALIGN', (1, 2), (-1, -1), 'CENTRE'),  # Align all number in centre


        ('GRID', (0, 1), (-1, -1), 1, '#000000'),  # Add grid lines below super title
        ('GRID', (1, 1), (0, -1), 2, '#000000'),  # Add grid lines after Route name column
        #('GRID', (3, 1), (2, -1), 1, '#000000'),  # Add grid lines after Running name column
        ('GRID', (7, 1), (6, -1), 2, '#000000'),  # Add grid lines Schools Total name column
        ('GRID', (14, 1), (13, -1), 2, '#000000'),  # Add grid lines after Rice Total
        ('GRID', (20, 1), (19, -1), 2, '#000000'),  # Add grid lines after Dal Total
        #('GRID', (26, 1), (25, -1), 1, '#000000'),  # Add grid lines --Curry...
        #('GRID', (27, 1), (26, -1), 1, '#000000'),  # Add grid lines...Snack..


        ('GRID', (1, 0), (19, 0), 2, '#000000'),  # Add grid lines for Super Title
        ('GRID', (0, 2), (-1, 1), 2, '#000000'),  # Add grid lines for Title below


        ('FONTSIZE', (0, 0), (-1, -1), 12),  # Set font size to 1
        ('BOX', (0, 1), (-1, -1), 2, colors.black),  # Out box Nice


    ]

page2=[
          ('BACKGROUND', (1, -1), (6, -1), colors.yellow),  # Color header row Rice all
          ('BACKGROUND', (7, -1), (13, -1), colors.lightblue),  # Color header row Dal All
          ('BACKGROUND', (14, -1), (19, -1), colors.yellow),  # Color header row Dal All

          ('GRID', (0, -1), (-1, -2), 2, '#000000'),  # Add grid lines for Title below

      ]




style = TableStyle(page1+page2)

style2= TableStyle(page1+page2)

style3 = TableStyle([
     ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Color header row
     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  # Set text color for header row
     ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),  # Align numbers to the right
     ('VALIGN', (0, 0), (-1, -1), 'TOP'),# Vertically align text to the top

     ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Align Items to the left


     ('GRID', (0, 0), (-1, -1), 1.0, '#000000'),  # Add grid lines
     ('FONTSIZE', (0, 0), (-1, -1), 9),  # Set font size to 8

])




def function(pdf, result,iso2, row, Date, Menu, vbcd, curryRatio):
    pdf.translate(-10,600)

    # Page 1 Data Table:
    table = Table(result , rowHeights=30)  
    table.setStyle(style)
    a,b=table.wrapOn(pdf, 500, 400)  # Wrap table if it exceeds width
    table.drawOn(pdf, 20, -75-b)  # Specify starting coordinates.
    iso2.topTable(pdf, Date, vbcd)

    # Page 2 Data Table:
    #pdf.showPage()
    #pdf.translate(-10,600)

    # Down-Singanutes:
    pdf.setFont("Helvetica", 10)
    pdf.drawString(80, -530, "Prepared By")
    pdf.drawString(250, -530, "Verified By (Production)")
    pdf.drawString(420, -530, "Distribution HOD")

    # Summary Table Page 1:
    DataReport=[ ["SrNo","Item","Kg", "Quantity"],
                 [1,Menu["Rice"], round(row['Rice'],2),round(row['RiceCouldron'],2)],
                 [2,Menu["Dal"], round(row['Dal'],2),round(row['DalCouldron'],2)],
                 [3,Menu["Curry"], round(row['Curry'],2),round(row['CurryCouldron']*curryRatio,2)],
                 [4,"Curd", round(row['Curd'],2),'-'],
                 [5,"Snack", round(row['Snack'],2),'-'],
            ]

    table3 = Table(DataReport, rowHeights=15)
    table3.setStyle(style3)
    a,b=table3.wrapOn(pdf, 500, 400)  # Wrap table if it exceeds width
    table3.drawOn(pdf, 550, -490)  # Specify starting coordinates.

    return pdf
