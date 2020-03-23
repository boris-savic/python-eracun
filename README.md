# Python e-Račun

Python library that enables you to generate e-Slog (e-Račun) XML in 1.6.1 and 2.0 format. 

## 1. Installation

    $ pip install eracun-generator
    
# 2. Quick Start

## 2.1. Create Issuer and Recipient objects

```python
from eracun_generator.core import Invoice, ReferenceDocument, Business

issuer = Business(name='Company d.o.o.',
                  address='Our Address 100',
                  zip_code=1000,
                  city='Ljubljana',
                  country='Slovenia',
                  country_iso_code='SI',
                  vat_id='12345678',
                  iban='SI56111122223333456',
                  bic='BAKOSI2XXXX',
                  registration_number='555555555')

recipient = Business(name='Recipient Name',
                     address='Recipient Address 101',
                     zip_code=1000,
                     city='Ljubljana',
                     country='Slovenia',
                     country_iso_code='SI',
                     vat_id='87654321',
                     iban='SI56111122223333444',
                     bic='BAKOSI2XXXX',
                     registration_number='666666666')
```

## 2.2. Create Invoice object

```python
from decimal import Decimal
from datetime import datetime

from eracun_generator.core import Invoice, ReferenceDocument, Business

invoice = Invoice(
    issuer=issuer,
    recipient=recipient,
    invoice_number='1-2019-154',
    total_without_tax=Decimal('1.48'),
    total_with_tax=Decimal('1.81'),
    location_address='Ljubljana',
    date_issued=datetime.now(),
    date_of_service=datetime.now(),
    date_due=datetime.now(),
    payment_reference='SI001-2019-154',
    global_discount_amount=None,
    global_discount_percentage=None,
    intro_text='Some general description about the invoice. Not neccessary.')

# Add items
invoice.add_item(
    row_number=1,
    item_name='CocaCola 0.33L',
    quantity=Decimal('2.00'),
    price_without_tax=Decimal('0.82'),
    total_with_tax=Decimal('1.81'),
    total_without_tax=Decimal('1.48'),
    tax_rate=22.00,
    discount_percentage=10,
    discount_amount=0.16)


# Add tax summary
invoice.add_tax_summary(tax_rate=22, tax_base=1.48, tax_amount=0.33)


# Add reference document 
invoice.add_reference_document('NAR-54654', ReferenceDocument.TYPE_ORDER_NUMBER)

# Print XML 
print(invoice.render_xml(v2=True)) # set v2 parameter to False to use e-Slog v1.6.1
```

## 2.3. Get Envelope

```python
print(invoice.render_envelope(attachments=[('invoice.pdf', 'PDF')]))
```

