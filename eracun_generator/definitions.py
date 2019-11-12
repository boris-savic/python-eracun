import textwrap


def construct_invoice_json(invoice):
    NS = 'http://www.w3.org/2001/XMLSchema-instance'

    data = {
        '_name': 'IzdaniRacunEnostavni',
        '_attrs': [("{%s}noNamespaceSchemaLocation" % NS, 'http://www.gzs.si/e-poslovanje/sheme/eSLOG_1-6_EnostavniRacun.xsd')],
        '_ns': {
            'ds': 'http://www.w3.org/2000/09/xmldsig#',
            'xsd': 'http://uri.etsi.org/01903/v1.1.1#',
            'xsi': NS
        },
        'invoice': {
            '_name': 'Racun',
            '_attrs': [('Id', 'data')],
            'header': construct_header_data(invoice),
            'date_issued': construct_date_data(invoice.date_issued_code, invoice.date_issued),
            'date_of_service': construct_date_data(invoice.date_of_service_code, invoice.date_of_service),
            'currency': construct_currency_data(invoice.currency),
            'location': construct_location_data(invoice.location_code, invoice.location_address),
            'issuer': construct_company_data(invoice.issuer, 'II'),
            'buyer': construct_company_data(invoice.recipient, 'BY'),
            'recipient': construct_company_data(invoice.recipient, 'IV'),
            'payment_terms': construct_payment_terms_data(invoice.date_due_code, invoice.date_due),
            'reference_data': construct_reference_data(invoice.total_with_tax, invoice.payment_reference),

        }  # end invoice
    }

    for i, reference_document in enumerate(invoice.reference_documents):
        data['invoice'][f"reference_document_{i}"] = construct_reference_document_data(reference_document)

    if invoice.global_discount_amount:
        data['invoice']['global_discount'] = construct_global_discount_data(invoice.global_discount_amount, invoice.global_discount_percentage)

    if invoice.intro_text:
        data['invoice']['intro_text'] = construct_custom_text_data('AAI', 'GLAVA_TEKST', invoice.intro_text)

    for i, item in enumerate(invoice.document_items):
        data['invoice'][f"item_{i}"] = construct_item_data(item)

    for i, ts in enumerate(invoice.tax_summaries):
        data['invoice'][f"tax_summary_{i}"] = construct_tax_summary_data(ts)

    # add final sums to invoice
    # Total without discount
    data['invoice']['sums_without_discounts'] = construct_sums_data(amount=invoice.total_without_discount, sum_type='79')
    # Discounts amount
    data['invoice']['sums_discounts'] = construct_sums_data(amount=invoice.total_without_discount - invoice.total_without_tax, sum_type='53')
    # Tax base sums
    data['invoice']['sums_tax_base_amount'] = construct_sums_data(amount=invoice.total_without_tax, sum_type='125')
    # Taxes amount
    data['invoice']['sums_taxes'] = construct_sums_data(amount=invoice.total_with_tax - invoice.total_without_tax, sum_type='176')
    # Total amount - with taxes
    data['invoice']['sums_total_amount'] = construct_sums_data(amount=invoice.total_with_tax, sum_type='86')

    if invoice.outro_text:
        data['invoice']['outro_text'] = construct_custom_text_data('AAI', 'DODATNI_TEKST', invoice.outro_text)

    return data


def construct_header_data(invoice):
    header = {
        '_name': 'GlavaRacuna',
        'invoice_type': {
            '_name': 'VrstaRacuna',
            '_value': invoice.invoice_type,
        },
        'invoice_number': {
            '_name': 'StevilkaRacuna',
            '_value': invoice.invoice_number,
        },
        'invoice_function': {
            '_name': 'FunkcijaRacuna',
            '_value': invoice.invoice_function,
        },
        'payment_type': {
            '_name': 'NacinPlacila',
            '_value': invoice.payment_type,
        },
        'payment_purpose': {
            '_name': 'KodaNamena',
            '_value': invoice.payment_purpose
        }
    }

    return header


def construct_date_data(date_code, date):
    date = {
        '_name': 'DatumiRacuna',
        'date_type': {
            '_name': 'VrstaDatuma',
            '_value': date_code
        },
        'date': {
            '_name': 'DatumRacuna',
            '_value': date.isoformat()
        }
    }

    return date


def construct_currency_data(currency):
    currency = {
        '_name': 'Valuta',
        'currency_type': {
            '_name': 'VrstaValuteRacuna',
            '_value': '2',
        },
        'currency_code': {
            '_name': 'KodaValute',
            '_value': currency,
        },
    }

    return currency


def construct_location_data(location_code, location_address):
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
        '_name': 'PodatkiPodjetja',
        'info': {
            '_name': 'NazivNaslovPodjetja',
            'type': {
                '_name': 'VrstaPartnerja',
                '_value': business_type
            },
            'name': {
                '_name': 'NazivPartnerja',
            },
            'address': {
                '_name': 'Ulica',
            },
            'city': {
                '_name': 'Kraj',
                '_value': business.city
            },
            'country': {
                '_name': 'NazivDrzave',
                '_value': business.country
            },
            'zip_code': {
                '_name': 'PostnaStevilka',
                '_value': str(business.zip_code)
            },
            'country_code': {
                '_name': 'KodaDrzave',
                '_value': business.country_iso_code
            },
        }
    }

    # Add business name
    business_name_split = textwrap.wrap(business.name, 35, break_long_words=True)

    for i, bn_part in enumerate(business_name_split):
        i = i + 1  # Start from 1
        data['info']['name'][f"part_{i}"] = {
            '_name': f"NazivPartnerja{i}",
            '_value': bn_part
        }

        if i == 4:
            break  # Stop at max length

    # Add business name
    addr_split = textwrap.wrap(business.address, 35, break_long_words=True)

    for i, addr_part in enumerate(addr_split):
        i = i + 1  # Start from 1
        data['info']['address'][f"part_{i}"] = {
            '_name': f"Ulica{i}",
            '_value': addr_part
        }

        if i == 4:
            break  # Stop at max length

    if business.iban:
        data['financial_info'] = {
            '_name': 'FinancniPodatkiPodjetja',
            'bank_account_info': {
                '_name': 'BancniRacun',
                'iban': {
                    '_name': 'StevilkaBancnegaRacuna',
                    '_value': business.iban
                },
                'bic': {
                    '_name': 'BIC',
                    '_value': business.bic
                }
            }
        }

    if business.vat_id:
        data['vat_id'] = {
            '_name': 'ReferencniPodatkiPodjetja',
            'type': {
                '_name': 'VrstaPodatkaPodjetja',
                '_value': 'VA'
            },
            'vat': {
                '_name': 'PodatekPodjetja',
                '_value': str(business.vat_id)
            }
        }

    if business.registration_number:
        data['registration_number'] = {
            '_name': 'ReferencniPodatkiPodjetja',
            'type': {
                '_name': 'VrstaPodatkaPodjetja',
                '_value': 'GN'
            },
            'vat': {
                '_name': 'PodatekPodjetja',
                '_value': str(business.registration_number)
            }
        }

    return data


def construct_payment_terms_data(date_due_code, date_due):
    payment_terms = {
        '_name': 'PlacilniPogoji',
        'term_data': {
            '_name': 'PodatkiORokih',
            'term_code': {
                '_name': 'VrstaPogoja',
                '_value': '3',
            }
        },
        'term_due': {
            '_name': 'PlacilniRoki',
            'term_due_type': {
                '_name': 'VrstaDatumaPlacilnegaRoka',
                '_value': date_due_code,
            },
            'term_due_date': {
                '_name': 'Datum',
                '_value': date_due.isoformat(),
            },
        }
    }

    return payment_terms


def construct_reference_data(total_with_tax, payment_reference):
    reference = {
        '_name': 'PovzetekZneskovRacuna',
        'invoice_amounts': {
            '_name': 'ZneskiRacuna',
            'type': {
                '_name': 'VrstaZneska',
                '_value': '9'  # Amount to be paid
            },
            'amount': {
                '_name': 'ZnesekRacuna',
                '_value': str(total_with_tax)
            }
        },
        'reference': {
            '_name': 'SklicZaPlacilo',
            'ref_type': {
                '_name': 'SklicPlacila',
                '_value': 'PQ'
            },
            'ref_number': {
                '_name': 'StevilkaSklica',
                '_value': payment_reference
            }
        }
    }

    return reference


def construct_reference_document_data(reference_document):
    reference_doc_data = {
        '_name': 'ReferencniDokumenti',
        '_attrs': [('VrstaDokumenta', reference_document.type_code)],
        'document_number': {
            '_name': "StevilkaDokumenta",
            '_value': reference_document.document_number
        }
    }

    return reference_doc_data


def construct_global_discount_data(discount_amount, discount_percentage):
    discount_data = {
        '_name': 'GlobalniPopusti',
        'description': {
            '_name': 'OpisPopusta',
            '_value': 'SKUPNI POPUST',
        },
        'type': {
            '_name': 'TipPopusta',
            '_value': 'PP',
        },
        'percentage': {
            '_name': 'OdstotekPopusta',
            '_value': str(discount_percentage)
        },
        'amount': {
            '_name': 'ZnesekPopusta',
            '_value': str(discount_amount)
        },
    }

    return discount_data


def construct_custom_text_data(text_format, text_type, text):
    """
    Text must be split into 70 chars long strings.
    :param text_format: AAI or other predefined formats
    :param text_type:
    :param text:
    :return:
    """
    text_split = textwrap.wrap(text, 70, break_long_words=True)

    custom_text = {
        '_name': 'PoljubnoBesedilo',
        'format': {
            '_name': 'VrstaBesedila',
            '_value': text_format,
        },
        'content': {
            '_name': 'Besedilo',
            'text_1': {
                '_name': 'Tekst1',
                '_value': text_type,
            },
        }
    }

    for i, txt in enumerate(text_split):
        # Since text_1 is used for text_type we must enumerate from 2 onwards
        i = i + 2

        custom_text['content'][f"text_{i}"] = {
            '_name': f"Tekst{i}",
            '_value': txt
        }

        # Stop the loop if index is 5 - we can't place any more than  that in XML.
        if i == 5:
            break

    return custom_text


def construct_item_data(item):
    data = {
        '_name': 'PostavkeRacuna',
        'info': {
            '_name': 'Postavka',
            'row_num': {
                '_name': 'StevilkaVrstice',
                '_value': str(item.row_number)
            }
        },
        'description': {
            '_name': 'OpisiArtiklov',
            'code': {
                '_name': 'KodaOpisaArtikla',
                '_value': 'F',
            },
            'name': {
                '_name': 'OpisArtikla',
                'desc_1': {
                    '_name': 'OpisArtikla1',
                    '_value': item.item_name[:35]  # Only 35 chars...
                }
            }
        },
        'quantity': {
            '_name': 'KolicinaArtikla',
            'qty_type': {
                '_name': 'VrstaKolicine',
                '_value': item.quantity_type,
            },
            'qty': {
                '_name': 'Kolicina',
                '_value': str(item.quantity)
            },
            'unit': {
                '_name': 'EnotaMere',
                '_value': item.unit
            }
        },
        'value_before_discount': {
            '_name': 'ZneskiPostavke',
            'type': {
                '_name': 'VrstaZneskaPostavke',
                '_value': '203'  # Total before discount
            },
            'amount': {
                '_name': 'ZnesekPostavke',
                '_value': "%.2f" % (item.price_without_tax * item.quantity)
            }
        },
        'value_total': {
            '_name': 'ZneskiPostavke',
            'type': {
                '_name': 'VrstaZneskaPostavke',
                '_value': '38'  # Total with discount
            },
            'amount': {
                '_name': 'ZnesekPostavke',
                '_value': str(item.total_with_tax)
            }
        },
        'price': {
            '_name': 'CenaPostavke',
            'value': {
                '_name': 'Cena',
                '_value': str(item.price_without_tax)
            }
        },
        'tax_info': {
            '_name': 'DavkiPostavke',
            'taxes': {
                '_name': 'DavkiNaPostavki',
                'type': {
                    '_name': 'VrstaDavkaPostavke',
                    '_value': 'VAT'
                },
                'vat_percentage': {
                    '_name': 'OdstotekDavkaPostavke',
                    '_value': str(item.tax_rate)
                }
            },
            'tax_amounts_base': {
                '_name': 'ZneskiDavkovPostavke',
                'type': {
                    '_name': 'VrstaZneskaDavkaPostavke',
                    '_value': '125'
                },
                'amount': {
                    '_name': 'Znesek',
                    '_value': str(item.total_without_tax)
                }
            },
            'tax_amounts_tax': {
                '_name': 'ZneskiDavkovPostavke',
                'type': {
                    '_name': 'VrstaZneskaDavkaPostavke',
                    '_value': '124'
                },
                'amount': {
                    '_name': 'Znesek',
                    '_value': str(item.total_with_tax - item.total_without_tax)
                }
            }
        }
    }

    if item.discount_percentage:
        data['discount'] = {
            '_name': 'OdstotkiPostavk',
            'identification': {
                '_name': 'Identifikator',
                '_value': 'A',  # Discount
            },
            'type': {
                '_name': 'VrstaOdstotkaPostavke',
                '_value': '12',  # Discount
            },
            'percentage': {
                '_name': 'OdstotekPostavke',
                '_value': str(item.discount_percentage)
            },
            'type_amount': {
                '_name': 'VrstaZneskaOdstotka',
                '_value': '204'
            },
            'amount': {
                '_name': 'ZnesekOdstotka',
                '_value': str(item.discount_amount)
            }

        }

    return data


def construct_tax_summary_data(tax_summary):
    data = {
        '_name': 'PovzetekDavkovRacuna',
        'summary': {
            '_name': 'DavkiRacuna',
            'tax_type': {
                '_name': 'VrstaDavka',
                '_value': 'VAT'
            },
            'tax_percentage': {
                '_name': 'OdstotekDavka',
                '_value': str(tax_summary.tax_rate)
            },
        },
        'amount_base': {
            '_name': 'ZneskiDavkov',
            'type': {
                '_name': 'VrstaZneskaDavka',
                '_value': '125'  # Osnova
            },
            'amount': {
                '_name': 'ZnesekDavka',
                '_value': str(tax_summary.tax_base)
            }
        },
        'amount_tax': {
            '_name': 'ZneskiDavkov',
            'type': {
                '_name': 'VrstaZneskaDavka',
                '_value': '124'  # Tax amount
            },
            'amount': {
                '_name': 'ZnesekDavka',
                '_value': str(tax_summary.tax_amount)
            }
        }
    }

    return data


def construct_sums_data(amount, sum_type, ref=None):
    data = {
        '_name': 'PovzetekZneskovRacuna',
        'amounts': {
            '_name': 'ZneskiRacuna',
            'type': {
                '_name': 'VrstaZneska',
                '_value': str(sum_type)
            },
            'amount': {
                '_name': 'ZnesekRacuna',
                '_value': "%.2f" % amount
            }
        },
        'ref': {
            '_name': 'SklicZaPlacilo',
            'ref_type': {
                '_name': 'SklicPlacila',
                '_value': 'PQ'
            }
        }
    }

    if ref is not None:
        data['ref']['ref_number'] = {
            '_name': 'StevilkaSklica',
            '_value': ref
        }

    return data
