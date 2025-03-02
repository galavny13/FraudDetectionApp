from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Data for the table
data = [
    ['Date', 'Merchant', 'Category', 'Amount', 'Currency', 'Transaction Type'],
    ['2019-10-09 13:49:52', 'Kuhic LLC', 'shopping', '965.55', 'USD', 'Purchase'],
    ['2019-10-09 21:40:45', 'Brown PLC', 'entertainment', '1200.50', 'USD', 'Purchase'],
    ['2019-10-10 00:55:35', 'Christiansen-Gusikowski', 'home', '3500.75', 'USD', 'Purchase'],
    ['2019-10-12 22:33:05', 'fraud_Baumbach, Feeney and Morar', 'shopping', '967.92', 'USD', 'Purchase'],
    ['2019-10-13 01:06:37', 'Rutherford-Mertz', 'grocery', '281.06', 'USD', 'Purchase'],
    ['2019-10-13 05:32:10', 'Parisian and Sons', 'gas_transport', '46.22', 'USD', 'Purchase'],
    ['2019-10-17 20:26:40', 'Ruecker Group', 'misc', '843.91', 'USD', 'Purchase'],
    ['2019-10-22 05:05:38', 'Kris-Weimann', 'misc', '1.13', 'USD', 'Purchase']
]

# Define the output PDF file name
pdf_file = "sample_credit_card_fraud_transactions.pdf"

# Create the PDF document
doc = SimpleDocTemplate(pdf_file, pagesize=letter)

# Create the table with the data
table = Table(data)

# Define the table style
style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
])

table.setStyle(style)

# Build the PDF
elements = [table]
doc.build(elements)

print(f"PDF '{pdf_file}' has been created successfully.")
