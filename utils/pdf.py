import os

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table, Paragraph
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import landscape, A4, A5
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle


STYLES = {
    'pAlignLeft': ParagraphStyle(name="left", alignment=TA_LEFT),
    'pAlignRight': ParagraphStyle(name='right', alignment=TA_RIGHT)
}


def draw_header(canvas, name):
    """ Draws the invoice header """
    canvas.setStrokeColorRGB(0.9, 0.5, 0.2)
    canvas.setFillColorRGB(0.2, 0.2, 0.2)
    canvas.setFont('Helvetica', 16)
    canvas.drawString(12.7 * cm, -1 * cm, 'Invoice')
    if os.path.isfile(name):
        canvas.drawInlineImage(name, 0.4 * cm, -1 * cm, 100, 32)
    else:
        canvas.drawString(0.4 * cm, -1 * cm, name)
    canvas.setLineWidth(4)
    canvas.line(0, -1.25 * cm, 21.7 * cm, -1.25 * cm)


def draw_address(canvas, address):
    """ Draws the business address """
    canvas.setFont('Helvetica', 9)
    textobject = canvas.beginText(8.5 * cm, -2.5 * cm)
    for line in address.strip().splitlines():
        textobject.textLine(line)
    canvas.drawText(textobject)


def draw_footer(canvas, footer):
    """ Draws the invoice footer """
    textobject = canvas.beginText(0.7 * cm, -18 * cm)
    for line in footer.strip().splitlines():
        textobject.textLine(line)
    canvas.drawText(textobject)


header_func = draw_header
address_func = draw_address
footer_func = draw_footer


def draw_pdf(buffer, data):
    """ Draws the invoice """
    canvas = Canvas(buffer, pagesize=A5)
    canvas.translate(0, 20.7 * cm)
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
    textobject = canvas.beginText(0.5 * cm, -2.5 * cm)
    for line in data['customer_details']:
        textobject.textLine(line)
    canvas.drawText(textobject)

    # Info
    textobject = canvas.beginText(0.5 * cm, -6.75 * cm)
    textobject.textLine(u'Invoice ID: %s' % data['id'])
    textobject.textLine(u'Invoice Date: %s' % data['date'].strftime(
        '%Y-%m-%d'))
    canvas.drawText(textobject)

    # Items
    items = [[u'#', u'Description', u'Amount (INR)'], ]
    for count, item in enumerate(data['items']):
        items.append([u'{}'.format(count + 1),
                      Paragraph(item['description'], STYLES['pAlignLeft']),
                      item['amount']])
    items.append([u'', u'', u''])
    items.append([u'', Paragraph('<b>Taxes</b>', STYLES['pAlignRight']), u''])
    items.append([u'', u'SGST:', data['sgst']])
    items.append([u'', u'CGST:', data['cgst']])
    if 'discount' in data and data['discount']:
        items.append([u'', Paragraph('<b>Discount</b>', STYLES['pAlignRight']), data['discount']])
    items.append([u'', Paragraph(u'<b>Total:</b>', STYLES['pAlignRight']),
                  Paragraph('<b>{}</b>'.format(data['total_amount']), STYLES['pAlignRight'])])
    items.append([u'', Paragraph(u'Paid:', STYLES['pAlignRight']),
                  Paragraph('{}'.format(data['paid']), STYLES['pAlignRight'])])
    items.append([u'', Paragraph(u'<b>Due:</b>', STYLES['pAlignRight']),
                  Paragraph('<b>{}</b>'.format(data['due']), STYLES['pAlignRight'])])
    table = Table(items, colWidths=[1 * cm, 10 * cm, 2.7 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
        ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
    ])
    tw, th, = table.wrapOn(canvas, 15 * cm, 19 * cm)
    table.drawOn(canvas, 0.5 * cm, -8 * cm - th)

    canvas.showPage()
    canvas.save()
