import textwrap
from decimal import Decimal


def construct_invoice_json(invoice):
    NS = 'http://www.w3.org/2001/XMLSchema-instance'

    data = {
        '_name': 'Invoice',
        '_attrs': [
            ('xmlns', 'urn:eslog:2.00'),
            ("{%s}noNamespaceSchemaLocation" % NS, 'http://www.roseslovenia.eu/e_files/news/eSLOG20_INVOIC_v200.xsd'),
        ],
        '_ns': {
            'xs4xs': 'http://www.w3.org/2001/XMLSchema',
            'in':'http://uri.etsi.org/01903/v1.1.1#',
            'ds':'http://www.w3.org/2000/09/xmldsig#',
            'xsi': NS
        },
        'invoice': {
            '_name': 'M_INVOIC',
            '_attrs': [('Id', 'data')],
            '_sorting':['S_UNH', 'S_BGM', 'S_DTM', 'S_PAI', 'S_ALI', 'S_FTX', 'G_SG1', 'G_SG2', 'G_SG6', 'G_SG7', 'G_SG8', 'G_SG9', 'G_SG12', 'G_SG14', 'G_SG16', 'G_SG24', 'G_SG26', 'S_UNS', 'S_CNT', 'G_SG50', 'G_SG52', 'G_SG53', 'S_UNT'],
            'document_header': construct_document_header_data(invoice),
            'header': construct_header_data(invoice),
            'date_issued': construct_date_data(invoice.date_issued_code, invoice.date_issued),
            'date_of_service': construct_date_data(invoice.date_of_service_code, invoice.date_of_service),
            'payment_type': construct_payment_type_data(invoice),
            'payment_purpose': construct_payment_purpose_data(invoice),
            'issuer': construct_company_data(invoice.issuer, 'II'),
            'buyer': construct_company_data(invoice.recipient, 'BY'),
            'recipient': construct_company_data(invoice.recipient, 'IV'),
            'currency': construct_currency_data(invoice.currency),
            'payment_terms': construct_payment_terms_data(invoice.date_due_code, invoice.date_due),
            'payment_data': construct_payment_data(invoice.total_with_tax)
        }  # end invoice
    }

    if invoice.payment_reference != None:
        data['invoice']['payment_reference_data'] = construct_payment_reference_data(invoice.payment_reference)

    for i, reference_document in enumerate(invoice.reference_documents):
        data['invoice'][f"reference_document_{i}"] = construct_reference_document_data(reference_document)

    if invoice.global_discount_amount:
        data['invoice']['global_discount'] = construct_global_discount_data(invoice.global_discount_amount, invoice.global_discount_percentage)

    if invoice.intro_text:
        data['invoice']['intro_text'] = construct_custom_text_data('GEN', invoice.intro_text)

    for i, item in enumerate(invoice.document_items):
        data['invoice'][f"item_{i}"] = construct_item_data(item)

    for i, ts in enumerate(invoice.tax_summaries):
        data['invoice'][f"tax_summary_{i}"] = construct_tax_summary_data(ts)

    # add final sums to invoice
    # Total without discount
    data['invoice']['sums_without_discounts'] = construct_sums_data(amount=invoice.total_without_discount, sum_type='79')
    # Discounts amount
    data['invoice']['sums_discounts'] = construct_sums_data(amount=invoice.total_without_discount - invoice.total_without_tax, sum_type='260')
    # Tax base sums
    data['invoice']['sums_tax_base_amount'] = construct_sums_data(amount=invoice.total_without_tax, sum_type='389')
    # Taxes amount
    data['invoice']['sums_taxes'] = construct_sums_data(amount=invoice.total_with_tax - invoice.total_without_tax, sum_type='259')
    # Total amount - with taxes
    data['invoice']['sums_total_amount'] = construct_sums_data(amount=invoice.total_with_tax, sum_type='388')

    if invoice.outro_text:
        data['invoice']['outro_text'] = construct_custom_text_data('GEN', invoice.outro_text)

    return data

def construct_document_header_data(invoice):
    header = {
        '_name': 'S_UNH',
        'invoice_no':{
            '_name': 'D_0062',
            '_value': invoice.invoice_number
        },
        'data':{
            '_name':'C_S009',
            'val1':{
                '_name': 'D_0065',
                '_value': 'INVOIC'
            },
            'val2':{
                '_name': 'D_0052',
                '_value': 'D'
            },
            'val3':{
                '_name': 'D_0054',
                '_value': '01B'
            },
            'val4':{
                '_name': 'D_0051',
                '_value': 'UN'
            }
        }

    }

    return header

def construct_header_data(invoice):
    header = {
        '_name': 'S_BGM',
        'invoice_type': {
            '_name': 'C_C002',
            'value_tag':{
                '_name': 'D_1001',
                '_value': invoice.invoice_type,
            }
        },
        'invoice_number': {
            '_name': 'C_C106',
            'value_tag':{
                '_name': 'D_1004',
                '_value': invoice.invoice_number,
            }
        }
    }

    return header

def construct_payment_type_data(invoice):
    header = {
        '_name': 'S_FTX',
        'key': {
            '_name': 'D_4451',
            '_value': 'PAI'
        },
        'value': {
            '_name': 'C_C108',
            'value_tag':{
                '_name': 'D_4440',
                '_value': invoice.payment_type,
            }
        }
    }

    return header

def construct_payment_purpose_data(invoice):
    header = {
        '_name': 'S_FTX',
        'key': {
            '_name': 'D_4451',
            '_value': 'ALQ'
            
        },
        'value': {
            '_name': 'C_C108',
            'value_tag':{
                '_name': 'D_4440',
                '_value': invoice.payment_purpose,
            }
        }
    }

    return header

def construct_date_data(date_code, date):
    date = {
        '_name': 'S_DTM',
        'wrapper': {
            '_name': "C_C507",
            'date_type': {
                '_name': 'D_2005',
                '_value': date_code
            },
            'date': {
                '_name': 'D_2380',
                '_value': date.strftime('%Y-%m-%d')
            }
        }
    }

    return date

def construct_currency_data(currency):
    currency = {
        '_name': 'G_SG7',
        'wrapper':{
            '_name': 'S_CUX',
            'wrapper':{
                '_name': 'C_C504',
                'currency_type': {
                    '_name': 'D_6347',
                    '_value': '2',
                },
                'currency_code': {
                    '_name': 'D_6345',
                    '_value': currency,
                },
            }
        }
    }

    return currency

def construct_location_data(location_code, location_address): # does not translate
    location = {
        '_name': 'Lokacije',
        'location_code': {
            '_name': 'VrstaLokacije',
            '_value': location_code,
        },
        'location_name': {
            '_name': 'NazivLokacije',
            '_value': location_address,
        },
    }

    return location

def construct_company_data(business, business_type='II'):
    data = {
        '_name': 'G_SG2',
        'info1': {
            '_name': 'S_NAD',
            'business_type' :{
                '_name': 'D_3035',
                '_value': business_type
            },
            'name': {
                '_name': 'C_C080',
            },
            'address': {
                '_name': 'C_C059',
            },
            'city': {
                '_name': 'D_3164',
                '_value': business.city
            },
            'zip_code': {
                '_name': 'D_3251',
                '_value': str(business.zip_code)
            },
            'country_code': {
                '_name': 'D_3207',
                '_value': business.country_iso_code
            }
        }
    }

    # TODO: check if ok
    # Add business name
    business_name_split = textwrap.wrap(business.name, 70, break_long_words=True)

    for i, bn_part in enumerate(business_name_split):
        i = i + 1  # Start from 1
        data['info1']['name'][f"part_{i}"] = {
            '_name': f"D_3036_{i}",
            '_value': bn_part
        }

        if i == 1:
            data['info1']['name'][f"part_{i}"]["_name"] = "D_3036"

        if i == 4:
            break  # Stop at max length

    # Add business address
    addr_split = textwrap.wrap(business.address, 35, break_long_words=True)

    for i, addr_part in enumerate(addr_split):
        i = i + 1  # Start from 1
        data['info1']['address'][f"part_{i}"] = {
            '_name': f"D_3042_{i}",
            '_value': addr_part
        }

        if i == 1:
            data['info1']['address'][f"part_{i}"]["_name"] = "D_3042"

        if i == 4:
            break  # Stop at max length

    if business.iban:
        data['financial_info'] = {
            '_name': 'S_FII',
            'type':{
                '_name': 'D_3035',
                '_value': 'BB'
            },
            'bank_account_info1': {
                '_name': 'C_C078',
                'iban': {
                    '_name': 'D_3194',
                    '_value': business.iban
                },
                'owner':{
                    '_name': 'D_3192',
                    '_value': business.name[:34]
                }
            },
            'bank_account_info2': {
                '_name': 'C_C088',
                'bic': {
                    '_name': 'D_3433',
                    '_value': business.bic
                }
            }
        }

    if business.vat_id:
        data['vat_id'] = {
            '_name': 'G_SG3',
            'wrapper':{
                '_name': 'S_RFF',
                'wrapper':{
                    '_name': 'C_C506',
                    'type': {
                        '_name': 'D_1153',
                        '_value': 'VA'
                    },
                    'vat': {
                        '_name': 'D_1154',
                        '_value': str(business.vat_id)
                    }
                }
            }
        }

    if business.registration_number:
        data['registration_number'] = {
            '_name': 'G_SG3',
            'wrapper':{
                '_name': 'S_RFF',
                'wrapper':{
                    '_name': 'C_C506',
                    'type': {
                        '_name': 'D_1153',
                        '_value': 'GN'
                    },
                    'vat': {
                        '_name': 'D_1154',
                        '_value': str(business.registration_number)
                    }
                }
            }
        }

    return data

def construct_payment_terms_data(date_due_code, date_due):
    payment_terms = {
        '_name': 'G_SG8',
        'term_data': {
            '_name': 'S_PAT',
            'term_code': {
                '_name': 'D_4279',
                '_value': '1',
            }
        },
        'term_due': {
            '_name': 'S_DTM',
            'wrapper':{
                '_name': 'C_C507',
                'term_due_type': {
                    '_name': 'D_2005',
                    '_value': date_due_code,
                },
                'term_due_date': {
                    '_name': 'D_2380',
                    '_value': date_due.strftime('%Y-%m-%d'),
                },
            }
        }
    }

    return payment_terms

def construct_payment_data(total_with_tax):
    reference = {
        '_name': 'G_SG50',
        'invoice_amounts': {
            '_name': 'S_MOA',
            'wrapper':{
                '_name': 'C_C516',
                'type': {
                    '_name': 'D_5025',
                    '_value': '9'  # Amount to be paid
                },
                'amount': {
                    '_name': 'D_5004',
                    '_value': str(total_with_tax)
                }
            }
        }
    }

    return reference

def construct_payment_reference_data(payment_reference):
    reference = {
        '_name': 'G_SG1',
        'reference': {
            '_name': 'S_RFF',
            'wrapper':{
                '_name':'C_C506',
                'ref_type': {
                    '_name': 'D_1153',
                    '_value': 'PQ'
                },
                'ref_number': {
                    '_name': 'D_1154',
                    '_value': payment_reference
                }
            }
            
        }
    }

    return reference

def construct_reference_document_data(reference_document):
    reference_doc_data = {
        '_name': 'G_SG1',
        'wrapper':{
            '_name': 'S_RFF',
            'wrapper':{
                '_name': 'C_C506',
                'document_type': {
                    '_name': 'D_1153',
                    '_value': reference_document.type_code
                },
                'document_number': {
                    '_name': 'D_1154',
                    '_value': reference_document.document_number
                }
            }
        }
    }

    return reference_doc_data

def construct_global_discount_data(discount_amount, discount_percentage):
    discount_data = {
        '_name': 'G_SG16',
        'description': {
            '_name': 'S_ALC',
            'type':{
                '_name':'D_5463',
                '_value':'A'
            },
            'wrapper':{
                '_name': 'C_C552',
                'desc': {
                    '_name':'D_1230',
                    '_value': 'SKUPNI POPUST'
                },
                'type': {
                    '_name':'D_5189',
                    '_value': '42' #check if correct
                }
            }
        },
        'percentage': {
            '_name': 'G_SG19',
            'wrapper': {
                '_name': 'S_PCD',
                'wrapper': {
                    '_name': 'C_C501',
                    'type': {
                        '_name':'D_5245',
                        '_value':'1'
                    },
                    'val': {
                        '_name':'D_5482',
                        '_value': str(discount_percentage)
                    }
                }
            }
        },
        'amount': {
            '_name': 'G_SG20',
            'wrapper': {
                '_name': 'S_MOA',
                'wrapper': {
                    '_name': 'C_C516',
                    'type': {
                        '_name':'D_5025',
                        '_value':'1'
                    },
                    'val': {
                        '_name':'D_5004',
                        '_value': str(discount_amount)
                    }
                }
            }
        },
    }

    return discount_data

def construct_custom_text_data(text_format, text):
    """
    Text must be split into 70 chars long strings.
    :param text_format: AAI or other predefined formats
    :param text_type:
    :param text:
    :return:
    """
    text_split = textwrap.wrap(text, 70, break_long_words=True)

    custom_text = {
        '_name': 'S_FTX',
        'format': {
            '_name': 'D_4451',
            '_value': text_format,
        },
        'content': {
            '_name': 'C_C108'
        }
    }

    for i, txt in enumerate(text_split):
        # Since text_1 is used for text_type we must enumerate from 2 onwards
        i = i + 1

        name = 'D_4440'
        if i > 1 :
            name = f"D_4440_{i}"

        custom_text['content'][f"text_{i}"] = {
            '_name': name,
            '_value': txt
        }

        # Stop the loop if index is 5 - we can't place any more than  that in XML.
        if i == 5:
            break

    return custom_text

def construct_item_data(item):
    data = {
        '_name': 'G_SG26',
        '_sorting':['S_LIN', 'S_PIA', 'S_IMD', 'S_MEA', 'S_QTY', 'S_ALI', 'S_DTM', 'S_GIN', 'S_QVR', 'S_FTX', 'G_SG27', 'G_SG28', 'G_SG29', 'G_SG31', 'G_SG33', 'G_SG34', 'G_SG35', 'G_SG39', 'G_SG45', 'G_SG47'],
        'info': {
            '_name': 'S_LIN',
            'row_num': {
                '_name': 'D_1082',
                '_value': str(item.row_number)
            }
        },
        'description': {
            '_name': 'S_IMD',
            'code': {
                '_name': 'D_7077',
                '_value': item.item_description_code,
            },
            'name': {
                '_name': 'C_C273',
                'desc_1': {
                    '_name': 'D_7008',
                    '_value': item.item_name[:35]  # Only 35 chars...
                }
            }
        },
        'quantity': {
            '_name': 'S_QTY',
            'wrapper':{
                '_name': 'C_C186',
                'qty_type': {
                    '_name': 'D_6063',
                    '_value': item.quantity_type,
                },
                'qty': {
                    '_name': 'D_6060',
                    '_value': str(item.quantity)
                },
                'unit': {
                    '_name': 'D_6411',
                    '_value': item.unit
                }
            }
        },
        'value_before_discount': {
            '_name': 'G_SG27',
            'wrapper':{
                '_name': 'S_MOA',
                'wrapper':{
                    '_name': 'C_C516',
                    'type': {
                        '_name': 'D_5025',
                        '_value': '203'  # Total before discount
                    },
                    'amount': {
                        '_name': 'D_5004',
                        '_value': "%.2f" % (item.price_without_tax * item.quantity)
                    }
                }
            }
        },
        'value_total': {
            '_name': 'G_SG27',
            'wrapper':{
                '_name': 'S_MOA',
                'wrapper':{
                    '_name': 'C_C516',
                    'type': {
                        '_name': 'D_5025',
                        '_value': '38'  # Total before discount
                    },
                    'amount': {
                        '_name': 'D_5004',
                        '_value':  str(item.total_with_tax)
                    }
                }
            }
        },
        'tax_info': {
            '_name': 'G_SG34',
            'taxes': {
                '_name': 'S_TAX',
                'id':{
                    '_name': 'D_5283',
                    '_value': '7'
                },
                'type': {
                    '_name': 'C_C241',
                    'value':{
                        '_name': 'D_5153',
                        '_value': 'VAT'
                    }
                },
                'vat_percentage': {
                    '_name': 'C_C243',
                    'value':{
                        '_name': 'D_5278',
                        '_value': str(item.tax_rate)
                    }
                },
                'tax_type':{
                    '_name': 'D_5305',
                    '_value': item.tax_rate_type
                },
            },
            'tax_amounts_base': {
                '_name': 'S_MOA',
                'wrapper':{
                    '_name': 'C_C516',
                    'type': {
                        '_name': 'D_5025',
                        '_value': '125'
                    },
                    'amount': {
                        '_name': 'D_5004',
                        '_value': str(item.total_without_tax)
                    }
                }
            },
            'tax_amounts_tax': {
                '_name': 'S_MOA',
                'wrapper':{
                    '_name': 'C_C516',
                    'type': {
                        '_name': 'D_5025',
                        '_value': '124'
                    },
                    'amount': {
                        '_name': 'D_5004',
                        '_value': str(item.total_with_tax - item.total_without_tax)
                    }
                }
            }
        }
    }

    if item.ean != None:
        data['info']['ean'] = {
            '_name': 'C_C212',
            'code':{
                '_name': 'D_7140',
                '_value': str(item.ean)
            },
            'type':{
                '_name': 'D_7143',
                '_value': '0160' # type ean
            }
        }

    price_wo_tax = item.price_without_tax
    if item.discount_percentage:
        price_wo_tax = price_wo_tax * Decimal(1-(item.discount_percentage/100))

    data['price'] = {
        '_name': 'G_SG29',
        'wrapper': {
            '_name': 'S_PRI',
            'wrapper':{
                '_name': 'C_C509',
                'type': {
                    '_name': 'D_5125',
                    '_value': 'AAA'
                },
                'value': {
                    '_name': 'D_5118',
                    '_value': "%.2f" %price_wo_tax
                },
                'qty': {
                    '_name': 'D_5284',
                    '_value': '1'
                },
                'unit': {
                    '_name': 'D_6411',
                    '_value': 'C62'
                }
            }
        }
    }

    if item.discount_percentage:
        data['price_wo_discount'] = {
            '_name': 'G_SG29',
            'wrapper': {
                '_name': 'S_PRI',
                'wrapper':{
                    '_name': 'C_C509',
                    'type': {
                        '_name': 'D_5125',
                        '_value': 'AAB'
                    },
                    'value': {
                        '_name': 'D_5118',
                        '_value': str(item.price_without_tax)
                    },
                    'qty': {
                        '_name': 'D_5284',
                        '_value': '1'
                    },
                    'unit': {
                        '_name': 'D_6411',
                        '_value': 'C62'
                    }
                }
            }
        }
        data['discount'] = {
            '_name': 'G_SG39',
            'type':{
                '_name': 'S_ALC',
                'identification': {
                    '_name': 'D_5463',
                    '_value': 'A',  # Discount
                }
            },
            'percentage':{
                '_name': 'G_SG41',
                'wrapper':{
                    '_name': 'S_PCD',
                    'wrapper':{
                        '_name': 'C_C501',
                        'type': {
                            '_name': 'D_5245',
                            '_value': '1',  # Discount
                        },
                        'percentage': {
                            '_name': 'D_5482',
                            '_value': str(item.discount_percentage)
                        }
                    }
                }
            },
            'amount':{
                '_name': 'G_SG42',
                'wrapper':{
                    '_name': 'S_MOA',
                    'wrapper':{
                        '_name': 'C_C516',
                        'type': {
                            '_name': 'D_5025',
                            '_value': '204',  # Discount
                        },
                        'percentage': {
                            '_name': 'D_5004',
                            '_value': str(item.discount_amount)
                        }
                    }
                }
            }
        }

    return data

def construct_tax_summary_data(tax_summary):
    data = {
        '_name': 'G_SG52',
        'summary': {
            '_name': 'S_TAX',
            'type':{
                '_name': 'D_5283',
                '_value': '7'
            },
            'vat_wrapper': {
                '_name': 'C_C241',
                'type':{
                    '_name': 'D_5153',
                    '_value': 'VAT'
                }
            },
            'percentage_wrapper': {
                '_name': 'C_C243',
                'tax_percentage': {
                    '_name': 'D_5278',
                    '_value': str(tax_summary.tax_rate)
                }
            },
            'tax_type': {
                '_name': 'D_5305',
                '_value': tax_summary.tax_type
            }
        },
        'amount_base': {
            '_name': 'S_MOA',
            'wrapper':{
                '_name': 'C_C516',
                'type': {
                    '_name': 'D_5025',
                    '_value': '125'  # Osnova
                },
                'amount': {
                    '_name': 'D_5004',
                    '_value': str(tax_summary.tax_base)
                }
            }
        },
        'amount_tax': {
            '_name': 'S_MOA',
            'wrapper':{
                '_name': 'C_C516',
                'type': {
                    '_name': 'D_5025',
                    '_value': '124'  # Tax amount
                },
                'amount': {
                    '_name': 'D_5004',
                    '_value': str(tax_summary.tax_amount)
                }
            }
        }
    }

    return data

def construct_sums_data(amount, sum_type, ref=None):
    data = {
        '_name': 'G_SG50',
        'amounts': {
            '_name': 'S_MOA',
            'wrapper':{
                '_name': 'C_C516',
                'type': {
                    '_name': 'D_5025',
                    '_value': str(sum_type)
                },
                'amount': {
                    '_name': 'D_5004',
                    '_value': "%.2f" % amount
                }
            }
        }
    }
        

    return data
