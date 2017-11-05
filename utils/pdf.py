import os

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


def draw_header(canvas, name):
    """ Draws the invoice header """
    canvas.setStrokeColorRGB(0.9, 0.5, 0.2)
    canvas.setFillColorRGB(0.2, 0.2, 0.2)
    canvas.setFont('Helvetica', 16)
    canvas.drawString(18 * cm, -1 * cm, 'Invoice')
    if os.path.isfile(name):
        canvas.drawInlineImage(name, 1 * cm, -1 * cm, 250, 16)
    else:
        canvas.drawString(1 * cm, -1 * cm, name)
    canvas.setLineWidth(4)
    canvas.line(0, -1.25 * cm, 21.7 * cm, -1.25 * cm)


def draw_address(canvas, address):
    """ Draws the business address """
    canvas.setFont('Helvetica', 9)
    textobject = canvas.beginText(13 * cm, -2.5 * cm)
    for line in address.strip().splitlines():
        textobject.textLine(line)
    canvas.drawText(textobject)


def draw_footer(canvas, footer):
    """ Draws the invoice footer """
    textobject = canvas.beginText(1 * cm, -27 * cm)
    for line in footer.strip().splitlines():
        textobject.textLine(line)
    canvas.drawText(textobject)


header_func = draw_header
address_func = draw_address
footer_func = draw_footer


def draw_pdf(buffer, data):
    """ Draws the invoice """
    canvas = Canvas(buffer, pagesize=A4)
    canvas.translate(0, 29.7 * cm)
    canvas.setFont('Helvetica', 10)

    canvas.saveState()
    header_func(canvas, data['business_name'])
    canvas.restoreState()

    canvas.saveState()
    footer_func(canvas, data['footer'])
    canvas.restoreState()

    canvas.saveState()
    address_func(canvas, data['address'])
    canvas.restoreState()

    # Client address
    textobject = canvas.beginText(1.5 * cm, -2.5 * cm)
    for line in data['customer_details']:
        textobject.textLine(line)
    canvas.drawText(textobject)

    # Info
    textobject = canvas.beginText(1.5 * cm, -6.75 * cm)
    textobject.textLine(u'Invoice ID: %s' % data['id'])
    textobject.textLine(u'Invoice Date: %s' % data['date'])
    canvas.drawText(textobject)

    # Items
    items = [[u'#', u'Description', u'Amount'], ]
    for count, item in enumerate(data['items']):
        items.append([u'{}'.format(count + 1), item['description'],
                      item['amount']])
    items.append([u'', u'', u''])
    items.append([u'', u'Taxes', u''])
    items.append([u'', u'SGST:', data['sgst']])
    items.append([u'', u'CGST:', data['cgst']])
    items.append([u'', u'Total:', data['total_amount']])
    table = Table(items, colWidths=[2 * cm, 11 * cm, 3 * cm, 3 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
        ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
    ])
    tw, th, = table.wrapOn(canvas, 15 * cm, 19 * cm)
    table.drawOn(canvas, 1 * cm, -8 * cm - th)

    canvas.showPage()
    canvas.save()
