from datetime import datetime, timezone


def convert_invoice_to_envelope(invoice, attachments, sender_bic, recipient_bic):
    NS = 'http://www.w3.org/2001/XMLSchema-instance'

    envelope = {
        '_name': 'envelope',
        '_ns': {
            'xsi': NS,
            'xsd': 'http://www.w3.org/2001/XMLSchema',
        },
        'sender': _construct_sender_receiver_data(invoice.issuer, 'sender', sender_bic),
        'receiver': _construct_sender_receiver_data(invoice.recipient, 'receiver', recipient_bic),
        'document_data': {
            '_name': 'doc_data',
            'type': {
                '_name': 'doc_type',
                '_value': '0002',
            },
            'version': {
                '_name': 'doc_type_ver',
                '_value': '01',
            },
            'document_id': {
                '_name': 'doc_id',
                '_value': str(invoice.invoice_number),
            },
            'external_document_id': {
                '_name': 'external_doc_id',
                '_value': str(invoice.invoice_number),
            },
            'timestamp': {
                '_name': 'timestamp',
                '_value': invoice.date_issued.isoformat()
            },
        },
        'payment_data': {
            '_name': 'payment_data',
            'payment_method': {
                '_name': 'payment_method',
                '_value': invoice.payment_type
            },
            'creditor': _construct_creditor_debtor_data(invoice.issuer, 'creditor'),
            'debtor': _construct_creditor_debtor_data(invoice.recipient, 'debtor'),
            'execution_time': {
                '_name': 'requested_execution_date',
                '_value': invoice.date_issued.strftime('%Y-%m-%d')
            },
            'amount': {
                '_name': 'amount',
                '_value': str(invoice.total_with_tax)
            },
            'currency': {
                '_name': 'currency',
                '_value': invoice.currency
            },
            'remittance_information': {
                '_name': 'remittance_information',
                'creditor_reference': {
                    '_name': 'creditor_structured_reference',
                    '_value': invoice.payment_reference
                },
                'additional_info': {
                    '_name': 'additional_remittance_information',
                    '_value': invoice.additional_remittance_information
                }
            },
            'purpose': {
                '_name': 'purpose',
                '_value': invoice.payment_purpose
            }
        },
        'attachments': {
            '_name': 'attachments',
            'hash': {
                '_name': 'hash',
                '_value': '0000000000000000000000000000000000000000',
            },
            'size': {
                '_name': 'size',
                '_value': '0'
            },
            'count': {
                '_name': 'count',
                '_value': str(len(attachments))
            }
        }
    }

    for i, attachment in enumerate(attachments):
        envelope['attachments'][f'attachment_{i}'] = {
            '_name': 'attachment',
            'filename': {
                '_name': 'filename',
                '_value': attachment[0]
            },
            'size': {
                '_name': 'size',
                '_value': str(attachment[2])
            },
            'type': {
                '_name': 'type',
                '_value': attachment[1]
            }
        }

    return envelope


def _construct_sender_receiver_data(entity, entity_type='sender', bic=None):
    data = {
        '_name': entity_type,
        'name': {
            '_name': 'name',
            '_value': entity.name[:70]  # max length
        },
        'country': {
            '_name': 'country',
            '_value': entity.country_iso_code
        },
        'address': {
            '_name': 'address',
            '_value': entity.address[:70]
        },
        'zip_code': {
            '_name': 'address',
            '_value': str(entity.zip_code)
        },
        'vat_id': {
            '_name': f'{entity_type}_identifier',
            '_value': str(entity.vat_id)
        },
        'e_address': {
            '_name': f'{entity_type}_eddress',
            'bic': {
                '_name': f'{entity_type}_agent',
                '_value': bic if bic else entity.bic
            },
            'iban': {
                '_name': f'{entity_type}_mailbox',
                '_value': entity.iban
            }
        }
    }

    return data


def _construct_creditor_debtor_data(entity,  entity_type='creditor'):
    data = {
        '_name': entity_type,
        'name': {
            '_name': 'name',
            '_value': entity.name[:70]  # max length
        },
        'country': {
            '_name': 'country',
            '_value': entity.country_iso_code
        },
        'address': {
            '_name': 'address',
            '_value': entity.address[:70]
        },
        'zip_code': {
            '_name': 'address',
            '_value': str(entity.zip_code)
        },
        'bic': {
            '_name': f'{entity_type}_agent',
            '_value': entity.bic
        },
        'iban': {
            '_name': f'{entity_type}_account',
            '_value': entity.iban
        }
    }

    return data
