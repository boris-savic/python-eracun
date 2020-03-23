from decimal import Decimal

from lxml import etree

from eracun_generator.builder import build_xml
from eracun_generator.definitions import construct_invoice_json
from eracun_generator.definitionsV2 import construct_invoice_json as construct_invoice_jsonV2
from eracun_generator.envelope.utils import convert_invoice_to_envelope
from eracun_generator.utils import ds_tag, sign_invoice


class Business:
    """
    Prepare Business object for Issuer and Recipient instances.
    """
    def __init__(self, name, address, city, zip_code, country, country_iso_code, vat_id, iban=None, bic=None, registration_number=None):
        self.name = name
        self.address = address
        self.city = city
        self.zip_code = zip_code
        self.country = country
        self.country_iso_code = country_iso_code
        self.iban = iban.replace(" ", "") if iban else None  # remove any spaces
        self.bic = bic.ljust(11, 'X') if bic else None  # Schema requires 11 chars long - add Xs at the end of BIC/SWIFT
        self.registration_number = registration_number
        self.vat_id = vat_id


class ReferenceDocument:
    TYPE_PROFORMA_INVOICE = 'AAB'
    TYPE_DELIVERY_ORDER_NUMBER = 'AAJ'
    TYPE_DELIVERY_FORM = 'AAK'
    TYPE_BENEFICIARYS_REFERENCE = 'AFO'
    TYPE_CONSODILDATED_INVOICE = 'AIZ'
    TYPE_MESSAGE_BATCH_NUMBER = 'ALL'
    TYPE_RECEIVING_ADVICE_NUMBER = 'ALO'
    TYPE_COMMERCIAL_ACCOUNT_SUMMARY = 'APQ'
    TYPE_CREDIT_NOTE = 'CD'
    TYPE_CUSTOMER_REFERENCE_NUMBER = 'CR'
    TYPE_CONTRACT = 'CT'
    TYPE_DEBIT_NOTE = 'DL'
    TYPE_DELIVERY_NOTE = 'DQ'
    TYPE_IMPORT_LICENCE_NUMBER = 'IP'
    TYPE_INVOICE = 'IV'
    TYPE_ORDER_NUMBER = 'ON'
    TYPE_PRICE_LIST_NUMBER = 'PL'
    TYPE_PURCHASE_ORDER_RESPONSE_NUMBER = 'POR'
    TYPE_EXPORT_REFERENCE_NUMBER = 'RF'
    TYPE_SPECIFICATION_NUMBER = 'SZ'
    TYPE_ORDER_NUMBER_SUPPLIER = 'VN'

    def __init__(self, document_number, type_code=TYPE_ORDER_NUMBER):
        self.document_number = document_number
        self.type_code = type_code


class InvoiceItem:
    def __init__(self,
                 row_number,
                 item_name,
                 quantity,
                 price_without_tax,
                 total_with_tax,
                 total_without_tax,
                 tax_rate,
                 tax_rate_type='S',
                 discount_percentage=None,
                 discount_amount=None,
                 unit='PCE',
                 ean=''):
        self.row_number = row_number
        self.item_name = item_name
        self.quantity = quantity
        self.price_without_tax = price_without_tax   # CenaPostavke

        self.total_with_tax = total_with_tax         # total - after discount and tax
        self.total_without_tax = total_without_tax   # total - after discount

        self.discount_percentage = discount_percentage
        self.discount_amount = discount_amount

        self.tax_rate = tax_rate
        self.tax_rate_type = tax_rate_type

        self.unit = unit
        self.ean = ean

        self.item_description_code = 'F'
        self.quantity_type = '47'


class TaxSummary:
    def __init__(self, tax_rate, tax_amount, tax_base, tax_type='S'):
        self.tax_rate = tax_rate
        self.tax_amount = tax_amount
        self.tax_base = tax_base
        self.tax_type = tax_type


class Invoice:
    TYPE_MEASURED_SERVICES = '82'
    TYPE_FINANCIAL_CREDIT_NOTE = '83'
    TYPE_FINANCIAL_DEBIT_NOTE = '84'
    TYPE_INVOICING_DATA_SHEET = '130'
    TYPE_PROFORMA_INVOICE = '325'
    TYPE_INVOICE = '380'
    TYPE_CREDIT_NOTE = '381'
    TYPE_COMMISION_NOTE = '382'
    TYPE_DEBIT_NOTE = '383'
    TYPE_CORRECTED_INVOICE = '384'
    TYPE_CONSOLIDATED_INVOICE = '385'
    TYPE_PREPAYMENT_INVOICE = '386'
    TYPE_SELF_BILLED_INVOICE = '389'
    TYPE_DELCREDRE_INVOICE = '390'
    TYPE_FACTORED_INVOICE = '393'

    FUNCTION_CANCELLATION = '1'
    FUNCTION_REPLACE = '5'
    FUNCTION_DUPLICATE = '7'
    FUNCTION_ORIGINAL = '9'
    FUNCTION_COPY = '31'
    FUNCTION_ADDITIONAL_TRANSMISSION = '43'

    PAYMENT_REQUIRED = '0'
    PAYMENT_DIRECT_DEBIT = '1'
    PAYMENT_ALREADY_PAID = '2'
    PAYMENT_OTHER_NO_PAYMENT = '3'

    LOCATION_PAYMENT = '57'
    LOCATION_ISSUED = '91'
    LOCATION_SALE = '162'

    def __init__(self,
                 issuer,  # Business object
                 recipient,  # Business object
                 invoice_number,
                 total_without_tax,
                 total_with_tax,
                 location_address,
                 date_issued,
                 date_of_service,
                 date_due,
                 payment_reference,
                 global_discount_amount=None,
                 global_discount_percentage=None,
                 intro_text=None,   # type AAI = general information text  - GLAVA_TEXT
                 outro_text=None,   # type AAI = general information text  - DODATNI_TEKST
                 invoice_type=TYPE_INVOICE,
                 currency='EUR',
                 invoice_function=FUNCTION_ORIGINAL,
                 payment_type=PAYMENT_REQUIRED,
                 payment_purpose="GDSV",
                 additional_remittance_information=None,
                 location_code=LOCATION_ISSUED):
        # Business objects
        self.issuer = issuer
        self.recipient = recipient

        self.invoice_number = invoice_number

        self.total_without_tax = total_without_tax
        self.total_with_tax = total_with_tax

        self.location_address = location_address

        self.date_issued = date_issued
        self.date_of_service = date_of_service
        self.date_due = date_due

        self.payment_reference = payment_reference

        self.global_discount_amount = global_discount_amount
        self.global_discount_percentage = global_discount_percentage

        self.intro_text = intro_text
        self.outro_text = outro_text

        self.invoice_type = invoice_type
        self.currency = currency
        self.invoice_function = invoice_function
        self.payment_type = payment_type
        self.payment_purpose = payment_purpose
        self.additional_remittance_information = additional_remittance_information or f'Racun st. {self.invoice_number}'

        self.location_code = location_code

        self.date_issued_code = '137'
        self.date_of_service_code = '35'
        self.date_due_code = '13'

        self.reference_documents = []

        self.document_items = []

        self.total_without_discount = Decimal('0')

        self.tax_summaries = []

    def add_reference_document(self, reference_document_number, reference_type=ReferenceDocument.TYPE_ORDER_NUMBER):
        self.reference_documents.append(ReferenceDocument(reference_document_number, reference_type))

    def add_tax_summary(self, tax_rate, tax_base, tax_amount):
        self.tax_summaries.append(TaxSummary(tax_rate=tax_rate, tax_amount=tax_amount, tax_base=tax_base))

    def add_item(self,
                 row_number,
                 item_name,
                 quantity,
                 price_without_tax,
                 total_with_tax,
                 total_without_tax,
                 tax_rate,
                 ean=None,
                 discount_percentage=None,
                 discount_amount=None,
                 unit='PCE'):
        self.document_items.append(InvoiceItem(row_number=row_number,
                                               item_name=item_name,
                                               quantity=quantity,
                                               price_without_tax=price_without_tax,
                                               total_with_tax=total_with_tax,
                                               total_without_tax=total_without_tax,
                                               tax_rate=tax_rate,
                                               ean=ean,
                                               discount_percentage=discount_percentage,
                                               discount_amount=discount_amount,
                                               unit=unit))

        self.total_without_discount = self.total_without_discount + (quantity * price_without_tax)

    def render_envelope(self, attachments=None, sender_bic=None, recipient_bic=None):
        """
        Render envelope to be included with the eRacun.

        Every Envelope will have eRacun.xml as an attachment. It is recommended to
        include PDF invoice as an attachment as well.

        To include attachment data in envelope pass in the attachment name and format. For example

        attachments=[('invoice.pdf', 'PDF')]

        :param attachments:
        :param sender_bic: Set to UJPLSI20ICL for DEV environment and UJPLSI2DICL for production environment if
                           the issuer is government budget user.
        :param recipient_bic: Set to UJPLSI20ICL for DEV environment and UJPLSI2DICL for production environment if
                              the recipient is government budget user.
        :return:
        """
        if attachments is None:
            attachments = []

        attachments.insert(0, ('eRacun.xml', 'XML', 0))

        return ("%s%s" % ('<?xml version="1.0" encoding="UTF-8"?>\n',
                          etree.tostring(build_xml(convert_invoice_to_envelope(self, attachments, sender_bic, recipient_bic)),
                                         pretty_print=True,
                                         xml_declaration=False,
                                         encoding="utf-8").decode('utf-8')))

    def render_xml(self, key=None, cert=None, v2=True):
        if v2:
            xml_content = build_xml(construct_invoice_jsonV2(self))

            if key and cert:
                xml_content = sign_invoice(construct_invoice_jsonV2(self), key, cert)

            return ("%s%s" % ('<?xml version="1.0" encoding="UTF-8"?>\n',
                            etree.tostring(xml_content,
                                            pretty_print=False,
                                            xml_declaration=False,
                                            method="c14n",
                                            ).decode('utf-8')))
        else :
            xml_content = build_xml(construct_invoice_json(self))

            if key and cert:
                xml_content = sign_invoice(construct_invoice_json(self), key, cert)

            return ("%s%s" % ('<?xml version="1.0" encoding="UTF-8"?>\n',
                            etree.tostring(xml_content,
                                            pretty_print=False,
                                            xml_declaration=False,
                                            method="c14n",
                                            ).decode('utf-8')))
